import asyncio
import sys
from pathlib import Path
import argparse

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq as Groq
from langchain_mcp_adapters.client import MultiServerMCPClient

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", help="Prompt to send to the agent")
    return parser.parse_args()

async def main(prompt: str):
    workspace_root = Path(__file__).resolve().parent
    load_dotenv(workspace_root / ".env")

    client = MultiServerMCPClient(
        {
            "notes-app": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(workspace_root / "mcp-servers/vulnerabilities/01-prompt-injection/notes_app.py")],
            },
            # You can add more vulnerable MCP servers here in the future:
            # "other_vulnerable_server": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/...")],
            # },
        }
    )

    tools = await client.get_tools()
    
    agent = create_agent(
        Groq(model="llama-3.3-70b-versatile"),
        tools,
    )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }
    )
    
    print("\nAgent's Final Response:")
    print(result["messages"][-1].content)

if __name__ == "__main__":
    args = parse_args()
    prompt = args.prompt or input("Prompt: ")
    asyncio.run(main(prompt))
