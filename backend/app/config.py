import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


KEEPA_API_KEY = get_env("KEEPA_API_KEY")
PGHOST = get_env("PGHOST")
PGPORT = get_env("PGPORT", "5432")
PGDATABASE = get_env("PGDATABASE")
PGUSER = get_env("PGUSER")
PGPASSWORD = get_env("PGPASSWORD")

DEFAULT_BSR_THRESHOLD = int(get_env("DEFAULT_BSR_THRESHOLD", "50000"))
DEFAULT_MAX_FBA_OFFERS = int(get_env("DEFAULT_MAX_FBA_OFFERS", "5"))
DEFAULT_CV_THRESHOLD = float(get_env("DEFAULT_CV_THRESHOLD", "0.10"))

AI_EXPLANATIONS_ENABLED = get_env("AI_EXPLANATIONS_ENABLED", "true").lower() == "true"
JWT_SECRET = get_env("JWT_SECRET", "change_me")
AUTH_DISABLED = get_env("AUTH_DISABLED", "true").lower() == "true"
