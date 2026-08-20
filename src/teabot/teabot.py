from __future__ import annotations

import uvicorn

from teabot.app import create_app
from teabot.config import config

app = create_app()


def main() -> None:
    uvicorn.run(
        "teabot.teabot:app",
        host="0.0.0.0",
        port=8000,
        log_level=config.log_level.lower(),
        reload=config.dev_mode,
    )
