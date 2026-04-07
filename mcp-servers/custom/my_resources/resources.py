from mcp.server.fastmcp import FastMCP

# Demo Resource MCP Server
mcp = FastMCP("Demo Resources Server")


@mcp.resource("resource:sample_csv")
def sample_csv() -> str:
    """Returns a small CSV dataset useful for demoing resource usage.

    The client can fetch this resource and include it in prompts or
    save it for processing by tools.
    """
    return (
        "id,name,value\n"
        "1,Alice,12.3\n"
        "2,Bob,7.8\n"
        "3,Charlie,15.0\n"
    )


@mcp.resource("resource:dataset_info")
def dataset_info() -> dict:
    """Simple metadata about the sample dataset."""
    return {
        "name": "demo_sample_csv",
        "rows": 3,
        "columns": ["id", "name", "value"],
        "description": "Tiny CSV for MCP resource demo",
    }


if __name__ == "__main__":
    mcp.run()
