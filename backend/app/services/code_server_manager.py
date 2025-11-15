"""
Code Server Manager: Handle per-user VS Code container lifecycle
"""
import docker
import logging
from pathlib import Path
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)

class CodeServerManager:
    """
    Manages per-user code-server Docker containers
    
    Each user gets their own isolated code-server instance with:
    - Private workspace directory
    - Unique port assignment
    - Automatic startup/shutdown
    """
    
    def __init__(self):
        try:
            # Connect to Docker socket (note: three slashes after unix:)
            self.client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
            self.base_port = 9000  # Starting port for user instances
            self.workspace_base = Path(os.getenv("WORKSPACE_BASE", "/app/workspace"))
            logger.info("CodeServerManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
    
    def get_container_name(self, user_id: int) -> str:
        """Generate unique container name for user"""
        return f"code-server-user-{user_id}"
    
    def get_user_port(self, user_id: int) -> int:
        """Assign unique port to user (simple allocation for now)"""
        return self.base_port + user_id
    
    def get_user_workspace(self, user_id: int) -> Path:
        """Get user's workspace directory"""
        workspace = self.workspace_base / f"user_{user_id}"
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
    
    def is_container_running(self, user_id: int) -> bool:
        """Check if user's code-server container is running"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(self.get_container_name(user_id))
            return container.status == 'running'
        except docker.errors.NotFound:
            return False
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return False
    
    def start_user_container(self, user_id: int) -> Dict:
        """
        Start a code-server container for the user
        Returns container info including port
        """
        if not self.client:
            raise Exception("Docker client not available")
        
        container_name = self.get_container_name(user_id)
        port = self.get_user_port(user_id)
        workspace = self.get_user_workspace(user_id)
        
        # Check if container already exists
        try:
            container = self.client.containers.get(container_name)
            if container.status == 'running':
                logger.info(f"Container {container_name} already running")
                return {
                    "status": "running",
                    "port": port,
                    "container_id": container.id
                }
            else:
                # Restart existing container
                container.start()
                logger.info(f"Restarted container {container_name}")
                return {
                    "status": "started",
                    "port": port,
                    "container_id": container.id
                }
        except docker.errors.NotFound:
            pass
        
        # Create new container with Traefik labels for auto-discovery
        try:
            labels = {
                "traefik.enable": "true",
                f"traefik.http.routers.code-user-{user_id}.rule": f"Host(`shlinx.com`) && PathPrefix(`/code/user/{user_id}`)",
                f"traefik.http.routers.code-user-{user_id}.entrypoints": "websecure",
                f"traefik.http.routers.code-user-{user_id}.tls.certresolver": "letsencrypt",
                f"traefik.http.services.code-user-{user_id}.loadbalancer.server.port": "8080",
                # Strip the /code/user/{id} prefix before passing to code-server
                f"traefik.http.middlewares.code-user-{user_id}-stripprefix.stripprefix.prefixes": f"/code/user/{user_id}",
                f"traefik.http.routers.code-user-{user_id}.middlewares": f"code-user-{user_id}-stripprefix",
                "gunpowder.user_id": str(user_id),
            }
            
            container = self.client.containers.run(
                image="codercom/code-server:latest",
                name=container_name,
                detach=True,
                network="gunpowder-splash_beacon-network",
                volumes={
                    str(workspace.absolute()): {
                        'bind': '/home/coder/workspace',
                        'mode': 'rw'
                    }
                },
                environment={
                    'PASSWORD': '',  # No password - auth handled by main app
                },
                command=['--bind-addr', '0.0.0.0:8080', '--auth', 'none', '/home/coder/workspace'],
                user='1000:1000',
                labels=labels,
                restart_policy={"Name": "unless-stopped"}
            )
            
            logger.info(f"Created container {container_name} on port {port}")
            
            return {
                "status": "created",
                "port": port,
                "container_id": container.id,
                "workspace": str(workspace)
            }
            
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            raise
    
    def stop_user_container(self, user_id: int) -> bool:
        """Stop user's code-server container"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(self.get_container_name(user_id))
            container.stop()
            logger.info(f"Stopped container for user {user_id}")
            return True
        except docker.errors.NotFound:
            return True  # Already stopped
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False
    
    def remove_user_container(self, user_id: int) -> bool:
        """Remove user's code-server container"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(self.get_container_name(user_id))
            container.remove(force=True)
            logger.info(f"Removed container for user {user_id}")
            return True
        except docker.errors.NotFound:
            return True  # Already removed
        except Exception as e:
            logger.error(f"Error removing container: {e}")
            return False
    
    def get_user_container_url(self, user_id: int, base_url: str) -> Optional[str]:
        """Get the URL to access user's code-server"""
        if not self.is_container_running(user_id):
            return None
        
        port = self.get_user_port(user_id)
        # In production, this would go through nginx proxy
        # For now, return direct port access
        return f"{base_url}:{port}"


# Singleton instance
code_server_manager = CodeServerManager()

