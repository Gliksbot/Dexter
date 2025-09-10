#!/usr/bin/env python3
"""
Dexter Simple v2 - Startup Script

Easy launcher for the Dexter system with setup validation.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is suitable"""
    if sys.version_info < (3, 8, 0):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_config_file():
    """Check if configuration file exists"""
    config_path = Path("dexter_simple_config.json")
    
    if not config_path.exists():
        print("❌ Configuration file not found: dexter_simple_config.json")
        print("   Creating default configuration...")
        
        # Create minimal config
        default_config = {
            "system": {
                "name": "Dexter Simple v2",
                "version": "2.0.0",
                "server_mode": True,
                "debug": True
            },
            "llms": {
                "dexter": {
                    "name": "Dexter",
                    "role": "primary_orchestrator",
                    "enabled": True,
                    "provider": "ollama",
                    "endpoint": "https://ollama.com",
                    "model": "gpt-oss:120b",
                    "api_key_env": "OLLAMAKEY",
                    "identity": "You are Dexter, Jeffrey's personal AI assistant. You orchestrate tasks, generate code, and build skills. You are the primary interface - you speak directly to Jeffrey.",
                    "personality": "Professional, helpful, and proactive. You take initiative and build capabilities.",
                    "params": {"temperature": 0.7, "max_tokens": 2048, "top_p": 0.9}
                },
                "partner": {
                    "name": "Partner",
                    "role": "background_collaborator",
                    "enabled": True,
                    "provider": "ollama",
                    "endpoint": "https://ollama.com",
                    "model": "llama3.1:8b",
                    "api_key_env": "OLLAMAKEY",
                    "identity": "You are Partner, working with Dexter in the background. You draft proposals, update knowledge graphs, search skills, and provide technical expertise. You work silently unless directly addressed.",
                    "personality": "Analytical, thorough, and supportive. You enhance Dexter's capabilities.",
                    "params": {"temperature": 0.3, "max_tokens": 2048, "top_p": 0.8}
                }
            },
            "brain": {
                "memory": {
                    "short_term": {"enabled": True, "max_items": 1000, "storage": "ram"},
                    "long_term": {"enabled": True, "storage": "sqlite", "database_path": "./data/brain.db"}
                },
                "knowledge_graph": {"enabled": True, "storage": "sqlite", "database_path": "./data/knowledge.db"},
                "pattern_tables": {"enabled": True, "storage": "sqlite", "database_path": "./data/patterns.db"},
                "neural_components": {"enabled": True, "model_path": "./data/neural_net.pkl"}
            },
            "skills": {"enabled": True, "storage_path": "./skills", "database_path": "./data/skills.db"},
            "interface": {"type": "tkinter", "voice": {"enabled": False}},
            "collaboration": {"background_processing": True, "partner_active": True}
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✅ Created default config: {config_path}")
    else:
        print("✅ Configuration file found")
    
    return True

def check_directories():
    """Create necessary directories"""
    directories = ['data', 'skills', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory ready: {directory}/")
    
    return True

def install_requirements():
    """Install Python requirements"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ Requirements file not found")
        return False
    
    try:
        print("🔄 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def main():
    """Main startup sequence"""
    
    print("🚀 Dexter Simple v2 - Startup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not check_directories():
        sys.exit(1)
    
    # Check config
    if not check_config_file():
        sys.exit(1)
    
    # Install requirements (optional)
    install_choice = input("\n📦 Install/update requirements? (y/N): ").lower().strip()
    if install_choice in ['y', 'yes']:
        if not install_requirements():
            print("⚠️  Requirements installation failed, but continuing...")
    
    # Set API key reminder
    print("\n🔑 Make sure your API key is set:")
    print("   $env:OLLAMAKEY = 'your-api-key-here'")
    
    # Start Dexter - THIS IS THE KEY FIX!
    print("\n🚀 Starting Dexter Simple v2...")
    try:
        # Import and run the real UI
        from dexter_ui import main as run_dexter_ui
        run_dexter_ui()
        
    except ImportError as e:
        print(f"❌ Failed to import Dexter UI: {e}")
        print("   Make sure dexter_ui.py and llm_orchestrator.py are present")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dexter shutdown by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
