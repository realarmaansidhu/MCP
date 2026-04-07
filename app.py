import asyncio
import argparse
import sys
from pathlib import Path

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
            "terminal": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(workspace_root / "mcp-servers/custom/terminal/server.py")],
            },
            "weather": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(workspace_root / "mcp-servers/custom/weather/weather.py")],
            },
            "mcpdocs": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    str(workspace_root / "mcp-servers/custom/mcpdocs/server.py"),
                ],
            },
            "my_prompts": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(workspace_root / "mcp-servers/custom/my_prompts/prompts.py")],
            },
            "my_resources": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(workspace_root / "mcp-servers/custom/my_resources/resources.py")],
            },
        }
    )

    # Discover prompts and resources (if the client supports these helpers)
    prompts = None
    resources = None
    get_prompts = getattr(client, "get_prompts", None)
    if callable(get_prompts):
        try:
            prompts = await client.get_prompts()
        except Exception as e:
            print("Warning: couldn't list prompts:", e)

    get_resources = getattr(client, "get_resources", None)
    if callable(get_resources):
        try:
            resources = await client.get_resources()
        except Exception as e:
            print("Warning: couldn't list resources:", e)

    # Print discovered prompts/resources for visibility
    if prompts:
        print("Discovered prompts:")
        try:
            for p in prompts:
                name = getattr(p, "name", p.get("name") if isinstance(p, dict) else str(p))
                desc = getattr(p, "description", p.get("description") if isinstance(p, dict) else "")
                print(" -", name, "->", desc)
        except Exception:
            print(prompts)

    if resources:
        print("Discovered resources:")
        try:
            for r in resources:
                name = getattr(r, "name", r.get("name") if isinstance(r, dict) else str(r))
                print(" -", name)
        except Exception:
            print(resources)

    # Try to invoke the `data_analyst` prompt (if available) to construct a better prompt
    final_prompt = prompt
    try:
        if prompts:
            has_data_analyst = any((getattr(p, "name", None) == "data_analyst") or (isinstance(p, dict) and p.get("name") == "data_analyst") for p in prompts)
        else:
            has_data_analyst = False

        invoke_prompt = getattr(client, "invoke_prompt", None) or getattr(client, "prompts_invoke", None)
        if has_data_analyst and callable(invoke_prompt):
            try:
                constructed = await invoke_prompt("data_analyst", {"task": prompt})
                # Some clients return a dict with `text` or a string directly
                if isinstance(constructed, dict):
                    constructed_text = constructed.get("text") or constructed.get("result") or str(constructed)
                else:
                    constructed_text = str(constructed)
                print("Using constructed prompt from my_prompts (data_analyst)")
                final_prompt = constructed_text
            except Exception as e:
                print("Could not invoke data_analyst prompt:", e)

        # Try to fetch a demo resource and append its head to the prompt
        fetch_resource = getattr(client, "get_resource", None) or getattr(client, "fetch_resource", None) or getattr(client, "read_resource", None)
        if resources and callable(fetch_resource):
            # look for sample_csv resource
            found = None
            for r in resources:
                name = getattr(r, "name", None) or (r.get("name") if isinstance(r, dict) else None)
                if name == "sample_csv":
                    found = name
                    break
            if found:
                try:
                    content = await fetch_resource(found)
                    # normalize result
                    if isinstance(content, dict) and "content" in content:
                        content_text = content["content"]
                    else:
                        content_text = str(content)
                    final_prompt += "\n\nSample dataset (first 200 chars):\n" + content_text[:200]
                    print("Appended sample_csv resource to prompt (preview).")
                except Exception as e:
                    print("Failed to fetch resource sample_csv:", e)
    except Exception as e:
        print("Prompts/resources discovery failed:", e)

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
                    "content": final_prompt,
                }
            ]
        }
    )
    print(result)


if __name__ == "__main__":
    args = parse_args()
    prompt = args.prompt or input("Prompt: ")
    asyncio.run(main(prompt))
