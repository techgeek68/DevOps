import os

class Config:
    def __init__(self) -> None:
        # Required. No default, no credentials in the code. Stop now if it is absent.
        try:
            self.database_url = os.environ["DATABASE_URL"]
        except KeyError as exc:
            raise RuntimeError(
                "DATABASE_URL is not set. Configuration comes from the environment; "
                "credentials never live in the source."
            ) from exc

        # These are not secret, so a sensible default is fine
        self.app_name = os.environ.get("APP_NAME", "refapp")
        self.port     = int(os.environ.get("PORT", "8000"))

def load_config() -> "Config":
    return Config()
