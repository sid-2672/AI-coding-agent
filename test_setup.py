#!/usr/bin/env python3
"""
Test script to verify the offline coding assistant setup.
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import typer
        print("✅ typer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import typer: {e}")
        return False
    
    try:
        import llama_cpp
        print("✅ llama_cpp imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import llama_cpp: {e}")
        return False
    
    try:
        import rich
        print("✅ rich imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import rich: {e}")
        return False
    
    try:
        import pygments
        print("✅ pygments imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pygments: {e}")
        return False
    
    try:
        import pydantic
        print("✅ pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pydantic: {e}")
        return False
    
    return True

def test_agent_modules():
    """Test if agent modules can be imported."""
    print("\nTesting agent modules...")
    
    try:
        from agent.model import CodeAssistant
        print("✅ CodeAssistant imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CodeAssistant: {e}")
        return False
    
    try:
        from agent.memory import ConversationMemory
        print("✅ ConversationMemory imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ConversationMemory: {e}")
        return False
    
    try:
        from agent.code_tools import CodeTools
        print("✅ CodeTools imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CodeTools: {e}")
        return False
    
    return True

def test_cli():
    """Test if CLI can be imported."""
    print("\nTesting CLI...")
    
    try:
        from main import app
        print("✅ CLI app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CLI app: {e}")
        return False
    
    return True

def check_model_file():
    """Check if model file exists."""
    print("\nChecking model file...")
    
    model_path = Path("deepseek-coder-1.3b-instruct.Q4_K_M.gguf")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ Model file found: {model_path.name} ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ Model file not found")
        print("Download it with:")
        print("wget https://huggingface.co/TheBloke/deepseek-coder-1.3B-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q4_K_M.gguf")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Offline Coding Assistant Setup\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test agent modules
    if not test_agent_modules():
        all_passed = False
    
    # Test CLI
    if not test_cli():
        all_passed = False
    
    # Check model file
    model_exists = check_model_file()
    if not model_exists:
        print("\n⚠️  Model file is missing but not required for basic functionality")
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        if model_exists:
            print("You can now run: python3 main.py chat")
        else:
            print("Download the model file to start using the assistant.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 