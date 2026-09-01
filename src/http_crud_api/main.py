"""Application entry point."""

from http_crud_api.logging.setup import setup_logging
from http_crud_api.server import run_server
from http_crud_api.settings import Settings


def main() -> None:
    """Configure logging and start the HTTP server."""

    settings = Settings()
    setup_logging(settings)
    run_server(settings)


if __name__ == "__main__":
    main()
