"""
Code Server Manager: Handle per-user VS Code container lifecycle

Uses Docker CLI via subprocess instead of Python SDK to avoid Unix socket issues.
"""
import logging
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Union
import os
from uuid import UUID

logger = logging.getLogger(__name__)

class CodeServerManager:
    """
    Manages per-user code-server Docker containers
    
    Each user gets their own isolated code-server instance with:
    - Private workspace directory
    - Routed via Traefik (no unique ports needed)
    - Automatic startup/shutdown
    """
    
    def __init__(self):
        """Initialize manager using Docker CLI instead of Python SDK"""
        try:
            # Test Docker CLI is available
            result = subprocess.run(
                ['docker', 'version', '--format', '{{.Server.Version}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Docker CLI available, server version: {version}")
                self.available = True
            else:
                logger.error(f"Docker CLI test failed: {result.stderr}")
                self.available = False
            
            self.workspace_base = Path(os.getenv("WORKSPACE_BASE", "/app/workspace"))
            logger.info("CodeServerManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CodeServerManager: {e}")
            self.available = False
    
    def get_container_name(self, user_id: Union[str, UUID]) -> str:
        """Generate unique container name for user"""
        return f"code-server-user-{str(user_id)}"
    
    def get_user_port(self, user_id: Union[str, UUID]) -> int:
        """Return internal port (all containers use 8080, Traefik handles routing)"""
        return 8080  # All containers use same internal port, Traefik routes by path
    
    def get_user_workspace(self, user_id: Union[str, UUID]) -> Path:
        """Get user's workspace directory"""
        workspace = self.workspace_base / f"user_{user_id}"
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
    
    def is_container_running(self, user_id: Union[str, UUID]) -> bool:
        """Check if user's code-server container is running"""
        if not self.available:
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format', '{{.State.Running}}', self.get_container_name(user_id)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and result.stdout.strip() == 'true'
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return False
    
    def start_user_container(self, user_id: Union[str, UUID]) -> Dict:
        """
        Start a code-server container for the user using Docker CLI
        Returns container info including port
        """
        if not self.available:
            raise Exception("Docker not available")
        
        container_name = self.get_container_name(user_id)
        port = self.get_user_port(user_id)
        workspace = self.get_user_workspace(user_id)
        
        # Check if container already exists and is running
        if self.is_container_running(user_id):
            logger.info(f"Container {container_name} already running")
            return {
                "status": "running",
                "port": port,
                "container_id": container_name
            }
        
        # Check if container exists but is stopped
        check_result = subprocess.run(
            ['docker', 'inspect', '--format', '{{.State.Status}}', container_name],
            capture_output=True,
            text=True
        )
        
        if check_result.returncode == 0:
            # Container exists, just start it
            subprocess.run(['docker', 'start', container_name], check=True)
            logger.info(f"Restarted container {container_name}")
            return {
                "status": "started",
                "port": port,
                "container_id": container_name
            }
        
        # Create new container using Docker CLI
        logger.info(f"Creating new container {container_name}")
        
        cmd = [
            'docker', 'run',
            '--name', container_name,
            '--detach',
            '--network', 'gunpowder-splash_beacon-network',
            '--volume', f'{workspace.absolute()}:/home/coder/workspace:rw',
            '--user', '1000:1000',
            '--restart', 'unless-stopped',
            # Traefik labels
            '--label', 'traefik.enable=true',
            '--label', f'traefik.http.routers.code-user-{user_id}.rule=Host(`shlinx.com`) && PathPrefix(`/code/user/{user_id}`)',
            '--label', f'traefik.http.routers.code-user-{user_id}.entrypoints=websecure',
            '--label', f'traefik.http.routers.code-user-{user_id}.tls.certresolver=letsencrypt',
            '--label', f'traefik.http.services.code-user-{user_id}.loadbalancer.server.port=8080',
            '--label', f'traefik.http.middlewares.code-user-{user_id}-stripprefix.stripprefix.prefixes=/code/user/{user_id}',
            '--label', f'traefik.http.routers.code-user-{user_id}.middlewares=code-user-{user_id}-stripprefix',
            '--label', f'gunpowder.user_id={user_id}',
            'codercom/code-server:latest',
            '--bind-addr', '0.0.0.0:8080',
            '--auth', 'none',
            '/home/coder/workspace'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            container_id = result.stdout.strip()
            logger.info(f"Created container {container_name} (ID: {container_id[:12]})")
            
            return {
                "status": "created",
                "port": port,
                "container_id": container_id,
                "workspace": str(workspace)
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create container: {e.stderr}")
            raise Exception(f"Docker run failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            raise
    
    def stop_user_container(self, user_id: Union[str, UUID]) -> bool:
        """Stop user's code-server container using Docker CLI"""
        if not self.available:
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'stop', self.get_container_name(user_id)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Stopped container for user {user_id}")
                return True
            else:
                logger.warning(f"Container stop returned {result.returncode}: {result.stderr}")
                return result.returncode == 1  # Container may not exist, that's ok
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False
    
    def remove_user_container(self, user_id: Union[str, UUID]) -> bool:
        """Remove user's code-server container using Docker CLI"""
        if not self.available:
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'rm', '-f', self.get_container_name(user_id)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Removed container for user {user_id}")
                return True
            else:
                logger.warning(f"Container remove returned {result.returncode}: {result.stderr}")
                return result.returncode == 1  # Container may not exist, that's ok
        except Exception as e:
            logger.error(f"Error removing container: {e}")
            return False
    
    def get_user_container_url(self, user_id: Union[str, UUID], base_url: str) -> Optional[str]:
        """Get the URL to access user's code-server"""
        if not self.is_container_running(user_id):
            return None
        
        port = self.get_user_port(user_id)
        # In production, this would go through nginx proxy
        # For now, return direct port access
        return f"{base_url}:{port}"


# Singleton instance
code_server_manager = CodeServerManager()

