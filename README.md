# Freelance MCP Server - Installation and Usage Guide

A comprehensive freelance platform aggregator MCP server that helps users find gigs, generate proposals, negotiate rates, and optimize their freelance profiles using AI

## 🚀 Quick Start for Claude Desktop Users

**Want to use this with Claude Desktop right away? Follow these 3 steps:**

1. **Get a GROQ API Key** (free): Visit [console.groq.com](https://console.groq.com/), sign up, and create an API key

2. **Add to Claude Desktop config** - Edit your `claude_desktop_config.json`:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

   Add this to the `mcpServers` section (replace paths and keys with yours):
   ```json
   {
     "mcpServers": {
       "freelance": {
         "command": "uv",
         "args": [
           "run",
           "--with", "mcp",
           "--with", "python-dotenv",
           "--with", "langchain-groq",
           "--with", "pydantic",
           "C:\\path\\to\\your\\freelance_server.py",
           "stdio"
         ],
         "env": {
           "GROQ_API_KEY": "gsk_your_key_here",
           "OWNER_COUNTRY_CODE": "1",
           "OWNER_PHONE_NUMBER": "5551234567"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** and start using commands like:
   - "Search for Python gigs under $1000"
   - "Show me freelance market trends"
   - "Generate a proposal for gig upwork_001"

**Need more detailed instructions?** See [Integration with Claude Desktop](#integration-with-claude-desktop-recommended) below.

---

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

Create a `.env` file in your project directory with your API keys:

```bash
# Windows
echo GROQ_API_KEY=your_actual_key_here > .env
echo OWNER_COUNTRY_CODE=1 >> .env
echo OWNER_PHONE_NUMBER=5551234567 >> .env

# Linux/Mac
cat > .env << EOF
GROQ_API_KEY=your_actual_key_here
OWNER_COUNTRY_CODE=1
OWNER_PHONE_NUMBER=5551234567
EOF
```

**Required Environment Variables:**
- `GROQ_API_KEY` - Your Groq API key (get from https://console.groq.com/)
- `OWNER_COUNTRY_CODE` - Country code without + (e.g., 1 for US, 44 for UK)
- `OWNER_PHONE_NUMBER` - Phone number without country code or special characters
- `MCP_AUTH_TOKEN` - (Optional) Authentication token for advanced setups

### 4. Get GROQ API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Create a new API key
4. Copy it to your `.env` file

### 5. Run the Server

**Option A: Test Server Directly (for development)**
```bash
# Test server in stdio mode
python freelance_server.py stdio

# Or with uv and dependencies
uv run --with mcp --with python-dotenv --with langchain-groq --with pydantic freelance_server.py stdio
```

**Option B: Use with Claude Desktop (recommended)**

See the [Integration with Claude Desktop](#integration-with-claude-desktop-recommended) section below for full setup instructions.

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
├── freelance_server.py     # MCP Server (main server file)
├── freelance_client.py     # MCP Client (optional - for testing)
├── freelance_client2.py    # MCP Client (alternative implementation)
├── main.py                 # Demo file
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (create this)
├── README.md               # This guide
└── setup.py                # Setup configuration
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

### Integration with Claude Desktop (Recommended)

**Step 1: Create Environment File**

Create a `.env` file in your project directory:

```bash
# Windows
copy NUL .env

# Linux/Mac
touch .env
```

Add your API keys to `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
MCP_AUTH_TOKEN=your_optional_auth_token
OWNER_COUNTRY_CODE=1
OWNER_PHONE_NUMBER=5551234567
```

**Step 2: Get GROQ API Key**

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

**Step 3: Locate Claude Desktop Config**

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Step 4: Update Claude Desktop Config**

Open `claude_desktop_config.json` and add the freelance server configuration:

```json
{
  "mcpServers": {
    "freelance": {
      "command": "uv",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "python-dotenv",
        "--with", "langchain-groq",
        "--with", "pydantic",
        "/absolute/path/to/your/freelance_server.py",
        "stdio"
      ],
       "env": {
         "GROQ_API_KEY": "your_groq_api_key_here",
         "MCP_AUTH_TOKEN": "your_optional_auth_token",
         "OWNER_COUNTRY_CODE": "1",
         "OWNER_PHONE_NUMBER": "5551234567"
       }
    }
  }
}
```

**Important Notes:**
- Replace `/absolute/path/to/your/freelance_server.py` with the actual full path to your `freelance_server.py` file
- On Windows, use double backslashes: `C:\\Users\\YourName\\MCPs\\freelance_server.py`
- On Mac/Linux, use forward slashes: `/Users/YourName/MCPs/freelance_server.py`
- Replace all placeholder values with your actual API keys and phone number

**Windows Example:**
```json
{
  "mcpServers": {
    "freelance": {
      "command": "C:\\Users\\YourName\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "python-dotenv",
        "--with", "langchain-groq",
        "--with", "pydantic",
        "C:\\Users\\YourName\\MCPs\\mcp-server-1\\freelance_server.py",
        "stdio"
      ],
      "env": {
         "GROQ_API_KEY": "gsk_xxxxxxxxxxxxxxxxxxxxx",
         "MCP_AUTH_TOKEN": "your_optional_auth_token",
         "OWNER_COUNTRY_CODE": "1",
         "OWNER_PHONE_NUMBER": "5551234567"
      }
    }
  }
}
```

**Step 5: Restart Claude Desktop**

1. Completely quit Claude Desktop (not just close the window)
2. Reopen Claude Desktop
3. The freelance server should now be available

**Step 6: Verify Installation**

In Claude Desktop, try asking:
- "Search for Python freelance gigs under $500"
- "Show me current freelance market trends"
- "Validate the owner phone number"

**Troubleshooting Claude Desktop Integration:**

1. **Server shows as "failed":**
   - Check the logs: Open the "Open Logs Folder" from the error
   - Look for `ModuleNotFoundError` - means dependencies are missing
   - Verify all `--with` packages are included in args

2. **"Server disconnected" error:**
   - Ensure `stdio` is the last argument in args array
   - Check that the path to `freelance_server.py` is absolute and correct
   - Verify `uv` is installed: Run `uv --version` in terminal

3. **Environment variables not loading:**
   - Double-check the `.env` file exists in the same directory as `freelance_server.py`
   - Verify env values in `claude_desktop_config.json` match your `.env` file
   - Make sure there are no extra quotes or spaces

4. **Finding uv path (Windows):**
   ```powershell
   where.exe uv
   ```

5. **Finding uv path (Mac/Linux):**
   ```bash
   which uv
   ```

**Alternative: Manual Installation Method**

If you prefer to install dependencies globally instead of using `--with` flags:

```bash
# Install dependencies globally with uv
uv pip install mcp python-dotenv langchain-groq pydantic

# Then use simpler config
{
  "mcpServers": {
    "freelance": {
      "command": "uv",
      "args": [
        "run",
        "/path/to/freelance_server.py",
        "stdio"
      ],
      "env": {
        "GROQ_API_KEY": "your_key_here",
        "OWNER_COUNTRY_CODE": "1",
        "OWNER_PHONE_NUMBER": "5551234567"
      }
    }
  }
}
```

### Integration with ngrok for Remote Access

If you want to access your MCP server remotely via HTTPS:

```bash
# 1. Download and install ngrok
# Visit: https://ngrok.com/download

# 2. Add your authtoken (sign up at ngrok.com to get one)
ngrok config add-authtoken <your_token>

# 3. Start your MCP server on a specific port
python freelance_server.py sse --port 8080

# 4. In another terminal, expose it with ngrok
ngrok http 8080

# 5. Use the provided HTTPS URL to connect remotely
# Example: https://abc123.ngrok.io
```

**Note:** For production use, consider implementing proper authentication and security measures.

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

## Available MCP Tools

Once integrated with Claude Desktop, you'll have access to these tools:

### 🔍 Search & Discovery
- **`search_gigs`** - Search for freelance gigs by skills, budget, project type, and platform
- **`validate`** - Validate server owner's phone number

### 👤 Profile Management
- **`create_user_profile`** - Create a new freelancer profile with skills and rates
- **`analyze_profile_fit`** - Analyze how well a profile matches a specific gig
- **`optimize_profile`** - Get AI-powered profile optimization recommendations

### 📝 Proposals & Negotiation
- **`generate_proposal`** - Generate personalized proposals using AI
- **`negotiate_rate`** - Get rate negotiation strategies and messages

### 💻 Code Tools
- **`code_review`** - Review code quality with metrics and suggestions
- **`code_debug`** - Debug and automatically fix code issues

### 📊 Tracking
- **`track_application_status`** - Track and analyze application performance

### 📚 Resources
- **`freelance://profile/{profile_id}`** - Access user profile data
- **`freelance://gigs/{platform}`** - Get gigs from specific platforms
- **`freelance://market-trends`** - View current market trends and insights

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/N1KH1LT0X1N/Freelance-MCP).
