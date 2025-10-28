# AMC MCP Server - FastMCP Configuration

The AMC MCP Server now uses **FastMCP**, which provides automatic HTTP and stdio transport support!

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/nanda/src/amc-mcp
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 2. Run the Server

#### Stdio Mode (for local MCP clients)
```bash
python -m amc_mcp.fastmcp_server
```

#### HTTP Mode (for remote access)
```bash
fastmcp run amc_mcp.fastmcp_server:mcp --port 8000
```

Or simply:
```bash
fastmcp run amc_mcp/fastmcp_server.py
```

---

## Configuration for MCP Clients

### LM Studio - Stdio Transport

**File:** `~/Library/Application Support/LMStudio/mcp_config.json`

```json
{
  "mcpServers": {
    "amc-mcp": {
      "command": "/Users/nanda/src/amc-mcp/venv/bin/python",
      "args": ["-m", "amc_mcp.fastmcp_server"],
      "cwd": "/Users/nanda/src/amc-mcp"
    }
  }
}
```

### Claude Desktop - Stdio Transport

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "amc-mcp": {
      "command": "/Users/nanda/src/amc-mcp/venv/bin/python",
      "args": ["-m", "amc_mcp.fastmcp_server"],
      "cwd": "/Users/nanda/src/amc-mcp"
    }
  }
}
```

### LM Studio - HTTP Transport

```json
{
  "mcpServers": {
    "amc-mcp": {
      "url": "http://localhost:8000/mcp/v1",
      "transport": "http"
    }
  }
}
```

---

## Running as HTTP Server

FastMCP automatically provides HTTP endpoints:

### Start HTTP Server
```bash
# Option 1: Using fastmcp CLI
fastmcp run amc_mcp.fastmcp_server:mcp --port 8000

# Option 2: Using fastmcp dev mode (with auto-reload)
fastmcp dev amc_mcp.fastmcp_server:mcp --port 8000
```

### Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8000/` | Server info and documentation |
| `http://localhost:8000/mcp/v1` | MCP protocol endpoint |
| `http://localhost:8000/docs` | Interactive API docs (Swagger) |
| `http://localhost:8000/redoc` | Alternative API docs |
| `http://localhost:8000/health` | Health check |

### Test the HTTP Server

```bash
# Check server health
curl http://localhost:8000/health

# View available tools
curl http://localhost:8000/mcp/v1/tools

# Test a tool
curl -X POST http://localhost:8000/mcp/v1/tools/get_now_showing \
  -H "Content-Type: application/json" \
  -d '{"location": "Boston, MA"}'
```

---

## Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

The server will be available at:
- **HTTP**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`

### Docker Configuration for MCP Clients

```json
{
  "mcpServers": {
    "amc-mcp": {
      "url": "http://localhost:8000/mcp/v1"
    }
  }
}
```

---

## Testing

### Run Test Suite
```bash
python test_server.py
```

### Manual Testing with MCP Inspector
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Inspect the server
mcp-inspector python -m amc_mcp.fastmcp_server
```

### Test Individual Tools

```python
from amc_mcp.fastmcp_server import get_now_showing, book_seats

# Get movies
result = get_now_showing("Boston, MA")
print(result)

# Book seats
booking = book_seats(
    showtime_id="st001",
    seats=["A5", "A6"],
    user_id="test_user"
)
print(booking)
```

---

## Environment Variables

```bash
# Set custom port for HTTP server
export FASTMCP_PORT=9000

# Set log level
export FASTMCP_LOG_LEVEL=DEBUG

# Run server
fastmcp run amc_mcp.fastmcp_server:mcp
```

---

## Cloud Deployment

### Deploy to Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: amc-mcp
    env: python
    buildCommand: "pip install -r requirements.txt && pip install -e ."
    startCommand: "fastmcp run amc_mcp.fastmcp_server:mcp --port $PORT"
```

2. Deploy:
```bash
git push origin main
```

Your URL: `https://amc-mcp.onrender.com/mcp/v1`

### Deploy to Railway

```bash
railway up
```

Your URL: `https://amc-mcp.railway.app/mcp/v1`

---

## FastMCP Features

FastMCP automatically provides:

✅ **Dual Transport** - Both stdio and HTTP support  
✅ **Auto Documentation** - Swagger/ReDoc UI  
✅ **Type Safety** - Full Pydantic validation  
✅ **Hot Reload** - Dev mode with auto-restart  
✅ **Testing Tools** - Built-in test utilities  
✅ **Cloud Ready** - Easy deployment  

---

## Example Usage in MCP Client

Once configured, you can use natural language:

```
User: "Find action movies in Boston"
→ Calls: get_now_showing + get_recommendations

User: "Show me showtimes for Dune: Part Two on October 28"
→ Calls: get_showtimes

User: "Book seats A5 and A6 for showtime st001"
→ Calls: get_seat_map → book_seats

User: "Pay $37 with my card"
→ Calls: process_payment
```

---

## Troubleshooting

### "Module 'fastmcp' not found"
```bash
pip install fastmcp
```

### "Port already in use"
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
fastmcp run amc_mcp.fastmcp_server:mcp --port 9000
```

### "Cannot find data files"
Make sure you're running from the project directory or set PYTHONPATH:
```bash
export PYTHONPATH=/Users/nanda/src/amc-mcp/src
```

---

## Next Steps

1. **Add Authentication**: Implement API keys for HTTP endpoint
2. **Add Rate Limiting**: Protect against abuse
3. **Add Caching**: Cache movie data for better performance
4. **Add Webhooks**: Notify users of booking confirmations
5. **Add Real API**: Integrate with actual AMC Theatres API

Enjoy your AMC MCP Server! 🎬🍿