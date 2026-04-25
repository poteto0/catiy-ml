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
        r2AccountID: str,
        r2AccessKeyID: str,
        r2AccessSecretKey: str,
    ):
        self.postgresUser = postgresUser
        self.postgresPassword = postgresPassword
        self.postgresHost = postgresHost
        self.postgresPort = postgresPort
        self.postgresDB = postgresDB
        self.r2AccountID = r2AccountID
        self.r2AccessKeyID = r2AccessKeyID
        self.r2AccessSecretKey = r2AccessSecretKey

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
    r2AccountID = os.getenv("R2_ACCOUNT_ID") or ""
    r2AccessKeyID = os.getenv("R2_ACCESS_KEY_ID") or ""
    r2AccessSecretKey = os.getenv("R2_ACCESS_SECRET_KEY") or ""

    return AppSetting(
        postgresUser=psqlUser,
        postgresDB=psqlDB,
        postgresHost=psqlHost,
        postgresPassword=psqlPassword,
        postgresPort=psqlPort,
        r2AccountID=r2AccountID,
        r2AccessKeyID=r2AccessKeyID,
        r2AccessSecretKey=r2AccessSecretKey,
    )


setting = init_setting()
