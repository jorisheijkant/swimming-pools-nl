import base64
import os

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("PORTAL_USERNAME")
PASSWORD = os.getenv("PORTAL_PASSWORD")


def get_basic_auth() -> str:
    credentials = f"{USERNAME}:{PASSWORD}"
    return base64.b64encode(credentials.encode()).decode()
