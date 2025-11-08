"""
AI Provider integrations for Beacon Studio
Supports Gemini, LM Studio, and Ollama
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import httpx
from sqlalchemy.orm import Session
from .config import get_settings
from .models import AIUsage
import uuid

settings = get_settings()


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # 'user', 'assistant', 'system'
    content: str


class CompletionRequest(BaseModel):
    """Completion request model"""
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
    stop_sequences: Optional[List[str]] = None


class CompletionResponse(BaseModel):
    """Completion response model"""
    text: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    finish_reason: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[ChatMessage]
    max_tokens: int = 1000
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """Chat response model"""
    message: ChatMessage
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    finish_reason: Optional[str] = None


class AIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    async def generate_completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate text completion"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """Chat with AI"""
        pass
    
    def track_usage(
        self,
        db: Session,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        model_name: str,
        input_tokens: Optional[int],
        output_tokens: Optional[int],
        cost_cents: Optional[int] = None
    ) -> None:
        """
        Track AI usage in database
        
        Note: This method does NOT commit the transaction.
        The caller is responsible for committing after successful response delivery.
        """
        usage = AIUsage(
            user_id=user_id,
            workspace_id=workspace_id,
            provider=self.__class__.__name__.replace("Provider", "").lower(),
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_cents=cost_cents
        )
        db.add(usage)
        # Do NOT commit here - let the caller commit after successful response


class GeminiProvider(AIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key not configured")
        
        self.model_name = "gemini-1.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    async def generate_completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate completion using Gemini"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model_name}:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": [{
                        "parts": [{"text": request.prompt}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": request.max_tokens,
                        "temperature": request.temperature,
                        "stopSequences": request.stop_sequences or []
                    }
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response text
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Extract token counts
            usage = data.get("usageMetadata", {})
            input_tokens = usage.get("promptTokenCount")
            output_tokens = usage.get("candidatesTokenCount")
            
            return CompletionResponse(
                text=text,
                model=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=data["candidates"][0].get("finishReason")
            )
    
    async def chat(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """Chat with Gemini"""
        # Convert messages to Gemini format
        contents = []
        for msg in request.messages:
            role = "user" if msg.role == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model_name}:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "maxOutputTokens": request.max_tokens,
                        "temperature": request.temperature
                    }
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response
            reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Extract token counts
            usage = data.get("usageMetadata", {})
            input_tokens = usage.get("promptTokenCount")
            output_tokens = usage.get("candidatesTokenCount")
            
            return ChatResponse(
                message=ChatMessage(role="assistant", content=reply_text),
                model=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=data["candidates"][0].get("finishReason")
            )


class LMStudioProvider(AIProvider):
    """LM Studio local AI provider"""
    
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or settings.lm_studio_endpoint
        if not self.endpoint:
            raise ValueError("LM Studio endpoint not configured")
        
        # LM Studio uses OpenAI-compatible API
        self.model_name = "local-model"
    
    async def generate_completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate completion using LM Studio"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/completions",
                json={
                    "prompt": request.prompt,
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "stop": request.stop_sequences
                },
                timeout=120.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            return CompletionResponse(
                text=data["choices"][0]["text"],
                model=data.get("model", self.model_name),
                input_tokens=data.get("usage", {}).get("prompt_tokens"),
                output_tokens=data.get("usage", {}).get("completion_tokens"),
                finish_reason=data["choices"][0].get("finish_reason")
            )
    
    async def chat(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """Chat with LM Studio"""
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/chat/completions",
                json={
                    "messages": messages,
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                },
                timeout=120.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            reply = data["choices"][0]["message"]
            
            return ChatResponse(
                message=ChatMessage(role=reply["role"], content=reply["content"]),
                model=data.get("model", self.model_name),
                input_tokens=data.get("usage", {}).get("prompt_tokens"),
                output_tokens=data.get("usage", {}).get("completion_tokens"),
                finish_reason=data["choices"][0].get("finish_reason")
            )


class OllamaProvider(AIProvider):
    """Ollama local AI provider"""
    
    def __init__(self, endpoint: Optional[str] = None, model: str = "llama2"):
        self.endpoint = endpoint or settings.ollama_endpoint
        if not self.endpoint:
            raise ValueError("Ollama endpoint not configured")
        
        self.model_name = model
    
    async def generate_completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate completion using Ollama"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": request.prompt,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    },
                    "stream": False
                },
                timeout=120.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            return CompletionResponse(
                text=data["response"],
                model=data.get("model", self.model_name),
                input_tokens=data.get("prompt_eval_count"),
                output_tokens=data.get("eval_count"),
                finish_reason="stop" if data.get("done") else None
            )
    
    async def chat(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """Chat with Ollama"""
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    },
                    "stream": False
                },
                timeout=120.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            message = data["message"]
            
            return ChatResponse(
                message=ChatMessage(role=message["role"], content=message["content"]),
                model=data.get("model", self.model_name),
                input_tokens=data.get("prompt_eval_count"),
                output_tokens=data.get("eval_count"),
                finish_reason="stop" if data.get("done") else None
            )


# Provider factory
def get_ai_provider(provider_name: str, **kwargs) -> AIProvider:
    """
    Get AI provider instance
    
    Args:
        provider_name: 'gemini', 'lm_studio', or 'ollama'
        **kwargs: Provider-specific configuration
        
    Returns:
        AIProvider instance
    """
    providers = {
        "gemini": GeminiProvider,
        "lm_studio": LMStudioProvider,
        "ollama": OllamaProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {provider_name}")
    
    return provider_class(**kwargs)


# Default provider (Gemini)
def get_default_provider() -> AIProvider:
    """Get default AI provider (Gemini)"""
    return GeminiProvider()

