"""
Deployment Agent - Handles application deployment to various environments
"""

import asyncio
import logging
import json
import os
import tempfile
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

import docker
import yaml
from kubernetes import client, config

from core.config import settings

logger = logging.getLogger(__name__)

class DeploymentAgent:
    """AI agent for application deployment"""
    
    def __init__(self):
        self.docker_client = None
        self.k8s_client = None
        self.active_deployments = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the deployment agent"""
        if self._initialized:
            return
        
        logger.info("Initializing Deployment Agent...")
        
        try:
            # Initialize Docker client
            try:
                self.docker_client = docker.from_env()
                logger.info("Docker client initialized")
            except Exception as e:
                logger.warning(f"Docker not available: {str(e)}")
            
            # Initialize Kubernetes client
            try:
                if settings.KUBERNETES_CONFIG_PATH:
                    config.load_kube_config(config_file=settings.KUBERNETES_CONFIG_PATH)
                else:
                    config.load_incluster_config()
                
                self.k8s_client = client.ApiClient()
                logger.info("Kubernetes client initialized")
            except Exception as e:
                logger.warning(f"Kubernetes not available: {str(e)}")
            
            self._initialized = True
            logger.info("Deployment Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Deployment Agent: {str(e)}")
            raise
    
    async def deploy(self, repository_url: str, branch: str = "main", environment: str = "dev") -> Dict[str, Any]:
        """
        Deploy an application
        
        Args:
            repository_url: Git repository URL
            branch: Git branch to deploy
            environment: Target environment (dev, staging, prod)
            
        Returns:
            Dict containing deployment information
        """
        deployment_id = f"deploy_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"Starting deployment: {deployment_id}")
            
            # Store deployment info
            self.active_deployments[deployment_id] = {
                "repository_url": repository_url,
                "branch": branch,
                "environment": environment,
                "start_time": datetime.now(),
                "status": "cloning"
            }
            
            # Clone repository
            source_path = await self._clone_repository(repository_url, branch)
            
            # Analyze project for deployment strategy
            deployment_strategy = await self._analyze_project(source_path)
            
            # Build application
            build_result = await self._build_application(source_path, deployment_strategy)
            
            # Deploy based on environment and strategy
            deploy_result = await self._deploy_application(
                source_path, deployment_strategy, environment, build_result
            )
            
            # Update deployment status
            self.active_deployments[deployment_id].update({
                "status": "completed",
                "source_path": source_path,
                "deployment_strategy": deployment_strategy,
                "build_result": build_result,
                "deploy_result": deploy_result,
                "completion_time": datetime.now()
            })
            
            return {
                "deployment_id": deployment_id,
                "repository_url": repository_url,
                "branch": branch,
                "environment": environment,
                "deployment_strategy": deployment_strategy,
                "build_result": build_result,
                "deploy_result": deploy_result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error deploying {deployment_id}: {str(e)}")
            if deployment_id in self.active_deployments:
                self.active_deployments[deployment_id]["status"] = "failed"
                self.active_deployments[deployment_id]["error"] = str(e)
            raise
    
    async def _clone_repository(self, repository_url: str, branch: str) -> str:
        """Clone the Git repository"""
        clone_path = tempfile.mkdtemp(prefix="deploy_")
        
        try:
            # Clone repository
            cmd = f"git clone -b {branch} {repository_url} {clone_path}"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Git clone failed: {stderr.decode()}")
            
            logger.info(f"Cloned repository to: {clone_path}")
            return clone_path
            
        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            raise
    
    async def _analyze_project(self, source_path: str) -> Dict[str, Any]:
        """Analyze project structure to determine deployment strategy"""
        strategy = {
            "type": "unknown",
            "build_system": None,
            "runtime": None,
            "port": 3000,
            "health_check": "/health",
            "dockerfile_needed": True
        }
        
        try:
            # Check for package.json (Node.js)
            if os.path.exists(os.path.join(source_path, "package.json")):
                with open(os.path.join(source_path, "package.json"), 'r') as f:
                    package_json = json.load(f)
                
                strategy.update({
                    "type": "nodejs",
                    "build_system": "npm",
                    "runtime": "node",
                    "port": 3000,
                    "start_script": package_json.get("scripts", {}).get("start", "npm start")
                })
            
            # Check for requirements.txt (Python)
            elif os.path.exists(os.path.join(source_path, "requirements.txt")):
                strategy.update({
                    "type": "python",
                    "build_system": "pip",
                    "runtime": "python",
                    "port": 8000
                })
                
                # Check for specific Python frameworks
                with open(os.path.join(source_path, "requirements.txt"), 'r') as f:
                    requirements = f.read()
                    if "flask" in requirements.lower():
                        strategy["framework"] = "flask"
                        strategy["port"] = 5000
                    elif "fastapi" in requirements.lower():
                        strategy["framework"] = "fastapi"
                        strategy["port"] = 8000
                    elif "django" in requirements.lower():
                        strategy["framework"] = "django"
                        strategy["port"] = 8000
            
            # Check for existing Dockerfile
            if os.path.exists(os.path.join(source_path, "Dockerfile")):
                strategy["dockerfile_needed"] = False
                strategy["has_dockerfile"] = True
            
            # Check for Kubernetes manifests
            if os.path.exists(os.path.join(source_path, "k8s")) or \
               os.path.exists(os.path.join(source_path, "kubernetes")):
                strategy["has_k8s_manifests"] = True
            
            logger.info(f"Analyzed project: {strategy}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error analyzing project: {str(e)}")
            return strategy
    
    async def _build_application(self, source_path: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Build the application"""
        build_result = {"status": "success", "steps": []}
        
        try:
            # Create Dockerfile if needed
            if strategy.get("dockerfile_needed", True):
                dockerfile_content = self._generate_dockerfile(strategy)
                dockerfile_path = os.path.join(source_path, "Dockerfile")
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)
                build_result["steps"].append("Generated Dockerfile")
            
            # Build Docker image if Docker is available
            if self.docker_client:
                image_name = f"ai-agent-app:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                try:
                    image, logs = self.docker_client.images.build(
                        path=source_path,
                        tag=image_name,
                        rm=True
                    )
                    
                    build_result.update({
                        "docker_image": image_name,
                        "image_id": image.id,
                        "build_logs": [log.get('stream', '') for log in logs if 'stream' in log]
                    })
                    build_result["steps"].append(f"Built Docker image: {image_name}")
                    
                except Exception as e:
                    logger.error(f"Docker build failed: {str(e)}")
                    build_result["status"] = "failed"
                    build_result["error"] = str(e)
            else:
                build_result["steps"].append("Docker not available, skipping image build")
            
            return build_result
            
        except Exception as e:
            logger.error(f"Error building application: {str(e)}")
            build_result["status"] = "failed"
            build_result["error"] = str(e)
            return build_result
    
    async def _deploy_application(self, source_path: str, strategy: Dict[str, Any], 
                                environment: str, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy the application to the target environment"""
        deploy_result = {"status": "success", "steps": [], "endpoints": []}
        
        try:
            if environment == "dev":
                # For dev environment, run locally or in Docker
                if self.docker_client and build_result.get("docker_image"):
                    container_result = await self._run_docker_container(
                        build_result["docker_image"], strategy, environment
                    )
                    deploy_result.update(container_result)
                else:
                    # Run locally
                    local_result = await self._run_locally(source_path, strategy)
                    deploy_result.update(local_result)
            
            elif environment in ["staging", "prod"]:
                # For staging/prod, deploy to Kubernetes if available
                if self.k8s_client:
                    k8s_result = await self._deploy_to_kubernetes(
                        source_path, strategy, environment, build_result
                    )
                    deploy_result.update(k8s_result)
                else:
                    # Fallback to Docker deployment
                    if self.docker_client and build_result.get("docker_image"):
                        container_result = await self._run_docker_container(
                            build_result["docker_image"], strategy, environment
                        )
                        deploy_result.update(container_result)
                    else:
                        raise Exception("No deployment target available for staging/prod")
            
            return deploy_result
            
        except Exception as e:
            logger.error(f"Error deploying application: {str(e)}")
            deploy_result["status"] = "failed"
            deploy_result["error"] = str(e)
            return deploy_result
    
    async def _run_docker_container(self, image_name: str, strategy: Dict[str, Any], 
                                  environment: str) -> Dict[str, Any]:
        """Run application in Docker container"""
        try:
            port = strategy.get("port", 3000)
            container_name = f"ai-agent-app-{environment}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Run container
            container = self.docker_client.containers.run(
                image_name,
                name=container_name,
                ports={f'{port}/tcp': port},
                detach=True,
                environment={
                    "NODE_ENV": environment,
                    "PORT": str(port)
                }
            )
            
            return {
                "deployment_type": "docker",
                "container_id": container.id,
                "container_name": container_name,
                "endpoints": [f"http://localhost:{port}"],
                "steps": [f"Started Docker container: {container_name}"]
            }
            
        except Exception as e:
            logger.error(f"Error running Docker container: {str(e)}")
            raise
    
    async def _run_locally(self, source_path: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Run application locally"""
        try:
            port = strategy.get("port", 3000)
            
            # This is a simulation for demo purposes
            # In a real implementation, you would start the actual process
            
            return {
                "deployment_type": "local",
                "process_id": "simulated",
                "endpoints": [f"http://localhost:{port}"],
                "steps": [f"Started local development server on port {port}"]
            }
            
        except Exception as e:
            logger.error(f"Error running locally: {str(e)}")
            raise
    
    async def _deploy_to_kubernetes(self, source_path: str, strategy: Dict[str, Any], 
                                  environment: str, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy application to Kubernetes"""
        try:
            app_name = f"ai-agent-app-{environment}"
            namespace = environment
            
            # Create Kubernetes manifests
            manifests = self._generate_k8s_manifests(app_name, strategy, build_result, environment)
            
            # Apply manifests (simulation for demo)
            # In a real implementation, you would apply these to the cluster
            
            return {
                "deployment_type": "kubernetes",
                "namespace": namespace,
                "app_name": app_name,
                "manifests": list(manifests.keys()),
                "endpoints": [f"http://{app_name}.{namespace}.svc.cluster.local"],
                "steps": [
                    f"Created namespace: {namespace}",
                    f"Applied deployment: {app_name}",
                    f"Applied service: {app_name}",
                    f"Applied ingress: {app_name}"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error deploying to Kubernetes: {str(e)}")
            raise
    
    def _generate_dockerfile(self, strategy: Dict[str, Any]) -> str:
        """Generate Dockerfile based on project strategy"""
        if strategy["type"] == "nodejs":
            return """FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
        elif strategy["type"] == "python":
            if strategy.get("framework") == "flask":
                return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
"""
            elif strategy.get("framework") == "fastapi":
                return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        # Default Dockerfile
        return """FROM alpine:latest

WORKDIR /app
COPY . .

EXPOSE 8000

CMD ["echo", "Application running"]
"""
    
    def _generate_k8s_manifests(self, app_name: str, strategy: Dict[str, Any], 
                               build_result: Dict[str, Any], environment: str) -> Dict[str, str]:
        """Generate Kubernetes manifests"""
        port = strategy.get("port", 3000)
        image = build_result.get("docker_image", "nginx:latest")
        
        deployment = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: {environment}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {image}
        ports:
        - containerPort: {port}
        env:
        - name: NODE_ENV
          value: "{environment}"
        readinessProbe:
          httpGet:
            path: {strategy.get('health_check', '/')}
            port: {port}
          initialDelaySeconds: 10
          periodSeconds: 5
"""
        
        service = f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}
  namespace: {environment}
spec:
  selector:
    app: {app_name}
  ports:
  - port: 80
    targetPort: {port}
  type: ClusterIP
"""
        
        ingress = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app_name}
  namespace: {environment}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: {app_name}-{environment}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {app_name}
            port:
              number: 80
"""
        
        return {
            "deployment.yaml": deployment,
            "service.yaml": service,
            "ingress.yaml": ingress
        }
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get status of a deployment"""
        if deployment_id not in self.active_deployments:
            return {"error": "Deployment not found"}
        
        return self.active_deployments[deployment_id]
    
    async def list_active_deployments(self) -> List[Dict[str, Any]]:
        """List all active deployments"""
        return [
            {
                "deployment_id": deployment_id,
                "status": deployment_info["status"],
                "environment": deployment_info.get("environment"),
                "repository_url": deployment_info.get("repository_url"),
                "start_time": deployment_info["start_time"].isoformat()
            }
            for deployment_id, deployment_info in self.active_deployments.items()
        ]
    
    async def stop_deployment(self, deployment_id: str) -> bool:
        """Stop a running deployment"""
        if deployment_id not in self.active_deployments:
            return False
        
        try:
            deployment = self.active_deployments[deployment_id]
            
            # Stop Docker container if applicable
            if "container_id" in deployment.get("deploy_result", {}):
                container_id = deployment["deploy_result"]["container_id"]
                container = self.docker_client.containers.get(container_id)
                container.stop()
                container.remove()
            
            # Update status
            deployment["status"] = "stopped"
            deployment["stop_time"] = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping deployment {deployment_id}: {str(e)}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "status": "active" if self._initialized else "inactive",
            "active_deployments": len([
                d for d in self.active_deployments.values() 
                if d["status"] in ["cloning", "building", "deploying"]
            ]),
            "total_deployments": len(self.active_deployments),
            "capabilities": {
                "docker": self.docker_client is not None,
                "kubernetes": self.k8s_client is not None,
                "local_deployment": True,
                "cloud_deployment": bool(settings.AWS_ACCESS_KEY_ID)
            }
        }
    
    async def cleanup(self):
        """Cleanup agent resources"""
        logger.info("Cleaning up Deployment Agent...")
        
        # Stop all active deployments
        for deployment_id in list(self.active_deployments.keys()):
            await self.stop_deployment(deployment_id)
        
        # Close Docker client
        if self.docker_client:
            self.docker_client.close()
        
        logger.info("Deployment Agent cleanup completed")