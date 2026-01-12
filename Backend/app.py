import os
import asyncio
import json
import re
import traceback
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.messages import HumanMessage

from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools

# =======================
# App setup
# =======================
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =======================
# Models
# =======================
class QueryInput(BaseModel):
    description: str


# =======================
# LLM
# =======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b",
    temperature=0.5,
    max_tokens=500,
)


# =======================
# Helper: normalize & extract tool outputs
# =======================
def _extract_from_message_obj(m):
    """
    Return (is_tool_message: bool, content_str_or_obj)
    """
    # 1) get raw content
    content = None
    if hasattr(m, "content"):
        content = getattr(m, "content")
    elif isinstance(m, dict):
        content = m.get("content") or m.get("text") or m.get("output_text") or m.get("body")

    # 2) determine class name / flags
    clsname = getattr(m, "__class__", type(m)).__name__
    additional = getattr(m, "additional_kwargs", None)
    tool_call_id = getattr(m, "tool_call_id", None)

    # 3) treat list-of-chunks (common for tool outputs) => join text parts
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                # typical structure: {'type': 'text', 'text': '...'}
                if item.get("type") == "text" and "text" in item:
                    parts.append(item["text"])
                elif "text" in item:
                    parts.append(item["text"])
                else:
                    parts.append(json.dumps(item))
            else:
                parts.append(str(item))
        joined = "\n".join(parts)
        return True, joined

    # 4) dict-like content (may already be structured)
    if isinstance(content, dict):
        # if known field names exist, return structured
        if "output_text" in content:
            return True, content["output_text"]
        return True, content  # tool outputs often are dicts

    # 5) simple string content
    if isinstance(content, str):
        # If contains JSON blob, return parsed JSON if possible
        s = content.strip()
        # try parse whole string
        try:
            parsed = json.loads(s)
            return True, parsed
        except Exception:
            # try to find JSON substring
            match = re.search(r"(\{[\s\S]*\})", s)
            if match:
                js = match.group(1)
                try:
                    parsed = json.loads(js)
                    return True, parsed
                except Exception:
                    # fallback to raw string
                    pass
        # Not necessarily tool message: decide based on class/flags
        is_tool = (
            "ToolMessage" in clsname
            or "tool" in clsname.lower()
            or tool_call_id is not None
            or (isinstance(additional, dict) and additional.get("tool_calls"))
        )
        return is_tool, s

    # 6) no content
    return False, None


# =======================
# Agent runner
# =======================
async def run_agent_with_query(user_message: str):
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            print("Available tools:")
            for tool in tools:
                print(f"  - {getattr(tool, 'name', repr(tool))}: {getattr(tool, 'description', '')}")

            llm_with_tools = llm.bind_tools(tools)
            agent = create_agent(model=llm_with_tools, tools=tools)

            print(f"\nSending message: {user_message}\n")

            response = await agent.ainvoke({"messages": [HumanMessage(content=user_message)]})

            print("\nRaw agent response:")
            print(response)

            # Normalize messages list
            msgs = []
            if isinstance(response, dict) and "messages" in response:
                msgs = response["messages"]
            elif isinstance(response, (list, tuple)):
                msgs = list(response)
            else:
                # fallback: return raw string
                return {"assistant": str(response), "tool_outputs": []}

            assistant_texts = []
            tool_outputs = []

            for m in msgs:
                is_tool, content = _extract_from_message_obj(m)
                if is_tool:
                    tool_outputs.append(content)
                else:
                    if content:
                        assistant_texts.append(content)

            # Prefer the first tool output (most tools return single ToolMessage), but include all
            first_tool = None
            if tool_outputs:
                first_tool = tool_outputs[0]

            # Compose return value: structured if JSON/dict, else string
            return {
                "assistant": "\n\n".join(assistant_texts) if assistant_texts else None,
                "tool_outputs": tool_outputs,
                "primary_tool_output": first_tool,
            }


# =======================
# API Endpoints
# =======================
@app.post("/diagnosis")
async def get_diagnosis(query_input: QueryInput):
    try:
        print(f"Received query: {query_input.description}")

        agent_response = await run_agent_with_query(query_input.description)

        # If the tool returned structured JSON/dict, send that as pubmed_summary.
        pubmed_summary = agent_response.get("primary_tool_output") or agent_response.get("assistant") or ""

        return {
            "symptom": [query_input.description],
            "pubmed_summary": pubmed_summary,
            "raw_agent": agent_response,  # optional: useful for debugging in frontend
        }

    except Exception as e:
        print(f"Error processing query: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)