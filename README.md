# MediAssist - AI Health Assistant

A React frontend connected to a FastAPI backend with MCP server integration for health-related queries using LangGraph agents.

## Features

- 🩺 Symptom analysis and extraction
- 📚 PubMed article summaries
- 💡 Health tips and wellness information
- 🤖 AI agent with MCP tool integration
- 🎨 Clean, responsive UI similar to modern health apps

## Architecture

The system consists of three main components:

1. **MCP Server** (Port 8000): Provides medical tools via Model Context Protocol
2. **FastAPI Backend** (Port 8080): Handles API requests and runs LangGraph agents
3. **React Frontend** (Port 5173): User interface for health queries

```
Frontend (React) → Backend (FastAPI) → Agent (LangGraph) → MCP Server → Medical Tools
```

## Setup & Running

### Prerequisites
- Python 3.11.6+
- Node.js and Yarn
- GROQ API key (set in `.env` file)

### Environment Setup
1. Create a `.env` file in the Backend directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Quick Start (All Servers)
The easiest way to run the entire system:

1. Make the startup script executable:
   ```bash
   chmod +x start-dev.sh
   ```

2. Run all servers:
   ```bash
   ./start-dev.sh
   ```

This will start:
- MCP server on http://localhost:8000/mcp
- Backend API on http://localhost:8080
- Frontend on http://localhost:5173

### Manual Setup

#### Backend Setup
1. Navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the MCP server:
   ```bash
   python mcp_server.py
   ```

4. In a new terminal, start the FastAPI server:
   ```bash
   python app.py
   ```

#### Frontend Setup
1. Navigate to the React app directory:
   ```bash
   cd my-react-app
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Start the development server:
   ```bash
   yarn dev
   ```

## API Endpoints

### POST /diagnosis
Analyzes symptoms using AI agent and MCP tools.

**Request:**
```json
{
  "description": "I have a headache and fever"
}
```

**Response:**
```json
{
  "symptom": ["headache", "fever"],
  "pubmed_summary": "Medical summary based on PubMed articles..."
}
```

### GET /health
Health check endpoint.

### GET /test-mcp
Tests MCP server connection and lists available tools.

## MCP Integration

The system uses Model Context Protocol (MCP) to provide medical tools:

- **Server**: FastMCP running on port 8000
- **Tool**: `clinisight_ai(symptom_text)` - Analyzes symptoms and fetches medical information
- **Agent**: LangGraph agent with GROQ LLM that can use MCP tools

## How It Works

1. User enters a health query in the frontend
2. Frontend sends POST request to `/diagnosis` endpoint
3. Backend creates a LangGraph agent with MCP tools
4. Agent processes the query and calls appropriate MCP tools
5. MCP server extracts symptoms and fetches PubMed articles
6. Agent returns structured response to frontend
7. Frontend displays symptoms and medical summary

## Usage

1. Enter your health-related query in the input field
2. Click submit or press Enter
3. The AI agent will analyze your query using medical tools
4. View the extracted symptoms and medical summary
5. Use the sample queries for quick testing

## Troubleshooting

### Common Issues

1. **Frontend shows nothing after submitting query**:
   - Check browser console for errors
   - Verify backend is running on port 8080
   - Test with simple endpoint: `curl http://localhost:8080/test-response -X POST`

2. **MCP connection errors**:
   - Ensure MCP server is running on port 8000
   - Test MCP connection: `curl http://localhost:8080/test-mcp`

3. **GROQ API errors**:
   - Verify GROQ_API_KEY is set in `.env` file
   - Check API key is valid and has credits

### Testing

Use the provided test files:

```bash
# Test backend endpoints
python test_integration.py

# Test frontend (open in browser)
open test_frontend.html
```

### Debug Endpoints

- `GET /health` - Health check
- `GET /test-mcp` - Test MCP server connection  
- `POST /test-response` - Test simple response format
- `POST /debug-diagnosis` - Debug agent response parsing

## Disclaimer

This application is for informational purposes only. Always consult a healthcare professional for medical advice.