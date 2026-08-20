#!/usr/bin/env python3
"""Generate docs/openapi.json from the running application."""

from __future__ import annotations

import json
import os

# Ensure required config is available
os.environ.setdefault("DISCORD_TOKEN", "openapi-generator")
os.environ.setdefault("DISCORD_CLIENT_ID", "openapi-generator")
os.environ.setdefault("DISCORD_CLIENT_SECRET", "openapi-generator")
os.environ.setdefault("SESSION_SECRET", "openapi-generator")

from teabot.app import create_app

app = create_app()
schema = app.openapi()

output_path = "docs/openapi.json"
with open(output_path, "w") as f:
    json.dump(schema, f, indent=2)

print(f"OpenAPI schema written to {output_path}")
print(f"Paths: {list(schema.get('paths', {}).keys())}")
