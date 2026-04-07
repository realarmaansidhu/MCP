from mcpdoc.main import create_server


def main() -> None:
    server = create_server(
        [
            {
                "name": "MCP",
                "llms_txt": "https://modelcontextprotocol.io/llms.txt",
            }
        ],
        allowed_domains=["modelcontextprotocol.io"],
    )
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
