import asyncio
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("terminal")


def get_downloads_dir() -> Path:
    downloads_dir = os.environ.get("DOWNLOADS_DIR")
    if downloads_dir:
        return Path(downloads_dir)
    return Path.home() / "Downloads"


@mcp.tool()
async def run_command(command: str) -> dict[str, Any]:
    """Run a terminal command and return stdout, stderr, and return code."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return {
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
            "return_code": process.returncode,
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": f"Error executing command: {exc}",
            "return_code": -1,
        }


@mcp.resource("file:///downloads/f35-brochure.pdf", mime_type="application/pdf")
def f35_brochure() -> bytes:
    """Expose f35-brochure.pdf from the user's Downloads folder as a binary resource."""
    pdf_path = get_downloads_dir() / "f35-brochure.pdf"
    with pdf_path.open("rb") as file:
        return file.read()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
