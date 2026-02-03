import os

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", 8080))
API_PATH: str = os.getenv("API_PATH", "")
BEARER_TOKEN: str = os.getenv("BEARER_TOKEN")
TELEMETRY_TOKEN: str = os.getenv("TELEMETRY_TOKEN")
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
LOG_CHAT_ID: int = int(os.getenv("LOG_CHAT_ID", 0))
LOG_TOPIC_ID: int = int(os.getenv("LOG_TOPIC_ID", 0))
NOCODB_API_TOKEN: str = os.getenv("NOCODB_API_TOKEN")

GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_IMPERSONATE_ADMIN_EMAIL: str = os.getenv("GOOGLE_IMPERSONATE_ADMIN_EMAIL")

AD_USERNAME: str = os.getenv("AD_USERNAME", "")
AD_PASSWORD: str = os.getenv("AD_PASSWORD", "")
AD_HOSTNAME: str = os.getenv("AD_HOSTNAME", "")

GMAIL_USERNAME: str = os.getenv("GMAIL_USERNAME", "")
GMAIL_PASSWORD: str = os.getenv("GMAIL_PASSWORD", "")

if not BEARER_TOKEN:
    raise EnvironmentError("BEARER_TOKEN environment variable is not set")
if not TELEMETRY_TOKEN:
    raise EnvironmentError("TELEMETRY_TOKEN environment variable is not set")
if not BOT_TOKEN:
    raise EnvironmentError("BOT_TOKEN environment variable is not set")
if not GOOGLE_SERVICE_ACCOUNT_JSON:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not set")
if not GOOGLE_IMPERSONATE_ADMIN_EMAIL:
    raise EnvironmentError("GOOGLE_IMPERSONATE_ADMIN_EMAIL environment variable is not set")
if not NOCODB_API_TOKEN:
    raise EnvironmentError("NOCODB_API_TOKEN environment variable is not set")
if not AD_USERNAME:
    raise EnvironmentError("AD_USERNAME environment variable is not set")
if not AD_PASSWORD:
    raise EnvironmentError("AD_PASSWORD environment variable is not set")
if not AD_HOSTNAME:
    raise EnvironmentError("AD_HOSTNAME environment variable is not set")
if not GMAIL_USERNAME:
    raise EnvironmentError("GMAIL_USERNAME environment variable is not set")
if not GMAIL_PASSWORD:
    raise EnvironmentError("GMAIL_PASSWORD environment variable is not set")
