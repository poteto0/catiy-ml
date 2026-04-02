import os

from pydantic import PostgresDsn


class AppSetting:
    def __init__(
        self,
        postgresUser: str,
        postgresPassword: str,
        postgresHost: str,
        postgresPort: int,
        postgresDB: str,
    ):
        self.postgresUser = postgresUser
        self.postgresPassword = postgresPassword
        self.postgresHost = postgresHost
        self.postgresPort = postgresPort
        self.postgresDB = postgresDB

    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.postgresUser,
            password=self.postgresPassword,
            host=self.postgresHost,
            port=self.postgresPort,
            path=self.postgresDB,
        )


def init_setting() -> AppSetting:
    psqlUser = os.getenv("POSTGRES_USER") or ""
    psqlDB = os.getenv("POSTGRES_DB") or ""
    psqlHost = os.getenv("POSTGRES_HOST") or ""
    psqlPassword = os.getenv("POSTGRES_PASSWORD") or ""
    psqlPort = int(os.getenv("POSTGRES_PORT") or "5432")

    return AppSetting(
        postgresUser=psqlUser,
        postgresDB=psqlDB,
        postgresHost=psqlHost,
        postgresPassword=psqlPassword,
        postgresPort=psqlPort,
    )


setting = init_setting()
