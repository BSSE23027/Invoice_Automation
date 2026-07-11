import os
from pathlib import Path

TEMP_DIR = Path("/tmp")


def write_google_files():
    """
    Writes the Google OAuth JSON files from environment variables
    into temporary files.

    Returns:
        (credentials_path, token_path)
    """

    credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
    token = os.getenv("GOOGLE_TOKEN_JSON")

    credentials_path = TEMP_DIR / "credentials.json"
    token_path = TEMP_DIR / "token.json"

    if credentials:
        credentials_path.write_text(credentials)

    if token:
        token_path.write_text(token)

    return credentials_path, token_path