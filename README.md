# Freelance MCP Client - Installation and Usage Guide

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning repositories)

### 2. Installation

```bash
# Install required dependencies
uv pip install -r requirements.txt

# Or install individual packages
uv pip install mcp langchain-groq pydantic python-dotenv
```

### 3. Environment Setup

```bash
# Create environment file (run this command)
python freelance_client.py --create-env

# Edit the .env file with your API keys

# Copy .env.sample to .env and add your GROQ_API_KEY
cp .env.sample .env

# Edit .env and add: GROQ_API_KEY=your_actual_key_here
```

### 4. Get GROQ API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Create a new API key
4. Copy it to your `.env` file

### 5. Run the Server

```bash
# Start MCP Inspector (runs both Proxy and Local Server)
uv run mcp dev freelance_server.py
```

### 6. Run the Client

```bash
# Check environment setup
python freelance_client.py --check-env

# Run automated demo
python freelance_client.py --mode demo

# Run interactive mode
python freelance_client.py --mode interactive
```

## File Structure

```
your-project/
├── freelance_server.py     # MCP Server (from previous artifact)
├── freelance_client.py     # MCP Client (main file)
├── freelance_client2.py     # MCP Client (side-client file)
├── main.py                 # MCP Client #MCP Server(demo file)
├── requirements.txt        # Dependencies
├── .env                   # Environment variables (create this)
├── .env.sample           # Sample environment file
├── README.md             # This guide
└── setup.py                #Setup files
```

## Usage Examples

### Automated Demo Mode (Recommended)

```bash
python freelance_client.py --mode demo
```

This will run through all features automatically:
- 🔍 Gig searching and filtering
- 👤 User profile creation and analysis
- 📝 AI-powered proposal generation
- 💰 Rate negotiation strategies
- 🔍 Code review with quality metrics
- 🐛 Automated code debugging and fixing
- ⚡ Profile optimization recommendations
- 📚 Resource access and market insights

### Interactive Mode

```bash
python freelance_client.py --mode interactive
```

Available commands in interactive mode:
- `search` - Search for matching gigs
- `profile` - Create user profile
- `analyze` - Analyze profile fit for gigs
- `proposal` - Generate AI proposals
- `negotiate` - Get rate negotiation help
- `review` - Review code quality
- `debug` - Debug and fix code issues
- `optimize` - Get profile optimization tips
- `resources` - Access market data
- `demo` - Run full automated demo
- `quit` - Exit

## Key Features Demonstrated

### 1. Gig Search and Matching
```python
# Example: Search for React gigs under $1000
result = client.search_gigs(
    skills=["JavaScript", "React", "TypeScript"],
    max_budget=1000,
    project_type="fixed_price"
)
```

### 2. AI-Powered Proposal Generation
```python
# Generate personalized proposals using ChatGroq LLM
proposal = client.generate_proposal(
    gig_id="upwork_001",
    user_profile=profile_data,
    tone="professional"
)
```

### 3. Code Review Tool
```python
# Analyze code quality and get suggestions
review = client.code_review(
    file_path="./src/component.js",
    review_type="general"
)
```

### 4. Code Debug Tool
```python
# Automatically fix common code issues
debug_result = client.code_debug(
    file_path="./buggy_code.js",
    issue_description="Replace var with let/const",
    fix_type="auto"
)
```

### 5. Rate Negotiation
```python
# Get AI-powered negotiation strategies
negotiation = client.negotiate_rate(
    current_rate=40,
    target_rate=65,
    justification_points=["6+ years experience", "Proven track record"]
)
```

## Technical Architecture

### MCP Communication Flow
```
Client (freelance_client.py) 
    ↕️ (stdio transport)
Server (freelance_server.py)
    ↕️ (LLM calls)
ChatGroq API (Langchain integration)
```

### Server Capabilities
- **Tools**: 10+ interactive tools for gig management
- **Resources**: Market data and profile access
- **Prompts**: Template-based interactions
- **LLM Integration**: ChatGroq for AI features

### Client Features
- **Async Communication**: Full async/await support
- **Error Handling**: Comprehensive error recovery
- **Demo Mode**: Automated feature showcase
- **Interactive Mode**: Manual command interface
- **Environment Validation**: Setup verification

## Troubleshooting

### Common Issues

**1. "ChatGroq not initialized" Error**
```bash
# Make sure GROQ_API_KEY is set
python freelance_client.py --check-env
# Add your key to .env file
echo "GROQ_API_KEY=your_key_here" >> .env
```

**2. "freelance_server.py not found" Error**
```bash
# Make sure the server file is in the same directory
ls -la freelance_server.py
# Or adjust the path in freelance_client.py
```

**3. Module Import Errors**
```bash
# Install missing dependencies
pip install -r requirements.txt
# Or check what's missing
python freelance_client.py --check-env
```

**4. Server Connection Issues**
```bash
# Make sure server file is executable
python freelance_server.py stdio  # Test server directly
# Check for syntax errors in server file
python -m py_compile freelance_server.py
```

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export MCP_DEBUG=1
python freelance_client.py --mode demo
```

### Manual Server Testing

Test the server independently:
```bash
# Run server in stdio mode
python freelance_server.py stdio

# Run server with SSE transport
python freelance_server.py sse

# Run server with HTTP transport
python freelance_server.py streamable-http
```

## Advanced Usage

### Custom Configuration

Modify `freelance_client.py` to customize:
- Server connection parameters
- Demo scenarios and data
- Error handling behavior
- Output formatting

### Integration with Claude Desktop

```bash
# Install the server for Claude Desktop
uv run mcp install freelance_server.py --name "Freelance Gig Aggregator"

# With environment variables
uv run mcp install freelance_server.py -v GROQ_API_KEY=your_key
```

### Integration with ngrok for https connection

```bash
# Install the ngrok application
[Download ngrok for Windows](https://ngrok.com/downloads/windows)

#Configure and run
Add your authtoken:
    ngrok config add-authtoken <token>

Start an endpoint:
    ngrok http port_number

Congratulations, you have an endpoint online!
```

### API Extensions

The client can be extended to:
- Connect to live freelance platform APIs
- Integrate with local databases
- Add custom analysis tools
- Support additional LLM providers

## Performance Notes

- First run may be slower due to server startup
- LLM calls require internet connection and API credits
- Code review processes files up to 50MB
- Concurrent gig searches are supported
- Server maintains in-memory cache for demos

## Security Considerations

- API keys are loaded from environment variables only
- File operations are sandboxed to current directory
- No sensitive data is logged
- Server runs in isolated process
- Backup files include timestamps for safety
