"""
MCP Client for Freelance Gig Aggregator Server

A comprehensive MCP client that connects to the freelance server and demonstrates
code review and debugging capabilities with LLM integration.

Features:
- Connects to freelance server via stdio transport
- Interactive code review tool usage
- Code debugging and fixing capabilities
- Integration with server's LLM features
- User profile management
- Gig searching and proposal generation

Installation:
    pip install mcp langchain-groq pydantic python-dotenv

Usage:
    python freelance_client.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import AnyUrl

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Server configuration
SERVER_SCRIPT = "freelance_server.py"  # Path to the freelance server script


class FreelanceClient:
    """MCP Client for interacting with the Freelance Gig Aggregator server"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.server_params = StdioServerParameters(
            command=sys.executable,  # Use current Python interpreter
            args=[SERVER_SCRIPT, "stdio"],  # Run server with stdio transport
            env=dict(os.environ)  # Pass current environment
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client_context = stdio_client(self.server_params)
        self.read, self.write = await self.client_context.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        await self.client_context.__aexit__(exc_type, exc_val, exc_tb)
    
    async def list_available_capabilities(self) -> Dict[str, List[str]]:
        """List all available tools, resources, and prompts from the server"""
        capabilities = {}
        
        # List tools
        tools_response = await self.session.list_tools()
        capabilities["tools"] = [tool.name for tool in tools_response.tools]
        
        # List resources
        resources_response = await self.session.list_resources()
        capabilities["resources"] = [resource.uri for resource in resources_response.resources]
        
        # List prompts
        prompts_response = await self.session.list_prompts()
        capabilities["prompts"] = [prompt.name for prompt in prompts_response.prompts]
        
        return capabilities
    
    async def create_user_profile(self, name: str, title: str, skills: List[Dict], 
                                rate_min: float, rate_max: float, location: str, 
                                languages: List[str]) -> Dict[str, Any]:
        """Create a user profile using the server's tool"""
        result = await self.session.call_tool(
            "create_user_profile",
            arguments={
                "name": name,
                "title": title,
                "skills_data": skills,
                "hourly_rate_min": rate_min,
                "hourly_rate_max": rate_max,
                "location": location,
                "languages": languages
            }
        )
        
        # Parse structured content if available
        if hasattr(result, 'structuredContent') and result.structuredContent:
            return result.structuredContent
        
        # Fallback to text content
        for content in result.content:
            if isinstance(content, types.TextContent):
                try:
                    return json.loads(content.text)
                except json.JSONDecodeError:
                    return {"response": content.text}
        
        return {"error": "No valid response received"}
    
    async def search_gigs(self, skills: List[str], max_budget: Optional[float] = None,
                         platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search for gigs based on skills and criteria"""
        args = {"skills": skills}
        if max_budget:
            args["max_budget"] = max_budget
        if platforms:
            args["platforms"] = platforms
        
        result = await self.session.call_tool("search_gigs", arguments=args)
        
        if hasattr(result, 'structuredContent') and result.structuredContent:
            return result.structuredContent
        
        for content in result.content:
            if isinstance(content, types.TextContent):
                try:
                    return json.loads(content.text)
                except json.JSONDecodeError:
                    return {"response": content.text}
        
        return {"error": "No valid response received"}
    
    async def review_code_file(self, file_path: str, review_type: str = "general") -> Dict[str, Any]:
        """Review a code file using the server's code review tool"""
        print(f"🔍 Reviewing code file: {file_path}")
        
        try:
            result = await self.session.call_tool(
                "code_review",
                arguments={
                    "file_path": file_path,
                    "review_type": review_type
                }
            )
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                return result.structuredContent
            
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"response": content.text}
            
            return {"error": "No valid response received"}
            
        except Exception as e:
            return {"error": f"Failed to review code: {str(e)}"}
    
    async def debug_code_file(self, file_path: str, issue_description: str, 
                             fix_type: str = "suggest", backup: bool = True) -> Dict[str, Any]:
        """Debug and potentially fix issues in a code file"""
        print(f"🔧 Debugging code file: {file_path}")
        print(f"Issue: {issue_description}")
        
        try:
            result = await self.session.call_tool(
                "code_debug",
                arguments={
                    "file_path": file_path,
                    "issue_description": issue_description,
                    "fix_type": fix_type,
                    "backup": backup
                }
            )
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                return result.structuredContent
            
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"response": content.text}
            
            return {"error": "No valid response received"}
            
        except Exception as e:
            return {"error": f"Failed to debug code: {str(e)}"}
    
    async def generate_proposal(self, gig_id: str, user_profile: Dict[str, Any],
                               tone: str = "professional") -> Dict[str, Any]:
        """Generate a proposal for a specific gig"""
        print(f"✍️  Generating proposal for gig: {gig_id}")
        
        try:
            result = await self.session.call_tool(
                "generate_proposal",
                arguments={
                    "gig_id": gig_id,
                    "user_profile": user_profile,
                    "tone": tone,
                    "include_portfolio": True
                }
            )
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                return result.structuredContent
            
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"response": content.text}
            
            return {"error": "No valid response received"}
            
        except Exception as e:
            return {"error": f"Failed to generate proposal: {str(e)}"}
    
    async def analyze_profile_fit(self, profile_data: Dict[str, Any], 
                                 gig_id: str) -> Dict[str, Any]:
        """Analyze how well a profile fits a specific gig"""
        try:
            result = await self.session.call_tool(
                "analyze_profile_fit",
                arguments={
                    "profile_data": profile_data,
                    "gig_id": gig_id
                }
            )
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                return result.structuredContent
            
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"response": content.text}
            
            return {"error": "No valid response received"}
            
        except Exception as e:
            return {"error": f"Failed to analyze profile fit: {str(e)}"}
    
    async def negotiate_rate(self, current_rate: float, target_rate: float,
                           justification_points: List[str] = None) -> Dict[str, Any]:
        """Generate rate negotiation strategy"""
        try:
            args = {
                "current_rate": current_rate,
                "target_rate": target_rate,
                "project_complexity": "medium"
            }
            if justification_points:
                args["justification_points"] = justification_points
            
            result = await self.session.call_tool("negotiate_rate", arguments=args)
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                return result.structuredContent
            
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"response": content.text}
            
            return {"error": "No valid response received"}
            
        except Exception as e:
            return {"error": f"Failed to negotiate rate: {str(e)}"}


def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_dict_pretty(data: Dict[str, Any], indent: int = 0):
    """Pretty print dictionary data"""
    spacing = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{spacing}{key}:")
            print_dict_pretty(value, indent + 1)
        elif isinstance(value, list):
            print(f"{spacing}{key}: {value}")
        else:
            print(f"{spacing}{key}: {value}")


async def demonstrate_code_review_workflow():
    """Demonstrate the complete code review and debugging workflow"""
    
    print_separator("MCP Freelance Client - Code Review & Debug Demo")
    
    async with FreelanceClient() as client:
        # Check server capabilities
        print("🚀 Connected to Freelance MCP Server")
        
        capabilities = await client.list_available_capabilities()
        print("\n📋 Available Server Capabilities:")
        for cap_type, items in capabilities.items():
            print(f"  {cap_type.upper()}: {len(items)} items")
            for item in items[:5]:  # Show first 5 items
                print(f"    - {item}")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")
        
        # Create a sample code file for demonstration
        print_separator("Creating Sample Code File")
        
        sample_code = '''
# Sample Python code with intentional issues
def calculate_average(numbers):
    total = 0
    count = 0
    for number in numbers:
        total += number
        count += 1
    return total / count  # Division by zero risk

def process_data(data):
    result = []
    for i in data:
        if i > 0:
            result.append(i * 2)
    return result

# Missing docstrings and type hints
def fetch_user_data(user_id):
    # This function has no error handling
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()
'''
        
        sample_file_path = "sample_code_demo.py"
        with open(sample_file_path, "w") as f:
            f.write(sample_code)
        print(f"✅ Created sample file: {sample_file_path}")
        
        # Demonstrate code review
        print_separator("Code Review Analysis")
        
        review_result = await client.review_code_file(
            file_path=sample_file_path,
            review_type="general"
        )
        
        if "error" in review_result:
            print(f"❌ Review failed: {review_result['error']}")
        else:
            print("📊 Code Review Results:")
            print_dict_pretty(review_result)
        
        # Demonstrate code debugging
        print_separator("Code Debugging & Fixes")
        
        # Example 1: Fix division by zero
        debug_result1 = await client.debug_code_file(
            file_path=sample_file_path,
            issue_description="Fix division by zero risk in calculate_average function",
            fix_type="suggest",
            backup=True
        )
        
        print("🔧 Debug Result - Division by Zero:")
        if "error" in debug_result1:
            print(f"❌ Debug failed: {debug_result1['error']}")
        else:
            print_dict_pretty(debug_result1)
        
        # Example 2: Add missing docstrings
        debug_result2 = await client.debug_code_file(
            file_path=sample_file_path,
            issue_description="Add missing docstrings to functions for better documentation",
            fix_type="auto",
            backup=False  # Don't create another backup
        )
        
        print("\n📝 Debug Result - Missing Docstrings:")
        if "error" in debug_result2:
            print(f"❌ Debug failed: {debug_result2['error']}")
        else:
            print_dict_pretty(debug_result2)
        
        # Clean up the sample file
        try:
            os.remove(sample_file_path)
            print(f"\n🧹 Cleaned up sample file: {sample_file_path}")
        except:
            pass


async def demonstrate_freelance_workflow():
    """Demonstrate the complete freelance workflow"""
    
    print_separator("Freelance Workflow Demonstration")
    
    async with FreelanceClient() as client:
        
        # Create a user profile
        print_separator("Creating User Profile")
        
        skills_data = [
            {"name": "Python", "level": "advanced", "years_experience": 5},
            {"name": "React", "level": "intermediate", "years_experience": 3},
            {"name": "TypeScript", "level": "intermediate", "years_experience": 2},
            {"name": "Machine Learning", "level": "beginner", "years_experience": 1}
        ]
        
        profile_result = await client.create_user_profile(
            name="Alex Developer",
            title="Full Stack Developer & ML Enthusiast",
            skills=skills_data,
            rate_min=45.0,
            rate_max=85.0,
            location="New York, NY",
            languages=["English", "Spanish"]
        )
        
        print("👤 Profile Creation Result:")
        print_dict_pretty(profile_result)
        
        # Search for relevant gigs
        print_separator("Searching for Gigs")
        
        search_result = await client.search_gigs(
            skills=["Python", "React", "TypeScript"],
            max_budget=1000.0,
            platforms=["upwork", "freelancer"]
        )
        
        print("🔍 Gig Search Results:")
        print_dict_pretty(search_result)
        
        # Analyze profile fit for first gig
        if search_result.get("gigs") and len(search_result["gigs"]) > 0:
            first_gig = search_result["gigs"][0]
            gig_id = first_gig["id"]
            
            print_separator(f"Analyzing Fit for Gig: {first_gig['title']}")
            
            profile_data = {
                "name": "Alex Developer",
                "skills": skills_data,
                "hourly_rate_min": 45.0,
                "hourly_rate_max": 85.0,
                "years_experience": 5,
                "success_rate": 92.0
            }
            
            fit_analysis = await client.analyze_profile_fit(
                profile_data=profile_data,
                gig_id=gig_id
            )
            
            print("🎯 Profile Fit Analysis:")
            print_dict_pretty(fit_analysis)
            
            # Generate proposal if it's a good fit
            if fit_analysis.get("overall_score", 0) > 50:
                print_separator("Generating Proposal")
                
                proposal_result = await client.generate_proposal(
                    gig_id=gig_id,
                    user_profile=profile_data,
                    tone="professional"
                )
                
                print("✍️  Generated Proposal:")
                print_dict_pretty(proposal_result)
                
                # Demonstrate rate negotiation
                if proposal_result.get("proposed_rate"):
                    print_separator("Rate Negotiation Strategy")
                    
                    negotiation_result = await client.negotiate_rate(
                        current_rate=proposal_result["proposed_rate"],
                        target_rate=proposal_result["proposed_rate"] * 1.2,
                        justification_points=[
                            "5+ years of Python development experience",
                            "Full-stack expertise with React and TypeScript",
                            "Proven track record with 92% success rate",
                            "Additional ML skills for data analysis"
                        ]
                    )
                    
                    print("💰 Rate Negotiation Strategy:")
                    print_dict_pretty(negotiation_result)


async def main():
    """Main function to run the MCP client demonstration"""
    
    # Check if server file exists
    if not Path(SERVER_SCRIPT).exists():
        print(f"❌ Error: Server script '{SERVER_SCRIPT}' not found!")
        print("Please ensure the freelance_server.py file is in the current directory.")
        return
    
    # Check for required environment variables
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not set. Some LLM features may not work.")
        print("Set the environment variable or add it to a .env file.")
    
    try:
        print("🌟 Starting MCP Freelance Client Demonstration")
        print("This demo will showcase code review, debugging, and freelance workflow features.")
        
        # Run code review and debugging demonstration
        await demonstrate_code_review_workflow()
        
        # Run freelance workflow demonstration  
        await demonstrate_freelance_workflow()
        
        print_separator("Demo Complete")
        print("✅ All demonstrations completed successfully!")
        print("The client has showcased:")
        print("  - Code review capabilities")
        print("  - Code debugging and fixing")
        print("  - User profile management")
        print("  - Gig searching and matching")
        print("  - Proposal generation with LLM")
        print("  - Rate negotiation strategies")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())