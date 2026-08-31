"""Application entry point."""

from http_crud_api.logging.setup import setup_logging
from http_crud_api.server import run_server


def main() -> None:
    """Configure logging and start the HTTP server."""

    setup_logging()
    run_server()


if __name__ == "__main__":
    main()
