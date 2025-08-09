"""
Freelance Gig Aggregator MCP Client

A comprehensive MCP client that connects to the freelance server and demonstrates
all its capabilities including gig searching, proposal generation, code review,
and debugging functionality.

Installation:
    pip install mcp pydantic python-dotenv

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

class FreelanceMCPClient:
    """Main client class for interacting with the Freelance MCP Server"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.server_params = StdioServerParameters(
            command="python",
            args=["freelance_server.py", "stdio"],  # Run server in stdio mode
            env=dict(os.environ)  # Pass current environment including GROQ_API_KEY
        )
    
    async def connect(self):
        """Connect to the MCP server"""
        print("🚀 Connecting to Freelance Gig Aggregator MCP Server...")
        
        self.read, self.write = await stdio_client(self.server_params).__aenter__()
        self.session = await ClientSession(self.read, self.write).__aenter__()
        
        # Initialize the connection
        await self.session.initialize()
        print("✅ Connected successfully!")
        
        # List server capabilities
        await self._show_server_capabilities()
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        await self.write.__aexit__(None, None, None)
        await self.read.__aexit__(None, None, None)
    
    async def _show_server_capabilities(self):
        """Display available tools and resources"""
        print("\n📋 Available Tools:")
        tools = await self.session.list_tools()
        for tool in tools.tools:
            print(f"  • {tool.name}: {tool.description}")
        
        print("\n📚 Available Resources:")
        resources = await self.session.list_resources()
        for resource in resources.resources:
            print(f"  • {resource.uri}")
        
        # Check for resource templates
        try:
            templates = await self.session.list_resource_templates()
            if templates.resourceTemplates:
                print("\n📝 Resource Templates:")
                for template in templates.resourceTemplates:
                    print(f"  • {template.uriTemplate}")
        except Exception:
            pass  # Resource templates might not be supported
    
    async def demo_gig_search(self):
        """Demonstrate gig searching functionality"""
        print("\n" + "="*60)
        print("🔍 DEMO: Searching for Web Development Gigs")
        print("="*60)
        
        try:
            result = await self.session.call_tool("search_gigs", {
                "skills": ["JavaScript", "React", "Node.js", "TypeScript"],
                "max_budget": 1000,
                "project_type": "fixed_price",
                "platforms": ["upwork", "freelancer"]
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                gigs_data = result.structuredContent
                print(f"Found {gigs_data.get('total_found', 0)} matching gigs\n")
                
                for i, gig in enumerate(gigs_data.get('gigs', [])[:3], 1):
                    print(f"{i}. {gig['title']}")
                    print(f"   Platform: {gig['platform'].upper()}")
                    print(f"   Budget: {gig['budget']}")
                    print(f"   Match Score: {gig['match_score']}%")
                    print(f"   Skills: {', '.join(gig['skills_required'])}")
                    print(f"   Proposals: {gig['proposals_count']}")
                    print(f"   URL: {gig['url']}")
                    print()
            else:
                # Fallback to text content
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
        
        except Exception as e:
            print(f"❌ Error searching gigs: {e}")
    
    async def demo_profile_creation(self):
        """Demonstrate user profile creation"""
        print("\n" + "="*60)
        print("👤 DEMO: Creating User Profile")
        print("="*60)
        
        try:
            result = await self.session.call_tool("create_user_profile", {
                "name": "Alice Developer",
                "title": "Senior Full-Stack Developer",
                "skills_data": [
                    {"name": "JavaScript", "level": "expert", "years_experience": 6},
                    {"name": "React", "level": "expert", "years_experience": 5},
                    {"name": "Node.js", "level": "advanced", "years_experience": 4},
                    {"name": "TypeScript", "level": "advanced", "years_experience": 3},
                    {"name": "Python", "level": "intermediate", "years_experience": 2}
                ],
                "hourly_rate_min": 50,
                "hourly_rate_max": 100,
                "location": "San Francisco, CA",
                "languages": ["English", "Spanish", "French"]
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                profile_data = result.structuredContent
                print(f"✅ Profile created: {profile_data.get('profile_id', 'N/A')}")
                print(f"Message: {profile_data.get('message', '')}")
                
                summary = profile_data.get('profile_summary', {})
                print(f"\nProfile Summary:")
                print(f"  Name: {summary.get('name', 'N/A')}")
                print(f"  Title: {summary.get('title', 'N/A')}")
                print(f"  Skills: {summary.get('skills_count', 0)} skills")
                print(f"  Rate: {summary.get('rate_range', 'N/A')}")
                
                return profile_data.get('profile_id')
            else:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                        
        except Exception as e:
            print(f"❌ Error creating profile: {e}")
            return None
    
    async def demo_profile_analysis(self, profile_id: str = None):
        """Demonstrate profile fit analysis for a gig"""
        print("\n" + "="*60)
        print("📊 DEMO: Analyzing Profile Fit for Gig")
        print("="*60)
        
        try:
            result = await self.session.call_tool("analyze_profile_fit", {
                "profile_data": {
                    "skills": [
                        {"name": "JavaScript", "level": "expert"},
                        {"name": "React", "level": "expert"},
                        {"name": "TypeScript", "level": "advanced"},
                        {"name": "CSS", "level": "advanced"}
                    ],
                    "hourly_rate_min": 50,
                    "hourly_rate_max": 100,
                    "years_experience": 6,
                    "success_rate": 95
                },
                "gig_id": "upwork_001"  # React e-commerce gig from sample data
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                analysis = result.structuredContent
                print(f"Gig: {analysis.get('gig_title', 'N/A')}")
                print(f"Overall Score: {analysis.get('overall_score', 0)}%")
                print(f"Skill Match: {analysis.get('skill_match_score', 0)}%")
                print(f"Rate Compatibility: {analysis.get('rate_compatibility', 0)}%")
                print(f"Competition: {analysis.get('competition_level', 'N/A')}")
                print(f"Client Quality: {analysis.get('client_quality', 'N/A')}")
                print(f"\n💡 Recommendation: {analysis.get('recommendation', 'N/A')}")
                
                matching_skills = analysis.get('skill_matches', [])
                missing_skills = analysis.get('missing_skills', [])
                
                if matching_skills:
                    print(f"\n✅ Matching Skills: {', '.join(matching_skills)}")
                if missing_skills:
                    print(f"❌ Missing Skills: {', '.join(missing_skills)}")
                    
            else:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                        
        except Exception as e:
            print(f"❌ Error analyzing profile fit: {e}")
    
    async def demo_proposal_generation(self):
        """Demonstrate automated proposal generation using LLM"""
        print("\n" + "="*60)
        print("📝 DEMO: Generating Automated Proposal")
        print("="*60)
        
        try:
            result = await self.session.call_tool("generate_proposal", {
                "gig_id": "upwork_001",
                "user_profile": {
                    "name": "Alice Developer",
                    "title": "Senior Full-Stack Developer",
                    "skills": [
                        {"name": "React", "level": "expert"},
                        {"name": "JavaScript", "level": "expert"},
                        {"name": "TypeScript", "level": "advanced"},
                        {"name": "Redux", "level": "advanced"},
                        {"name": "CSS", "level": "advanced"}
                    ],
                    "years_experience": 6,
                    "success_rate": 95
                },
                "tone": "professional",
                "include_portfolio": True,
                "custom_message": "I have extensive experience with e-commerce payment integrations including Stripe, PayPal, and custom payment gateways."
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                proposal = result.structuredContent
                
                if 'error' in proposal:
                    print(f"❌ {proposal['error']}")
                    print("💡 Make sure GROQ_API_KEY is set in your .env file")
                    return
                
                print(f"Gig: {proposal.get('gig_title', 'N/A')}")
                print(f"Estimated Hours: {proposal.get('estimated_hours', 0)}")
                print(f"Proposed Rate: ${proposal.get('proposed_rate', 0)}/hr")
                print(f"Total Estimate: ${proposal.get('total_estimate', 0)}")
                print(f"Word Count: {proposal.get('word_count', 0)} words")
                print(f"\n📄 Generated Proposal:")
                print("-" * 50)
                print(proposal.get('proposal_text', 'No proposal generated'))
                print("-" * 50)
            else:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                        
        except Exception as e:
            print(f"❌ Error generating proposal: {e}")
    
    async def demo_rate_negotiation(self):
        """Demonstrate rate negotiation assistance"""
        print("\n" + "="*60)
        print("💰 DEMO: Rate Negotiation Strategy")
        print("="*60)
        
        try:
            result = await self.session.call_tool("negotiate_rate", {
                "current_rate": 40,
                "target_rate": 65,
                "project_complexity": "high",
                "justification_points": [
                    "6+ years experience with React and modern JavaScript",
                    "Proven track record with e-commerce platforms",
                    "Can deliver 20% faster due to reusable components",
                    "Includes comprehensive testing and documentation",
                    "Post-launch support and maintenance included"
                ]
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                negotiation = result.structuredContent
                
                if 'error' in negotiation:
                    print(f"❌ {negotiation['error']}")
                    print("💡 Make sure GROQ_API_KEY is set in your .env file")
                    return
                
                print(f"Current Rate: ${negotiation.get('current_rate', 0)}/hr")
                print(f"Target Rate: ${negotiation.get('target_rate', 0)}/hr")
                print(f"Increase: {negotiation.get('rate_increase_percent', 0)}%")
                print(f"Strategy: {negotiation.get('strategy', 'N/A')}")
                print(f"Success Probability: {negotiation.get('success_probability', 'N/A')}")
                
                print(f"\n📧 Negotiation Message:")
                print("-" * 50)
                print(negotiation.get('negotiation_message', 'No message generated'))
                print("-" * 50)
                
                alternatives = negotiation.get('alternative_approaches', [])
                if alternatives:
                    print("\n🔄 Alternative Approaches:")
                    for i, alt in enumerate(alternatives, 1):
                        print(f"  {i}. {alt}")
                        
            else:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                        
        except Exception as e:
            print(f"❌ Error generating negotiation strategy: {e}")
    
    async def demo_code_review(self):
        """Demonstrate code review functionality"""
        print("\n" + "="*60)
        print("🔍 DEMO: Code Review Tool")
        print("="*60)
        
        # Create a sample JavaScript file for review
        sample_code = """// Sample React component with intentional issues
var React = require('react');
var PropTypes = require('prop-types');

function PaymentForm(props) {
    var [amount, setAmount] = React.useState('');
    var [cardNumber, setCardNumber] = React.useState('');
    
    var handleSubmit = function(e) {
        e.preventDefault();
        if (amount == '') {
            alert('Amount is required');
            return;
        }
        
        // TODO: Validate card number
        props.onSubmit({amount: amount, cardNumber: cardNumber});
    };
    
    return React.createElement('form', {onSubmit: handleSubmit},
        React.createElement('input', {
            type: 'text',
            placeholder: 'Amount',
            value: amount,
            onChange: function(e) { setAmount(e.target.value) }
        }),
        React.createElement('input', {
            type: 'text', 
            placeholder: 'Card Number',
            value: cardNumber,
            onChange: function(e) { setCardNumber(e.target.value) }
        }),
        React.createElement('button', {type: 'submit'}, 'Submit Payment')
    );
}

module.exports = PaymentForm;
"""
        
        # Write sample file
        sample_file = Path("sample_payment_form.js")
        try:
            sample_file.write_text(sample_code)
            print(f"📄 Created sample file: {sample_file}")
            
            # Perform code review
            result = await self.session.call_tool("code_review", {
                "file_path": str(sample_file),
                "review_type": "general"
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                review = result.structuredContent
                
                if 'error' in review:
                    print(f"❌ {review['error']}")
                    return
                
                print(f"\n📊 Code Review Results:")
                print(f"File: {review.get('file_path', 'N/A')}")
                print(f"Language: {review.get('language', 'N/A')}")
                print(f"Overall Quality: {review.get('overall_quality', 'N/A')}")
                
                metrics = review.get('metrics', {})
                print(f"\n📈 Metrics:")
                print(f"  Total Lines: {metrics.get('total_lines', 0)}")
                print(f"  Code Lines: {metrics.get('code_lines', 0)}")
                print(f"  Comment Lines: {metrics.get('comment_lines', 0)}")
                print(f"  Comment Ratio: {metrics.get('comment_ratio', 0)}%")
                print(f"  Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 0)}")
                
                issues = review.get('issues', [])
                if issues:
                    print(f"\n❌ Issues Found:")
                    for i, issue in enumerate(issues, 1):
                        print(f"  {i}. {issue}")
                
                suggestions = review.get('suggestions', [])
                if suggestions:
                    print(f"\n💡 Suggestions:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")
            else:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                        
        except Exception as e:
            print(f"❌ Error during code review: {e}")
        finally:
            # Clean up sample file
            if sample_file.exists():
                sample_file.unlink()
                print(f"🗑️ Cleaned up sample file")
    
    async def demo_code_debug(self):
        """Demonstrate code debugging and fixing functionality"""
        print("\n" + "="*60)
        print("🐛 DEMO: Code Debug Tool")
        print("="*60)
        
        # Create a sample file with specific issues to fix
        buggy_code = """// Buggy JavaScript code
var userName = 'john_doe'
var userAge = 25
var isActive = true

function getUserInfo() {
    return {
        name: userName,
        age: userAge,
        active: isActive
    }
}

var result = getUserInfo()
console.log(result)

// More issues
if (userAge == '25') {
    console.log('User is 25 years old')
}

var numbers = [1, 2, 3, 4, 5]
for (var i = 0; i < numbers.length; i++) {
    setTimeout(function() {
        console.log(numbers[i])  // Closure issue
    }, 100)
}
"""
        
        debug_file = Path("buggy_code.js")
        try:
            debug_file.write_text(buggy_code)
            print(f"📄 Created buggy code file: {debug_file}")
            print(f"📜 Original code preview:")
            print("-" * 30)
            print(buggy_code[:200] + "..." if len(buggy_code) > 200 else buggy_code)
            print("-" * 30)
            
            # Debug the code
            result = await self.session.call_tool("code_debug", {
                "file_path": str(debug_file),
                "issue_description": "Replace var with let/const and fix equality operators",
                "fix_type": "auto",
                "backup": True
            })
            
            if hasattr(result, 'structuredContent') and result.structuredContent:
                debug_result = result.structuredContent
                
                if 'error' in debug_result:
                    print(f"❌ {debug_result['error']}")
                    return
                
                print(f"\n🔧 Debug Results:")
                print(f"File: {debug_result.get('file_path', 'N/A')}")
                print(f"Status: {debug_result.get('status', 'N/A')}")
                print(f"Changes Made: {debug_result.get('changes_made', False)}")
                print(f"Backup Created: {debug_result.get('backup_created', 'None')}")
                
                fixes = debug_result.get('fixes_applied', [])
                if fixes:
                    print(f"\n✅ Fixes Applied:")
                    for i, fix in enumerate(fixes, 1):
                        print(f"  {i}. {fix}")
                
                suggestions = debug_result.get('suggestions', [])
                if suggestions:
                    print(f"\n💡 Additional Suggestions:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")
                
                # Show the fixed code if changes were made
                if debug_result.get('changes_made') and debug_file.exists():
                    fixed_code = debug_file.read_text()
                    print(f"\n📜 Fixed code preview:")
                    print("-" * 30)
                    print(fixed_code[:300] + "..." if len(fixed_code) > 300 else fixed_code)
                    print("-" * 30)
                    
            else:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                        
        except Exception as e:
            print(f"❌ Error during code debugging: {e}")
        finally:
            # Clean up files
            if debug_file.exists():
                debug_file.unlink()
                print(f"🗑️ Cleaned up debug file")
            
            # Clean up backup files
            for backup_file in Path(".").glob("buggy_code.js.backup.*"):
                backup_file.unlink()
                print(f"🗑️ Cleaned up backup file: {backup_file}")
    
    async def demo_profile_optimization(self):
        """Demonstrate profile optimization recommendations"""
        print("\n" + "="*60)
        print("⚡ DEMO: Profile Optimization")
        print("="*60)
        
        # First create a profile to optimize
        profile_result = await self.session.call_tool("create_user_profile", {
            "name": "Bob Developer",
            "title": "Web Developer",
            "skills_data": [
                {"name": "HTML", "level": "advanced", "years_experience": 4},
                {"name": "CSS", "level": "intermediate", "years_experience": 3},
                {"name": "JavaScript", "level": "intermediate", "years_experience": 2},
                {"name": "jQuery", "level": "beginner", "years_experience": 1}
            ],
            "hourly_rate_min": 20,
            "hourly_rate_max": 35,
            "location": "Remote",
            "languages": ["English"]
        })
        
        if hasattr(profile_result, 'structuredContent') and profile_result.structuredContent:
            profile_id = profile_result.structuredContent.get('profile_id')
            
            if profile_id:
                try:
                    # Optimize the profile
                    result = await self.session.call_tool("optimize_profile", {
                        "profile_id": profile_id,
                        "target_niche": "Modern JavaScript Development"
                    })
                    
                    if hasattr(result, 'structuredContent') and result.structuredContent:
                        optimization = result.structuredContent
                        
                        if 'error' in optimization:
                            print(f"❌ {optimization['error']}")
                            print("💡 Make sure GROQ_API_KEY is set in your .env file")
                            return
                        
                        current = optimization.get('current_profile', {})
                        print(f"📋 Current Profile:")
                        print(f"  Title: {current.get('title', 'N/A')}")
                        print(f"  Skills: {current.get('skills_count', 0)} skills")
                        print(f"  Rate: {current.get('rate_range', 'N/A')}")
                        print(f"  Success Rate: {current.get('success_rate', 'N/A')}")
                        
                        print(f"\n🚀 Optimization Recommendations:")
                        print("-" * 50)
                        print(optimization.get('recommendations', 'No recommendations generated'))
                        print("-" * 50)
                        
                        actions = optimization.get('action_items', [])
                        if actions:
                            print(f"\n✅ Action Items:")
                            for i, action in enumerate(actions, 1):
                                print(f"  {i}. {action}")
                        
                        insights = optimization.get('market_insights', {})
                        if insights:
                            print(f"\n📊 Market Insights:")
                            print(f"  Hot Skills: {', '.join(insights.get('hot_skills', []))}")
                            print(f"  Average Rate: {insights.get('average_rate', 'N/A')}")
                            print(f"  Success Rate Target: {insights.get('success_rate_target', 'N/A')}")
                            
                        next_steps = optimization.get('next_steps', [])
                        if next_steps:
                            print(f"\n🎯 Next Steps:")
                            for i, step in enumerate(next_steps, 1):
                                print(f"  {i}. {step}")
                    else:
                        for content in result.content:
                            if isinstance(content, types.TextContent):
                                print(content.text)
                                
                except Exception as e:
                    print(f"❌ Error optimizing profile: {e}")
    
    async def demo_resources(self):
        """Demonstrate accessing server resources"""
        print("\n" + "="*60)
        print("📚 DEMO: Accessing Server Resources")
        print("="*60)
        
        try:
            # Get market trends
            trends = await self.session.read_resource(AnyUrl("freelance://market-trends"))
            if trends.contents:
                content = trends.contents[0]
                if isinstance(content, types.TextContent):
                    trends_data = json.loads(content.text)
                    print("📈 Market Trends:")
                    print(f"Hot Skills: {', '.join(trends_data.get('hot_skills', []))}")
                    
                    rates = trends_data.get('average_rates', {})
                    print(f"\n💰 Average Rates:")
                    for skill, rate in rates.items():
                        print(f"  {skill}: {rate}")
                    
                    tips = trends_data.get('tips', [])
                    if tips:
                        print(f"\n💡 Tips:")
                        for i, tip in enumerate(tips, 1):
                            print(f"  {i}. {tip}")
            
            print(f"\n" + "-"*40)
            
            # Get platform gigs
            upwork_gigs = await self.session.read_resource(AnyUrl("freelance://gigs/upwork"))
            if upwork_gigs.contents:
                content = upwork_gigs.contents[0]
                if isinstance(content, types.TextContent):
                    gigs_data = json.loads(content.text)
                    print("🎯 Upwork Gigs:")
                    for gig in gigs_data[:2]:  # Show first 2
                        print(f"  • {gig['title']} - {gig['budget']}")
                        print(f"    Skills: {', '.join(gig['skills'])}")
                        print(f"    Proposals: {gig['proposals']}")
                        
        except Exception as e:
            print(f"❌ Error accessing resources: {e}")
    
    async def run_interactive_demo(self):
        """Run an interactive demo of all features"""
        print("🎉 Welcome to the Freelance Gig Aggregator MCP Client Demo!")
        print("This demo will showcase all the server capabilities.\n")
        
        try:
            await self.connect()
            
            # Run all demos
            await self.demo_gig_search()
            await self.demo_profile_creation()
            await self.demo_profile_analysis()
            await self.demo_proposal_generation()
            await self.demo_rate_negotiation()
            await self.demo_code_review()
            await self.demo_code_debug()
            await self.demo_profile_optimization()
            await self.demo_resources()
            
            print("\n" + "="*60)
            print("🎊 Demo Complete!")
            print("="*60)
            print("All features have been demonstrated successfully.")
            print("You can now integrate this MCP server with Claude Desktop")
            print("or other MCP-compatible clients.")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.disconnect()
    
    async def interactive_mode(self):
        """Run in interactive mode for manual testing"""
        print("🎮 Interactive Mode - Type 'help' for available commands")
        
        await self.connect()
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'help':
                    print("Available commands:")
                    print("  search - Search for gigs")
                    print("  profile - Create user profile")
                    print("  analyze - Analyze profile fit")
                    print("  proposal - Generate proposal")
                    print("  negotiate - Rate negotiation")
                    print("  review - Code review")
                    print("  debug - Code debugging")
                    print("  optimize - Profile optimization")
                    print("  resources - Show resources")
                    print("  demo - Run full demo")
                    print("  quit - Exit")
                    
                elif command == 'search':
                    await self.demo_gig_search()
                elif command == 'profile':
                    await self.demo_profile_creation()
                elif command == 'analyze':
                    await self.demo_profile_analysis()
                elif command == 'proposal':
                    await self.demo_proposal_generation()
                elif command == 'negotiate':
                    await self.demo_rate_negotiation()
                elif command == 'review':
                    await self.demo_code_review()
                elif command == 'debug':
                    await self.demo_code_debug()
                elif command == 'optimize':
                    await self.demo_profile_optimization()
                elif command == 'resources':
                    await self.demo_resources()
                elif command == 'demo':
                    await self.run_interactive_demo()
                    break
                elif command in ['quit', 'exit', 'q']:
                    break
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        await self.disconnect()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Freelance Gig Aggregator MCP Client")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo",
                       help="Run mode: demo (automated) or interactive (manual)")
    parser.add_argument("--check-env", action="store_true",
                       help="Check environment setup")
    
    args = parser.parse_args()
    
    if args.check_env:
        check_environment()
        return
    
    client = FreelanceMCPClient()
    
    if args.mode == "demo":
        await client.run_interactive_demo()
    else:
        await client.interactive_mode()


def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking Environment Setup...")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+)")
    
    # Check required packages
    required_packages = ["mcp", "pydantic", "python-dotenv"]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (install with: pip install {package})")
    
    # Check for server file
    server_file = Path("freelance_server.py")
    if server_file.exists():
        print(f"✅ freelance_server.py found")
    else:
        print(f"❌ freelance_server.py not found in current directory")
    
    # Check for .env file and GROQ_API_KEY
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env file found")
        load_dotenv()
        if os.getenv("GROQ_API_KEY"):
            print(f"✅ GROQ_API_KEY configured")
        else:
            print(f"⚠️  GROQ_API_KEY not set (LLM features will not work)")
    else:
        print(f"⚠️  .env file not found (create one with GROQ_API_KEY)")
    
    print("-" * 40)
    print("Setup complete! Run with: python freelance_client.py")


def create_sample_env():
    """Create a sample .env file"""
    env_content = """# Freelance Gig Aggregator MCP Server Environment Variables

# Required for LLM-powered features (get from https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here

# Optional: Real platform API keys for live data integration
# UPWORK_API_KEY=your_upwork_api_key
# FIVERR_API_KEY=your_fiverr_api_key
# FREELANCER_API_KEY=your_freelancer_api_key

# Server Configuration (optional)
# SERVER_DEBUG=true
# SERVER_PORT=8000
"""
    
    env_file = Path(".env.sample")
    env_file.write_text(env_content)
    print(f"📄 Sample environment file created: {env_file}")
    print("Copy it to .env and add your actual API keys")


if __name__ == "__main__":
    # Handle special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create-env":
            create_sample_env()
            sys.exit(0)
        elif sys.argv[1] == "--check-deps":
            check_environment()
            sys.exit(0)
    
    # Run async main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)