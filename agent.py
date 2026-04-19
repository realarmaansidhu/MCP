import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq as Groq
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    workspace_root = Path(__file__).resolve().parent
    load_dotenv(workspace_root / ".env")

    client = MultiServerMCPClient(
        {
            # "notes-app": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/01-prompt-injection/notes_app.py")],
            # },
            # "doc-helper": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/01-prompt-injection/doc_helper.py")],
            # },
            # "smart-calculator": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/02-tool-poisoning/smart_calculator.py")],
            # },
            # "enhanced-notes": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/02-tool-poisoning/enhanced_notes.py")],
            # },
            # "session-manager": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/03-data-exfiltration/session_manager.py")],
            # },
            # "project-helper": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/03-data-exfiltration/project_helper.py")],
            # },
            # "corp-knowledge-base": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [
            #         str(workspace_root / "mcp-servers/vulnerabilities/04-command-injection/corp_knowledge_base.py")
            #     ],
            # },
            # "internal-iam": {
            #     "transport": "stdio",
            #     "command": sys.executable,
            #     "args": [str(workspace_root / "mcp-servers/vulnerabilities/07-context-manipulation/internal_iam.py")],
            # }
            "read-summarize": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(workspace_root / "mcp-servers/vulnerabilities/09-authorization/read_summarize.py")]
            }
        }
    )

    tools = await client.get_tools()

    agent = create_agent(
        Groq(model="llama-3.3-70b-versatile"),
        tools,
    )

    # Check if a single prompt was passed as command line argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        print("\nAgent's Final Response:")
        print(result["messages"][-1].content)
        return

    # Interactive multi-turn conversation mode
    print("MCP Security Agent (type 'exit' to quit)")
    print("-" * 45)

    messages = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting.")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            result = await agent.ainvoke({"messages": messages})
            # Update messages with full history from agent
            messages = result["messages"]
            print(f"\nAgent: {messages[-1].content}")
        except Exception as e:
            # Groq/Llama sometimes garbles tool call formatting — don't crash
            print(f"\nAgent error (model garbled a tool call): {type(e).__name__}")
            print("Try rephrasing or continue chatting.")


if __name__ == "__main__":
    asyncio.run(main())