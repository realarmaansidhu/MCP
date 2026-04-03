from __future__ import annotations

import json
from pathlib import Path

from mcpdoc.main import create_server


def load_sources() -> list[dict[str, str]]:
    config_path = Path(__file__).with_name("mcpdoc_sources.json")
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("mcpdoc_sources.json must contain a JSON list")

    return data


def main() -> None:
    # Only allow fetching docs from modelcontextprotocol.io for safety.
    server = create_server(load_sources(), allowed_domains=["modelcontextprotocol.io"])
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
