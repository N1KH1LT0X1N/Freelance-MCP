# Contributing to Freelance MCP Server

First off, thank you for considering contributing to Freelance MCP Server! 🎉

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples
- Describe the behavior you observed and what you expected
- Include screenshots if relevant
- Include your environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any similar features in other projects

### Pull Requests

1. Fork the repo and create your branch from `master`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Freelance-MCP.git
cd Freelance-MCP

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env with your keys

# Test the server
python freelance_server.py stdio
```

## Style Guidelines

### Python Style Guide

- Follow PEP 8
- Use type hints where applicable
- Write docstrings for all functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add rate negotiation strategy generator

- Implement AI-powered negotiation message generation
- Add support for different project complexity levels
- Include success probability calculation

Fixes #123
```

## Project Structure

```
Freelance-MCP/
├── freelance_server.py      # Main MCP server
├── freelance_client.py      # Test client (optional)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── README.md               # Main documentation
└── .github/                # GitHub specific files
    ├── CONTRIBUTING.md     # This file
    ├── ISSUE_TEMPLATE/     # Issue templates
    └── workflows/          # CI/CD workflows
```

## Adding New Features

When adding a new feature:

1. **Create an Issue First** - Discuss the feature before implementing
2. **Write Tests** - Add tests for your new feature
3. **Update Documentation** - Update README.md with usage examples
4. **Add Type Hints** - Use Python type hints for all new functions
5. **Follow MCP Standards** - Ensure compliance with MCP protocol

### Adding a New Tool

```python
@mcp.tool()
def your_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of what the tool does
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dictionary with results
    """
    # Implementation
    return {"result": "success"}
```

### Adding a New Resource

```python
@mcp.resource("freelance://your-resource/{resource_id}")
def get_your_resource(resource_id: str) -> str:
    """Get your resource information"""
    # Implementation
    return json.dumps(data, indent=2)
```

## Testing

```bash
# Run basic tests
python -m pytest tests/

# Test with Claude Desktop
# 1. Update your claude_desktop_config.json
# 2. Restart Claude Desktop
# 3. Try commands in Claude
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all new functions
- Include usage examples
- Update type hints

## Questions?

Feel free to open an issue with the question label or reach out to the maintainers.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing! 🚀
