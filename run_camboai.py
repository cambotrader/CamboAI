#!/usr/bin/env python3
"""
🚀 CAMBOAI TRADING PLATFORM - STARTUP SCRIPT
One-command startup for the complete trading platform
"""

import os
import sys
import asyncio
import subprocess
import time
import signal
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
import platform
import webbrowser

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CamboAILauncher:
    """Complete CamboAI platform launcher"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.base_path = Path(__file__).parent
        self.backend_path = self.base_path / "backend"
        self.frontend_path = self.base_path / "frontend" 
        self.mobile_path = self.base_path / "mobile"
        
        # Configuration
        self.config = {
            "backend_host": "0.0.0.0",
            "backend_port": 8000,
            "frontend_port": 3000,
            "mobile_port": 19006,
            "open_browser": True,
            "enable_services": {
                "backend": True,
                "frontend": True,
                "mobile": False,  # Optional
                "redis": False,   # Optional
                "postgres": False # Optional
            }
        }
        
        # Process management
        self.running = False
        self.startup_complete = False
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        
        logger.info("🔍 Checking prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 9):
            logger.error(f"❌ Python 3.9+ required, found {python_version.major}.{python_version.minor}")
            return False
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check Node.js (if frontend/mobile enabled)
        if self.config["enable_services"]["frontend"] or self.config["enable_services"]["mobile"]:
            try:
                result = subprocess.run(["node", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✅ Node.js {result.stdout.strip()}")
                else:
                    logger.error("❌ Node.js not found - required for frontend/mobile")
                    return False
            except FileNotFoundError:
                logger.error("❌ Node.js not found - required for frontend/mobile")
                return False
        
        # Check Python dependencies
        try:
            import fastapi
            import uvicorn
            import sqlalchemy
            logger.info("✅ Python dependencies available")
        except ImportError as e:
            logger.error(f"❌ Missing Python dependencies: {e}")
            logger.info("💡 Run: pip install -r backend/requirements.txt")
            return False
        
        return True
    
    def setup_environment(self):
        """Setup environment variables and directories"""
        
        logger.info("⚙️ Setting up environment...")
        
        # Create necessary directories
        directories = [
            "logs",
            "backend/logs", 
            "backend/uploads",
            "backend/secrets"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        env_vars = {
            "PYTHONPATH": str(self.backend_path),
            "ENVIRONMENT": "development",
            "DATABASE_URL": "sqlite:///./cambo_ai_trader.db",  # Default SQLite
            "SECRET_KEY": "development-secret-key-change-in-production",
            "REDIS_URL": "redis://localhost:6379",
        }
        
        for key, value in env_vars.items():
            if key not in os.environ:
                os.environ[key] = value
        
        logger.info("✅ Environment configured")
    
    def start_backend(self) -> subprocess.Popen:
        """Start the FastAPI backend server"""
        
        logger.info("🚀 Starting backend server...")
        
        # Change to backend directory
        backend_cmd = [
            sys.executable, 
            "-m", 
            "uvicorn",
            "app.main:app",
            "--host", self.config["backend_host"],
            "--port", str(self.config["backend_port"]),
            "--reload"
        ]
        
        try:
            process = subprocess.Popen(
                backend_cmd,
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(process)
            logger.info(f"✅ Backend server started on http://localhost:{self.config['backend_port']}")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            raise
    
    def start_frontend(self) -> subprocess.Popen:
        """Start the React frontend development server"""
        
        if not self.config["enable_services"]["frontend"]:
            return None
        
        if not self.frontend_path.exists():
            logger.warning("⚠️ Frontend directory not found, skipping...")
            return None
        
        logger.info("🌐 Starting frontend server...")
        
        # Check if node_modules exists
        if not (self.frontend_path / "node_modules").exists():
            logger.info("📦 Installing frontend dependencies...")
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=self.frontend_path,
                capture_output=True,
                text=True
            )
            
            if npm_install.returncode != 0:
                logger.error(f"❌ Failed to install frontend dependencies: {npm_install.stderr}")
                return None
        
        # Set frontend environment
        frontend_env = os.environ.copy()
        frontend_env["REACT_APP_API_URL"] = f"http://localhost:{self.config['backend_port']}"
        frontend_env["PORT"] = str(self.config["frontend_port"])
        
        frontend_cmd = ["npm", "start"]
        
        try:
            process = subprocess.Popen(
                frontend_cmd,
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=frontend_env
            )
            
            self.processes.append(process)
            logger.info(f"✅ Frontend server started on http://localhost:{self.config['frontend_port']}")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return None
    
    def start_mobile(self) -> subprocess.Popen:
        """Start the React Native/Expo mobile development server"""
        
        if not self.config["enable_services"]["mobile"]:
            return None
        
        if not self.mobile_path.exists():
            logger.warning("⚠️ Mobile directory not found, skipping...")
            return None
        
        logger.info("📱 Starting mobile development server...")
        
        # Check if node_modules exists
        if not (self.mobile_path / "node_modules").exists():
            logger.info("📦 Installing mobile dependencies...")
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=self.mobile_path,
                capture_output=True,
                text=True
            )
            
            if npm_install.returncode != 0:
                logger.error(f"❌ Failed to install mobile dependencies: {npm_install.stderr}")
                return None
        
        mobile_cmd = ["npx", "expo", "start"]
        
        try:
            process = subprocess.Popen(
                mobile_cmd,
                cwd=self.mobile_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            logger.info(f"✅ Mobile development server started on port {self.config['mobile_port']}")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start mobile server: {e}")
            return None
    
    def wait_for_backend_ready(self, timeout: int = 30) -> bool:
        """Wait for backend to be ready"""
        
        logger.info("⏳ Waiting for backend to be ready...")
        
        import requests
        backend_url = f"http://localhost:{self.config['backend_port']}/health"
        
        for i in range(timeout):
            try:
                response = requests.get(backend_url, timeout=2)
                if response.status_code == 200:
                    logger.info("✅ Backend is ready!")
                    return True
            except:
                pass
            
            time.sleep(1)
            print(f"\rWaiting... {i+1}/{timeout}s", end="", flush=True)
        
        print()  # New line
        logger.error("❌ Backend failed to start within timeout")
        return False
    
    def open_browser(self):
        """Open browser with the application"""
        
        if not self.config["open_browser"]:
            return
        
        urls_to_open = [
            f"http://localhost:{self.config['backend_port']}",  # Main dashboard
            f"http://localhost:{self.config['backend_port']}/demo",  # Demo trading
            f"http://localhost:{self.config['backend_port']}/api/docs",  # API docs
        ]
        
        # Add frontend URL if available
        if self.config["enable_services"]["frontend"]:
            urls_to_open.insert(0, f"http://localhost:{self.config['frontend_port']}")
        
        logger.info("🌐 Opening browser...")
        
        for url in urls_to_open:
            try:
                webbrowser.open(url)
                time.sleep(1)  # Delay between opening tabs
            except:
                pass
    
    def display_startup_info(self):
        """Display startup information"""
        
        print("\n" + "="*80)
        print("🚀 CAMBOAI TRADING PLATFORM")
        print("="*80)
        print("Institutional-Grade AI-Powered Trading Platform")
        print()
        
        # Service URLs
        print("🌐 SERVICE URLS:")
        print(f"   • Main Dashboard:    http://localhost:{self.config['backend_port']}")
        print(f"   • Demo Trading:      http://localhost:{self.config['backend_port']}/demo")
        print(f"   • API Documentation: http://localhost:{self.config['backend_port']}/api/docs")
        print(f"   • System Status:     http://localhost:{self.config['backend_port']}/api/v1/system/status")
        
        if self.config["enable_services"]["frontend"]:
            print(f"   • React Frontend:    http://localhost:{self.config['frontend_port']}")
        
        if self.config["enable_services"]["mobile"]:
            print(f"   • Mobile Dev Server: http://localhost:{self.config['mobile_port']}")
        
        print()
        
        # Features
        print("✨ AVAILABLE FEATURES:")
        print("   • Real-time market data streaming")
        print("   • Paper trading with realistic simulation")
        print("   • Advanced risk management and VaR calculations")
        print("   • AI-powered trading signals and analysis")
        print("   • DeFi yield farming and arbitrage detection")
        print("   • Voice trading assistant (in development)")
        print("   • Professional order management (TWAP, VWAP, Iceberg)")
        print("   • Multi-asset support (Stocks, Options, Crypto, Forex)")
        
        print()
        
        # Quick start
        print("🎯 QUICK START:")
        print("   1. Visit the Demo Trading page to try paper trading")
        print("   2. Check API Documentation for integration details")
        print("   3. Monitor System Status for real-time metrics")
        print("   4. Use Ctrl+C to stop all services")
        
        print()
        print("="*80)
        print()
    
    def monitor_processes(self):
        """Monitor running processes"""
        
        while self.running:
            try:
                # Check if any process has died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        logger.error(f"❌ Process {i} has exited with code {process.returncode}")
                        
                        # Read any error output
                        try:
                            stderr = process.stderr.read()
                            if stderr:
                                logger.error(f"Error output: {stderr}")
                        except:
                            pass
                
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                break
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"\n🛑 Received signal {signum}, shutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all services"""
        
        logger.info("🛑 Shutting down CamboAI Trading Platform...")
        self.running = False
        
        # Terminate all processes
        for i, process in enumerate(self.processes):
            try:
                logger.info(f"Stopping process {i}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing process {i}...")
                    process.kill()
                    
            except Exception as e:
                logger.error(f"Error stopping process {i}: {e}")
        
        logger.info("✅ All services stopped")
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        
        try:
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Check prerequisites
            if not self.check_prerequisites():
                sys.exit(1)
            
            # Setup environment
            self.setup_environment()
            
            # Start services
            logger.info("🚀 Starting CamboAI Trading Platform...")
            
            # Start backend (required)
            backend_process = self.start_backend()
            
            # Wait for backend to be ready
            if not self.wait_for_backend_ready():
                self.shutdown()
                return
            
            # Start frontend (optional)
            self.start_frontend()
            
            # Start mobile (optional)
            self.start_mobile()
            
            # Wait a moment for services to stabilize
            time.sleep(3)
            
            # Display startup information
            self.display_startup_info()
            
            # Open browser
            self.open_browser()
            
            # Mark startup complete
            self.startup_complete = True
            self.running = True
            
            logger.info("✅ All services started successfully!")
            logger.info("💡 Use Ctrl+C to stop all services")
            
            # Monitor processes
            self.monitor_processes()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            self.shutdown()
            sys.exit(1)

def main():
    """Main entry point"""
    
    print("🚀 CamboAI Trading Platform Launcher")
    print("=====================================")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="CamboAI Trading Platform Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend service")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--enable-mobile", action="store_true", help="Start mobile development server")
    parser.add_argument("--port", type=int, default=8000, help="Backend port (default: 8000)")
    
    args = parser.parse_args()
    
    # Create launcher
    launcher = CamboAILauncher()
    
    # Configure based on arguments
    if args.backend_only:
        launcher.config["enable_services"]["frontend"] = False
        launcher.config["enable_services"]["mobile"] = False
    
    if args.no_browser:
        launcher.config["open_browser"] = False
    
    if args.enable_mobile:
        launcher.config["enable_services"]["mobile"] = True
    
    launcher.config["backend_port"] = args.port
    
    # Run launcher
    launcher.run()

if __name__ == "__main__":
    main()