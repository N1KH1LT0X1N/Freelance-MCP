"""
Test script to verify the Freelance MCP setup works correctly.

Run this script to test your installation before using the main client.

Usage:
    python test_setup.py
"""

import asyncio
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("🧪 Testing imports...")
    
    required_packages = [
        ("mcp", "MCP SDK"),
        ("pydantic", "Pydantic"),
        ("dotenv", "Python-dotenv")
    ]
    
    optional_packages = [
        ("langchain_groq", "Langchain-groq")
    ]
    
    all_good = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            all_good = False
    
    for package, name in optional_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"⚠️  {name}: {e} (optional)")
    
    return all_good


def test_files():
    """Test that required files exist"""
    print("\n🗂️  Testing files...")
    
    required_files = [
        ("freelance_server.py", "MCP Server"),
        ("freelance_client.py", "MCP Client")
    ]
    
    optional_files = [
        (".env", "Environment file"),
        ("requirements.txt", "Requirements file")
    ]
    
    all_good = True
    
    for filename, description in required_files:
        if Path(filename).exists():
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ {description}: {filename} not found")
            all_good = False
    
    for filename, description in optional_files:
        if Path(filename).exists():
            print(f"✅ {description}: {filename}")
        else:
            print(f"⚠️  {description}: {filename} not found")
    
    return all_good


def test_environment():
    """Test environment configuration"""
    print("\n🌍 Testing environment...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (requires 3.8+)")
        return False
    
    # Check API key
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        if len(groq_key) > 20:  # Basic validation
            print("✅ GROQ_API_KEY configured")
        else:
            print("⚠️  GROQ_API_KEY seems too short")
    else:
        print("⚠️  GROQ_API_KEY not set (LLM features won't work)")
    
    return True


async def test_server_startup():
    """Test that the server can start up"""
    print("\n🚀 Testing server startup...")
    
    try:
        from mcp import StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["freelance_server.py", "stdio"],
            env=dict(os.environ)
        )
        
        # Try to start server with a short timeout
        print("Starting server...")
        
        async with stdio_client(server_params) as (read, write):
            print("✅ Server started successfully")
            
            # Try to create a session
            from mcp import ClientSession
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                print("✅ Server initialized successfully")
                
                # Test basic functionality
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools")
                
                resources = await session.list_resources()
                print(f"✅ Found {len(resources.resources)} resources")
                
        return True
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False


async def test_basic_tool():
    """Test a basic tool call"""
    print("\n🔧 Testing basic tool functionality...")
    
    try:
        from mcp import StdioServerParameters, ClientSession
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["freelance_server.py", "stdio"],
            env=dict(os.environ)
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test search_gigs tool
                result = await session.call_tool("search_gigs", {
                    "skills": ["JavaScript", "Python"],
                    "max_budget": 1000
                })
                
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    data = result.structuredContent
                    if "total_found" in data:
                        print(f"✅ Tool call successful - found {data['total_found']} gigs")
                        return True
                
                # Fallback to text content
                if result.content and len(result.content) > 0:
                    print("✅ Tool call successful (text response)")
                    return True
                
                print("⚠️  Tool call returned empty result")
                return False
                
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False


def create_minimal_env():
    """Create a minimal .env file for testing"""
    env_content = """# Minimal environment for testing
GROQ_API_KEY=test_key_please_replace_with_real_key
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content)
        print("📄 Created minimal .env file")
        print("⚠️  Please edit .env and add your real GROQ_API_KEY")


def main():
    """Run all tests"""
    print("🧪 Freelance MCP Setup Test")
    print("=" * 50)
    
    # Create env file if missing
    if not Path(".env").exists():
        create_minimal_env()
    
    # Run tests
    tests_passed = 0
    total_tests = 0
    
    # Import tests
    total_tests += 1
    if test_imports():
        tests_passed += 1
    
    # File tests
    total_tests += 1
    if test_files():
        tests_passed += 1
    
    # Environment tests
    total_tests += 1
    if test_environment():
        tests_passed += 1
    
    # Server startup test
    print("\n⏳ Running server tests (may take a moment)...")
    total_tests += 1
    try:
        if asyncio.run(test_server_startup()):
            tests_passed += 1
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    
    # Basic tool test
    total_tests += 1
    try:
        if asyncio.run(test_basic_tool()):
            tests_passed += 1
    except Exception as e:
        print(f"❌ Basic tool test failed: {e}")
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your setup is ready.")
        print("Run: python freelance_client.py --mode demo")
    elif tests_passed >= total_tests - 1:
        print("⚠️  Most tests passed. Check warnings above.")
        print("You can probably run: python freelance_client.py --mode demo")
    else:
        print("❌ Several tests failed. Please fix the issues above.")
        print("Check the installation guide for help.")
    
    print("\n💡 Next steps:")
    if not os.getenv("GROQ_API_KEY") or len(os.getenv("GROQ_API_KEY", "")) < 20:
        print("1. Get a GROQ API key from https://console.groq.com/")
        print("2. Add it to your .env file: GROQ_API_KEY=your_real_key")
    print("3. Run the full demo: python freelance_client.py --mode demo")
    print("4. Try interactive mode: python freelance_client.py --mode interactive")


if __name__ == "__main__":
    main()