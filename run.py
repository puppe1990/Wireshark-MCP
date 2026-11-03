import argparse
import logging

import uvicorn

from app.config import settings
from app.server import mcp

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))

logger = logging.getLogger("wireshark-mcp")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")

    args = parser.parse_args()

    if args.transport == "stdio":
        try:
            logger.info("Starting MCP server (STDIO)")

            mcp.run()

        except KeyboardInterrupt:
            logger.info("MCP server stopped gracefully.")

    elif args.transport == "http":
        logger.info(f"Starting HTTP server on {settings.HTTP_HOST}:{settings.HTTP_PORT}")

        uvicorn.run("app.transports.http_transport:app", host=settings.HTTP_HOST, port=settings.HTTP_PORT, reload=False)


if __name__ == "__main__":
    main()
