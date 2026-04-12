import os

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", 8080))
API_PATH: str = os.getenv("API_PATH", "")
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
LOG_CHAT_ID: int = int(os.getenv("LOG_CHAT_ID", 0))
LOG_TOPIC_ID: int = int(os.getenv("LOG_TOPIC_ID", 0))
NOCODB_API_TOKEN: str = os.getenv("NOCODB_API_TOKEN")
DB_USERNAME: str = os.getenv("DB_USERNAME")
DB_PASSWORD: str = os.getenv("DB_PASSWORD")
DB_HOST: str = os.getenv("DB_HOST")
DB_PORT: int = os.getenv("DB_PORT")
DB_NAME: str = os.getenv("DB_NAME")
TLM_TOKEN_DURATION: int = int(os.getenv("TLM_TOKEN_DURATION", 28800))
TLM_TOKEN_REFRESH: int = int(os.getenv("TLM_TOKEN_REFRESH", 3600))

for required_var in ["BOT_TOKEN", "NOCODB_API_TOKEN",
                     "DB_USERNAME", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]:
    if not globals()[required_var]:
        raise EnvironmentError(f"{required_var} environment variable is not set")
