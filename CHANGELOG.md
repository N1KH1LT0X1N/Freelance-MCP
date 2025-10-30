# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-31

### Added
- Initial release of Freelance MCP Server
- Multi-platform gig search and filtering (Upwork, Fiverr, Freelancer, etc.)
- AI-powered proposal generation using ChatGroq LLM
- Rate negotiation strategy generator
- User profile creation and management
- Profile-to-gig fit analysis
- Code review tool with quality metrics
- Code debugging with automatic fixes
- Profile optimization recommendations
- Application performance tracking
- Market trends and insights resource
- Full Claude Desktop integration via MCP protocol
- Environment-based configuration
- Comprehensive documentation

### Tools Implemented
- `search_gigs` - Search and filter freelance opportunities
- `validate` - Validate owner phone number
- `analyze_profile_fit` - Analyze profile compatibility with gigs
- `generate_proposal` - Generate AI-powered proposals
- `negotiate_rate` - Generate negotiation strategies
- `create_user_profile` - Create freelancer profiles
- `code_review` - Review code quality
- `code_debug` - Debug and fix code issues
- `optimize_profile` - Get profile optimization tips
- `track_application_status` - Track application performance

### Resources Implemented
- `freelance://profile/{profile_id}` - Access user profiles
- `freelance://gigs/{platform}` - Get platform-specific gigs
- `freelance://market-trends` - Access market insights

### Technical Details
- FastMCP server implementation
- Stdio transport for Claude Desktop
- ChatGroq LLM integration via LangChain
- Pydantic data validation
- Comprehensive error handling
- Sample data for demonstration

[Unreleased]: https://github.com/N1KH1LT0X1N/Freelance-MCP/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/N1KH1LT0X1N/Freelance-MCP/releases/tag/v1.0.0
