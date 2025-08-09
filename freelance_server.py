"""
Freelance Gig Aggregator MCP Server

A comprehensive MCP server for aggregating freelance opportunities across multiple platforms,
matching user skills with available gigs, and automating proposal generation with rate negotiation.

Features:
- Multi-platform gig aggregation (Upwork, Fiverr, Freelancer, etc.)
- Skill-based matching and scoring
- Automated proposal generation with Langchain ChatGroq
- Rate negotiation assistance
- Code review and debugging tools
- Profile optimization recommendations

Installation:
    pip install mcp langchain-groq pydantic python-dotenv

Usage:
    python freelance_server.py
    or
    uv run mcp dev freelance_server.py
"""

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from mcp.server.fastmcp import Context, FastMCP

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Freelance Gig Aggregator", instructions="""
A comprehensive freelance platform aggregator that helps users:
- Find and match relevant gigs across multiple platforms
- Generate personalized proposals and applications
- Negotiate rates and terms
- Review and debug code for projects
- Optimize freelance profiles and strategies
""")

# Initialize Langchain ChatGroq
try:
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        model_name="mixtral-8x7b-32768",
        temperature=0.7
    )
except Exception as e:
    print(f"Warning: Could not initialize ChatGroq: {e}")
    llm = None


# Data Models
class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProjectType(str, Enum):
    FIXED_PRICE = "fixed_price"
    HOURLY = "hourly"
    RETAINER = "retainer"
    CONTEST = "contest"


class Platform(str, Enum):
    UPWORK = "upwork"
    FIVERR = "fiverr"
    FREELANCER = "freelancer"
    TOPTAL = "toptal"
    GURU = "guru"
    PEOPLEPERHOUR = "peopleperhour"


@dataclass
class Skill:
    name: str
    level: SkillLevel
    years_experience: int
    certifications: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    name: str
    title: str
    skills: List[Skill]
    hourly_rate_min: float
    hourly_rate_max: float
    location: str
    timezone: str
    languages: List[str]
    portfolio_urls: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    years_experience: int = 0
    success_rate: float = 0.0
    total_earnings: float = 0.0


@dataclass
class Gig:
    id: str
    platform: Platform
    title: str
    description: str
    budget_min: Optional[float]
    budget_max: Optional[float]
    hourly_rate: Optional[float]
    project_type: ProjectType
    skills_required: List[str]
    client_rating: float
    client_reviews: int
    posted_date: datetime
    deadline: Optional[datetime]
    proposals_count: int
    url: str
    location: str = ""
    remote_ok: bool = True


@dataclass
class GigMatch:
    gig: Gig
    match_score: float
    skill_matches: List[str]
    missing_skills: List[str]
    rate_compatibility: float
    recommendation: str


class ProposalRequest(BaseModel):
    gig_id: str
    user_profile: Dict[str, Any]
    tone: str = Field(default="professional", description="Tone: professional, friendly, confident")
    include_portfolio: bool = Field(default=True)
    custom_message: str = Field(default="", description="Additional custom message to include")


class RateNegotiation(BaseModel):
    current_rate: float
    target_rate: float
    justification_points: List[str]
    project_complexity: str = Field(default="medium", description="low, medium, high")


# In-memory storage for demo purposes
class FreelanceDatabase:
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.gigs: Dict[str, Gig] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample gigs for demonstration"""
        sample_gigs = [
            Gig(
                id="upwork_001",
                platform=Platform.UPWORK,
                title="React Developer Needed for E-commerce Site",
                description="Looking for an experienced React developer to build a modern e-commerce platform. Must have experience with Redux, TypeScript, and payment integration.",
                budget_min=800.0,
                budget_max=1500.0,
                hourly_rate=None,
                project_type=ProjectType.FIXED_PRICE,
                skills_required=["React", "TypeScript", "Redux", "JavaScript", "CSS"],
                client_rating=4.8,
                client_reviews=23,
                posted_date=datetime.now() - timedelta(hours=2),
                deadline=datetime.now() + timedelta(days=30),
                proposals_count=12,
                url="https://upwork.com/job/001",
                remote_ok=True
            ),
            Gig(
                id="fiverr_002",
                platform=Platform.FIVERR,
                title="Python Automation Script Development",
                description="Need a Python script to automate data processing tasks. Should work with CSV files and generate reports.",
                budget_min=200.0,
                budget_max=400.0,
                hourly_rate=25.0,
                project_type=ProjectType.FIXED_PRICE,
                skills_required=["Python", "Data Processing", "CSV", "Automation"],
                client_rating=4.5,
                client_reviews=8,
                posted_date=datetime.now() - timedelta(hours=5),
                deadline=datetime.now() + timedelta(days=14),
                proposals_count=7,
                url="https://fiverr.com/gig/002",
                remote_ok=True
            ),
            Gig(
                id="freelancer_003",
                platform=Platform.FREELANCER,
                title="WordPress Website Debugging and Optimization",
                description="Existing WordPress site needs debugging and performance optimization. Experience with PHP, MySQL required.",
                budget_min=300.0,
                budget_max=600.0,
                hourly_rate=30.0,
                project_type=ProjectType.HOURLY,
                skills_required=["WordPress", "PHP", "MySQL", "Performance Optimization"],
                client_rating=4.2,
                client_reviews=15,
                posted_date=datetime.now() - timedelta(hours=8),
                deadline=datetime.now() + timedelta(days=21),
                proposals_count=18,
                url="https://freelancer.com/project/003",
                remote_ok=True
            )
        ]
        
        for gig in sample_gigs:
            self.gigs[gig.id] = gig


# Initialize database
db = FreelanceDatabase()


# Helper Functions
def calculate_match_score(user_skills: List[str], required_skills: List[str]) -> float:
    """Calculate skill match score between user and gig requirements"""
    if not required_skills:
        return 0.5
    
    user_skills_lower = [skill.lower() for skill in user_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    
    matches = sum(1 for skill in required_skills_lower if skill in user_skills_lower)
    return matches / len(required_skills_lower)


def check_rate_compatibility(user_min: float, user_max: float, gig_budget_min: Optional[float], 
                           gig_budget_max: Optional[float], hourly_rate: Optional[float]) -> float:
    """Check rate compatibility between user expectations and gig budget"""
    if hourly_rate:
        if user_min <= hourly_rate <= user_max:
            return 1.0
        elif hourly_rate < user_min:
            return max(0.0, 1.0 - (user_min - hourly_rate) / user_min)
        else:
            return 0.7  # Higher than expected, but still acceptable
    
    if gig_budget_max:
        # Assume 40 hours for fixed price projects
        estimated_hourly = gig_budget_max / 40
        if user_min <= estimated_hourly <= user_max:
            return 1.0
        elif estimated_hourly < user_min:
            return max(0.0, 1.0 - (user_min - estimated_hourly) / user_min)
        else:
            return 0.8
    
    return 0.5  # Unknown budget


# Resources
@mcp.resource("freelance://profile/{profile_id}")
def get_user_profile(profile_id: str) -> str:
    """Get user profile information"""
    profile = db.user_profiles.get(profile_id)
    if not profile:
        return f"Profile {profile_id} not found"
    
    return json.dumps({
        "name": profile.name,
        "title": profile.title,
        "skills": [{"name": s.name, "level": s.level, "experience": s.years_experience} 
                  for s in profile.skills],
        "rate_range": f"${profile.hourly_rate_min}-${profile.hourly_rate_max}/hr",
        "location": profile.location,
        "success_rate": f"{profile.success_rate}%",
        "total_earnings": f"${profile.total_earnings}"
    }, indent=2)


@mcp.resource("freelance://gigs/{platform}")
def get_platform_gigs(platform: str) -> str:
    """Get gigs from a specific platform"""
    platform_gigs = [gig for gig in db.gigs.values() 
                    if gig.platform.value == platform.lower()]
    
    gig_summaries = []
    for gig in platform_gigs:
        gig_summaries.append({
            "id": gig.id,
            "title": gig.title,
            "budget": f"${gig.budget_min}-${gig.budget_max}" if gig.budget_min else f"${gig.hourly_rate}/hr",
            "skills": gig.skills_required,
            "proposals": gig.proposals_count,
            "posted": gig.posted_date.strftime("%Y-%m-%d %H:%M")
        })
    
    return json.dumps(gig_summaries, indent=2)


@mcp.resource("freelance://market-trends")
def get_market_trends() -> str:
    """Get current freelance market trends and insights"""
    trends = {
        "hot_skills": ["AI/ML", "React", "Python", "Node.js", "TypeScript"],
        "average_rates": {
            "Web Development": "$25-75/hr",
            "Mobile Development": "$30-80/hr",
            "Data Science": "$40-100/hr",
            "AI/ML": "$50-120/hr",
            "DevOps": "$35-90/hr"
        },
        "platform_competition": {
            "Upwork": "High competition, premium clients",
            "Fiverr": "Service-based, competitive pricing",
            "Freelancer": "Mixed budget range, global",
            "Toptal": "Elite developers, high rates"
        },
        "tips": [
            "Specialize in 2-3 complementary skills",
            "Build a strong portfolio with case studies",
            "Maintain 95%+ success rate",
            "Respond to invitations within 24 hours"
        ]
    }
    
    return json.dumps(trends, indent=2)


# Tools
@mcp.tool()
def search_gigs(skills: List[str], max_budget: Optional[float] = None, 
                min_budget: Optional[float] = None, project_type: Optional[str] = None,
                platforms: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for freelance gigs based on skills and criteria
    
    Args:
        skills: List of skills to match against
        max_budget: Maximum budget/rate to filter by
        min_budget: Minimum budget/rate to filter by
        project_type: Type of project (fixed_price, hourly, retainer, contest)
        platforms: List of platforms to search (upwork, fiverr, freelancer, etc.)
    """
    
    filtered_gigs = []
    
    for gig in db.gigs.values():
        # Platform filter
        if platforms and gig.platform.value not in [p.lower() for p in platforms]:
            continue
            
        # Project type filter
        if project_type and gig.project_type.value != project_type.lower():
            continue
            
        # Budget filters
        if max_budget:
            gig_max = gig.budget_max or gig.hourly_rate
            if gig_max and gig_max > max_budget:
                continue
                
        if min_budget:
            gig_min = gig.budget_min or gig.hourly_rate
            if gig_min and gig_min < min_budget:
                continue
        
        # Skill matching
        skill_match_score = calculate_match_score(skills, gig.skills_required)
        if skill_match_score > 0:  # At least some skill match
            filtered_gigs.append({
                "gig": gig,
                "match_score": skill_match_score
            })
    
    # Sort by match score
    filtered_gigs.sort(key=lambda x: x["match_score"], reverse=True)
    
    results = []
    for item in filtered_gigs[:10]:  # Top 10 matches
        gig = item["gig"]
        results.append({
            "id": gig.id,
            "platform": gig.platform.value,
            "title": gig.title,
            "description": gig.description[:200] + "..." if len(gig.description) > 200 else gig.description,
            "budget": f"${gig.budget_min}-${gig.budget_max}" if gig.budget_min else f"${gig.hourly_rate}/hr",
            "skills_required": gig.skills_required,
            "match_score": round(item["match_score"] * 100, 1),
            "proposals_count": gig.proposals_count,
            "client_rating": gig.client_rating,
            "posted_date": gig.posted_date.strftime("%Y-%m-%d %H:%M"),
            "url": gig.url
        })
    
    return {
        "total_found": len(results),
        "gigs": results,
        "search_criteria": {
            "skills": skills,
            "max_budget": max_budget,
            "min_budget": min_budget,
            "project_type": project_type,
            "platforms": platforms
        }
    }


@mcp.tool()
def analyze_profile_fit(profile_data: Dict[str, Any], gig_id: str) -> Dict[str, Any]:
    """
    Analyze how well a user profile fits a specific gig
    
    Args:
        profile_data: User profile information
        gig_id: ID of the gig to analyze fit for
    """
    
    gig = db.gigs.get(gig_id)
    if not gig:
        return {"error": f"Gig {gig_id} not found"}
    
    user_skills = [skill["name"] for skill in profile_data.get("skills", [])]
    skill_match_score = calculate_match_score(user_skills, gig.skills_required)
    
    # Calculate rate compatibility
    rate_compatibility = check_rate_compatibility(
        profile_data.get("hourly_rate_min", 20),
        profile_data.get("hourly_rate_max", 100),
        gig.budget_min,
        gig.budget_max,
        gig.hourly_rate
    )
    
    # Find matching and missing skills
    user_skills_lower = [s.lower() for s in user_skills]
    required_skills_lower = [s.lower() for s in gig.skills_required]
    
    skill_matches = [skill for skill in gig.skills_required 
                    if skill.lower() in user_skills_lower]
    missing_skills = [skill for skill in gig.skills_required 
                     if skill.lower() not in user_skills_lower]
    
    # Generate recommendation
    overall_score = (skill_match_score + rate_compatibility) / 2
    
    if overall_score >= 0.8:
        recommendation = "Excellent match! Apply immediately."
    elif overall_score >= 0.6:
        recommendation = "Good match. Consider applying with emphasis on transferable skills."
    elif overall_score >= 0.4:
        recommendation = "Moderate match. May require additional learning or lower rate."
    else:
        recommendation = "Poor match. Consider focusing on better-aligned opportunities."
    
    return {
        "gig_id": gig_id,
        "gig_title": gig.title,
        "overall_score": round(overall_score * 100, 1),
        "skill_match_score": round(skill_match_score * 100, 1),
        "rate_compatibility": round(rate_compatibility * 100, 1),
        "skill_matches": skill_matches,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "competition_level": "High" if gig.proposals_count > 15 else "Medium" if gig.proposals_count > 5 else "Low",
        "client_quality": "Excellent" if gig.client_rating > 4.5 else "Good" if gig.client_rating > 4.0 else "Average"
    }


@mcp.tool()
async def generate_proposal(gig_id: str, user_profile: Dict[str, Any], 
                          tone: str = "professional", include_portfolio: bool = True,
                          custom_message: str = "", ctx: Context = None) -> Dict[str, Any]:
    """
    Generate a personalized proposal for a specific gig using Langchain ChatGroq
    
    Args:
        gig_id: ID of the gig to generate proposal for
        user_profile: User profile information
        tone: Tone of the proposal (professional, friendly, confident)
        include_portfolio: Whether to include portfolio references
        custom_message: Additional custom message to include
    """
    
    if not llm:
        return {"error": "ChatGroq not initialized. Please set GROQ_API_KEY environment variable."}
    
    gig = db.gigs.get(gig_id)
    if not gig:
        return {"error": f"Gig {gig_id} not found"}
    
    if ctx:
        await ctx.info(f"Generating proposal for: {gig.title}")
    
    # Prepare context for LLM
    context = f"""
    Generate a compelling freelance proposal for the following gig:
    
    GIG DETAILS:
    Title: {gig.title}
    Description: {gig.description}
    Budget: ${gig.budget_min}-${gig.budget_max} or ${gig.hourly_rate}/hr
    Skills Required: {', '.join(gig.skills_required)}
    Platform: {gig.platform.value}
    
    USER PROFILE:
    Name: {user_profile.get('name', 'Freelancer')}
    Title: {user_profile.get('title', 'Professional Developer')}
    Skills: {', '.join([skill['name'] for skill in user_profile.get('skills', [])])}
    Experience: {user_profile.get('years_experience', 3)} years
    Success Rate: {user_profile.get('success_rate', 95)}%
    
    REQUIREMENTS:
    - Tone: {tone}
    - Include portfolio references: {include_portfolio}
    - Custom message: {custom_message}
    
    Generate a professional proposal that:
    1. Shows understanding of the project requirements
    2. Highlights relevant skills and experience
    3. Provides a clear project approach
    4. Includes timeline and deliverables
    5. Ends with a call to action
    
    Keep it concise (200-400 words) and compelling.
    """
    
    try:
        response = llm.invoke(context)
        proposal_text = response.content
        
        # Generate additional metadata
        estimated_hours = 20 if gig.project_type == ProjectType.FIXED_PRICE else 40
        proposed_rate = user_profile.get('hourly_rate_min', 30)
        
        return {
            "gig_id": gig_id,
            "gig_title": gig.title,
            "proposal_text": proposal_text,
            "estimated_hours": estimated_hours,
            "proposed_rate": proposed_rate,
            "total_estimate": estimated_hours * proposed_rate,
            "generated_at": datetime.now().isoformat(),
            "tone": tone,
            "word_count": len(proposal_text.split())
        }
        
    except Exception as e:
        return {"error": f"Failed to generate proposal: {str(e)}"}


@mcp.tool()
async def negotiate_rate(current_rate: float, target_rate: float, 
                        project_complexity: str = "medium",
                        justification_points: List[str] = None,
                        ctx: Context = None) -> Dict[str, Any]:
    """
    Generate rate negotiation strategy and message using Langchain ChatGroq
    
    Args:
        current_rate: Current offered rate
        target_rate: Desired rate
        project_complexity: Complexity level (low, medium, high)
        justification_points: List of points to justify higher rate
    """
    
    if not llm:
        return {"error": "ChatGroq not initialized. Please set GROQ_API_KEY environment variable."}
    
    if ctx:
        await ctx.info(f"Preparing rate negotiation: ${current_rate} -> ${target_rate}")
    
    if not justification_points:
        justification_points = [
            "Extensive experience in required technologies",
            "Strong track record of successful project delivery",
            "Additional value through code review and optimization"
        ]
    
    rate_increase = ((target_rate - current_rate) / current_rate) * 100
    
    context = f"""
    Generate a professional rate negotiation message for a freelance project:
    
    SITUATION:
    - Current offered rate: ${current_rate}/hr
    - Target rate: ${target_rate}/hr
    - Rate increase requested: {rate_increase:.1f}%
    - Project complexity: {project_complexity}
    
    JUSTIFICATION POINTS:
    {chr(10).join([f"- {point}" for point in justification_points])}
    
    Generate a diplomatic negotiation message that:
    1. Expresses appreciation for the opportunity
    2. Presents the rate increase professionally
    3. Provides clear justification based on value delivered
    4. Offers flexibility and alternatives if needed
    5. Maintains positive relationship tone
    
    Keep it concise and professional (150-300 words).
    """
    
    try:
        response = llm.invoke(context)
        negotiation_message = response.content
        
        # Calculate negotiation strategy
        if rate_increase <= 20:
            strategy = "Direct approach - reasonable increase"
            success_probability = "High (70-80%)"
        elif rate_increase <= 50:
            strategy = "Value-focused approach - emphasize unique skills"
            success_probability = "Medium (40-60%)"
        else:
            strategy = "Gradual approach - suggest trial period or bonus structure"
            success_probability = "Low (20-40%)"
        
        return {
            "current_rate": current_rate,
            "target_rate": target_rate,
            "rate_increase_percent": round(rate_increase, 1),
            "negotiation_message": negotiation_message,
            "strategy": strategy,
            "success_probability": success_probability,
            "alternative_approaches": [
                f"Offer trial rate of ${(current_rate + target_rate) / 2:.2f}/hr for first 10 hours",
                f"Suggest performance bonus structure",
                f"Propose higher rate for rush deliveries or after-hours work"
            ],
            "justification_points": justification_points
        }
        
    except Exception as e:
        return {"error": f"Failed to generate negotiation strategy: {str(e)}"}


@mcp.tool()
def create_user_profile(name: str, title: str, skills_data: List[Dict[str, Any]],
                       hourly_rate_min: float, hourly_rate_max: float,
                       location: str, languages: List[str]) -> Dict[str, Any]:
    """
    Create a new user profile
    
    Args:
        name: Full name
        title: Professional title
        skills_data: List of skills with levels and experience
        hourly_rate_min: Minimum hourly rate
        hourly_rate_max: Maximum hourly rate
        location: Location/timezone
        languages: List of languages spoken
    """
    
    skills = []
    for skill_data in skills_data:
        skill = Skill(
            name=skill_data["name"],
            level=SkillLevel(skill_data.get("level", "intermediate")),
            years_experience=skill_data.get("years_experience", 1),
            certifications=skill_data.get("certifications", [])
        )
        skills.append(skill)
    
    profile = UserProfile(
        name=name,
        title=title,
        skills=skills,
        hourly_rate_min=hourly_rate_min,
        hourly_rate_max=hourly_rate_max,
        location=location,
        timezone=location,  # Simplified
        languages=languages
    )
    
    profile_id = f"user_{len(db.user_profiles) + 1}"
    db.user_profiles[profile_id] = profile
    
    return {
        "profile_id": profile_id,
        "message": f"Profile created successfully for {name}",
        "profile_summary": {
            "name": name,
            "title": title,
            "skills_count": len(skills),
            "rate_range": f"${hourly_rate_min}-${hourly_rate_max}/hr"
        }
    }


@mcp.tool()
def code_review(file_path: str, review_type: str = "general") -> Dict[str, Any]:
    """
    Review code file and provide feedback using LLM analysis
    
    Args:
        file_path: Path to the code file to review
        review_type: Type of review (general, security, performance, style)
    """
    
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {"error": f"File {file_path} not found"}
        
        # Read file content
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Determine file type
        file_extension = file_path_obj.suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        
        language = language_map.get(file_extension, 'Unknown')
        
        # Perform basic code analysis
        lines = code_content.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*'))])
        
        # Basic complexity analysis
        cyclomatic_complexity = len(re.findall(r'\b(if|while|for|switch|try|catch|elif|else if)\b', code_content))
        
        # Check for common issues
        issues = []
        suggestions = []
        
        # Language-specific checks
        if language == 'Python':
            if 'import *' in code_content:
                issues.append("Wildcard imports found - use specific imports")
            if len(re.findall(r'def \w+\([^)]*\):', code_content)) > 0:
                # Check for docstrings
                functions_without_docs = len(re.findall(r'def \w+\([^)]*\):\s*\n\s*(?!""")', code_content))
                if functions_without_docs > 0:
                    suggestions.append("Add docstrings to functions for better documentation")
        
        elif language == 'JavaScript':
            if 'var ' in code_content:
                suggestions.append("Consider using 'let' or 'const' instead of 'var'")
            if '==' in code_content and '===' not in code_content:
                suggestions.append("Use strict equality (===) instead of loose equality (==)")
        
        # General checks
        if cyclomatic_complexity > 10:
            issues.append(f"High cyclomatic complexity ({cyclomatic_complexity}) - consider refactoring")
        
        if total_lines > 500:
            suggestions.append("Large file detected - consider splitting into smaller modules")
        
        if comment_lines / non_empty_lines < 0.1:
            suggestions.append("Low comment ratio - consider adding more documentation")
        
        return {
            "file_path": file_path,
            "language": language,
            "review_type": review_type,
            "metrics": {
                "total_lines": total_lines,
                "code_lines": non_empty_lines,
                "comment_lines": comment_lines,
                "cyclomatic_complexity": cyclomatic_complexity,
                "comment_ratio": round((comment_lines / non_empty_lines) * 100, 1) if non_empty_lines > 0 else 0
            },
            "issues": issues,
            "suggestions": suggestions,
            "overall_quality": "Good" if len(issues) == 0 else "Needs Improvement" if len(issues) < 3 else "Poor",
            "reviewed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to review code: {str(e)}"}


@mcp.tool()
def code_debug(file_path: str, issue_description: str, fix_type: str = "auto",
               backup: bool = True) -> Dict[str, Any]:
    """
    Debug and fix issues in a code file
    
    Args:
        file_path: Path to the code file to debug
        issue_description: Description of the issue to fix
        fix_type: Type of fix (auto, manual, suggest)
        backup: Whether to create a backup before making changes
    """
    
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {"error": f"File {file_path} not found"}
        
        # Read original content
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup if requested
        backup_path = None
        if backup:
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Determine file type and common issues
        file_extension = file_path_obj.suffix.lower()
        fixes_applied = []
        modified_content = original_content
        
        # Language-specific debugging
        if file_extension == '.py':
            # Fix Python-specific issues
            
            # Fix import issues
            if "import *" in issue_description.lower() or "wildcard" in issue_description.lower():
                # This is a simplified fix - in practice, you'd need more sophisticated parsing
                modified_content = re.sub(r'from\s+\w+\s+import\s+\*', 
                                        '# TODO: Replace wildcard import with specific imports', 
                                        modified_content)
                fixes_applied.append("Marked wildcard imports for replacement")
            
            # Fix indentation issues
            if "indentation" in issue_description.lower():
                lines = modified_content.split('\n')
                fixed_lines = []
                for line in lines:
                    # Convert tabs to spaces
                    if '\t' in line:
                        fixed_lines.append(line.expandtabs(4))
                        if line not in fixes_applied:
                            fixes_applied.append("Converted tabs to spaces")
                    else:
                        fixed_lines.append(line)
                modified_content = '\n'.join(fixed_lines)
            
            # Add missing docstrings
            if "docstring" in issue_description.lower() or "documentation" in issue_description.lower():
                # Add basic docstring to functions without them
                pattern = r'(def\s+\w+\([^)]*\):\s*\n)(\s*)((?!"""|\'\'\')\S)'
                def add_docstring(match):
                    function_def = match.group(1)
                    indent = match.group(2)
                    next_line = match.group(3)
                    docstring = f'{indent}"""TODO: Add function description"""\n{indent}'
                    return function_def + docstring + next_line
                
                modified_content = re.sub(pattern, add_docstring, modified_content)
                fixes_applied.append("Added placeholder docstrings to functions")
        
        elif file_extension == '.js':
            # Fix JavaScript-specific issues
            
            # Replace var with let/const
            if "var" in issue_description.lower():
                modified_content = re.sub(r'\bvar\b', 'let', modified_content)
                fixes_applied.append("Replaced 'var' with 'let'")
            
            # Fix equality operators
            if "equality" in issue_description.lower() or "==" in issue_description:
                modified_content = re.sub(r'(?<!!)==(?!=)', '===', modified_content)
                modified_content = re.sub(r'!=(?!=)', '!==', modified_content)
                fixes_applied.append("Replaced loose equality with strict equality")
            
            # Add missing semicolons (basic detection)
            if "semicolon" in issue_description.lower():
                lines = modified_content.split('\n')
                fixed_lines = []
                for line in lines:
                    stripped = line.rstrip()
                    if (stripped and 
                        not stripped.endswith((';', '{', '}', ':', ',')) and
                        not stripped.startswith(('if', 'for', 'while', 'function', 'class')) and
                        not line.strip().startswith('//')):
                        fixed_lines.append(stripped + ';')
                        if "Added missing semicolons" not in fixes_applied:
                            fixes_applied.append("Added missing semicolons")
                    else:
                        fixed_lines.append(line)
                modified_content = '\n'.join(fixed_lines)
        
        # General fixes
        if "whitespace" in issue_description.lower() or "spacing" in issue_description.lower():
            # Remove trailing whitespace
            lines = modified_content.split('\n')
            fixed_lines = [line.rstrip() for line in lines]
            modified_content = '\n'.join(fixed_lines)
            fixes_applied.append("Removed trailing whitespace")
        
        # Apply fixes if auto mode and changes were made
        changes_made = modified_content != original_content
        
        if fix_type == "auto" and changes_made:
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            status = "Fixed automatically"
        elif fix_type == "suggest":
            status = "Suggestions generated"
        else:
            status = "Manual review required"
        
        return {
            "file_path": file_path,
            "issue_description": issue_description,
            "fix_type": fix_type,
            "backup_created": backup_path if backup else None,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "status": status,
            "suggestions": [
                "Review the changes before committing",
                "Test the code after applying fixes",
                "Consider running linting tools for additional checks"
            ],
            "fixed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to debug code: {str(e)}"}


@mcp.tool()
async def optimize_profile(profile_id: str, target_niche: str = "", 
                         ctx: Context = None) -> Dict[str, Any]:
    """
    Provide profile optimization recommendations using LLM analysis
    
    Args:
        profile_id: ID of the profile to optimize
        target_niche: Specific niche to optimize for (optional)
    """
    
    if not llm:
        return {"error": "ChatGroq not initialized. Please set GROQ_API_KEY environment variable."}
    
    profile = db.user_profiles.get(profile_id)
    if not profile:
        return {"error": f"Profile {profile_id} not found"}
    
    if ctx:
        await ctx.info(f"Optimizing profile for: {profile.name}")
    
    # Analyze current market demand
    market_context = f"""
    Analyze and optimize the following freelancer profile:
    
    CURRENT PROFILE:
    Name: {profile.name}
    Title: {profile.title}
    Skills: {', '.join([f"{skill.name} ({skill.level}, {skill.years_experience}y)" for skill in profile.skills])}
    Rate: ${profile.hourly_rate_min}-${profile.hourly_rate_max}/hr
    Experience: {profile.years_experience} years
    Success Rate: {profile.success_rate}%
    Target Niche: {target_niche or 'General development'}
    
    Provide specific recommendations for:
    1. Profile title optimization
    2. Skill positioning and emphasis
    3. Rate optimization based on market demand
    4. Portfolio recommendations
    5. Niche specialization opportunities
    
    Focus on actionable advice that will increase gig match rates and client attraction.
    """
    
    try:
        response = llm.invoke(market_context)
        recommendations = response.content
        
        # Generate specific action items
        action_items = []
        
        # Rate analysis
        avg_market_rate = 50  # This would come from real market data
        if profile.hourly_rate_max < avg_market_rate * 0.8:
            action_items.append(f"Consider increasing rates - market average is ${avg_market_rate}/hr")
        
        # Skill gaps analysis
        hot_skills = ["AI/ML", "React", "Python", "TypeScript", "Cloud Computing"]
        current_skills = [skill.name.lower() for skill in profile.skills]
        missing_hot_skills = [skill for skill in hot_skills 
                            if skill.lower() not in current_skills]
        
        if missing_hot_skills:
            action_items.append(f"Consider learning: {', '.join(missing_hot_skills[:3])}")
        
        # Success rate improvement
        if profile.success_rate < 95:
            action_items.append("Focus on improving success rate to 95%+ for better visibility")
        
        return {
            "profile_id": profile_id,
            "current_profile": {
                "title": profile.title,
                "skills_count": len(profile.skills),
                "rate_range": f"${profile.hourly_rate_min}-${profile.hourly_rate_max}/hr",
                "success_rate": f"{profile.success_rate}%"
            },
            "recommendations": recommendations,
            "action_items": action_items,
            "market_insights": {
                "hot_skills": hot_skills,
                "average_rate": f"${avg_market_rate}/hr",
                "success_rate_target": "95%+",
                "portfolio_items_recommended": 5
            },
            "next_steps": [
                "Update profile title and description",
                "Add 2-3 portfolio pieces showcasing best work",
                "Consider obtaining relevant certifications",
                "Set up automated bid responses for matching gigs"
            ],
            "optimized_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to optimize profile: {str(e)}"}


@mcp.tool()
def track_application_status(applications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Track and analyze freelance application performance
    
    Args:
        applications: List of application data with status updates
    """
    
    total_apps = len(applications)
    if total_apps == 0:
        return {"error": "No applications provided"}
    
    # Analyze application performance
    statuses = {}
    platforms = {}
    response_times = []
    success_rate = 0
    
    for app in applications:
        # Count statuses
        status = app.get('status', 'pending')
        statuses[status] = statuses.get(status, 0) + 1
        
        # Count platforms
        platform = app.get('platform', 'unknown')
        platforms[platform] = platforms.get(platform, 0) + 1
        
        # Calculate response times
        if 'applied_date' in app and 'response_date' in app:
            try:
                applied = datetime.fromisoformat(app['applied_date'])
                responded = datetime.fromisoformat(app['response_date'])
                response_time = (responded - applied).days
                response_times.append(response_time)
            except:
                pass
        
        # Calculate success rate
        if status in ['accepted', 'hired', 'contract_signed']:
            success_rate += 1
    
    success_rate = (success_rate / total_apps) * 100
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Generate insights
    insights = []
    
    if success_rate < 10:
        insights.append("Low success rate - consider improving proposal quality or targeting better-fit gigs")
    elif success_rate > 25:
        insights.append("Excellent success rate! Consider applying to more premium gigs")
    
    if avg_response_time > 7:
        insights.append("Slow client responses - may indicate low-quality clients or poor proposal targeting")
    
    best_platform = max(platforms.items(), key=lambda x: x[1])[0] if platforms else "N/A"
    insights.append(f"Most active on {best_platform} - consider focusing efforts here")
    
    return {
        "total_applications": total_apps,
        "success_rate": round(success_rate, 1),
        "status_breakdown": statuses,
        "platform_breakdown": platforms,
        "average_response_time_days": round(avg_response_time, 1),
        "insights": insights,
        "recommendations": [
            "Follow up on pending applications after 3-5 days",
            "A/B test different proposal templates",
            "Focus on gigs with <10 proposals for better chances",
            "Maintain consistent application schedule"
        ],
        "performance_metrics": {
            "response_rate": round((len(response_times) / total_apps) * 100, 1),
            "best_performing_platform": best_platform,
            "application_trend": "Stable"  # This would be calculated from historical data
        }
    }


# Main execution
def main():
    """Run the Freelance Gig Aggregator MCP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Freelance Gig Aggregator MCP Server")
    parser.add_argument("transport", nargs="?", default="stdio", 
                       choices=["stdio", "sse", "streamable-http"],
                       help="Transport method (default: stdio)")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        # Run with stdio transport for local connection
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        mcp.run(transport="sse", host="localhost", port=8000)
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host="localhost", port=8001)


if __name__ == "__main__":
    main()