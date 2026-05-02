from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.config.setting import setting

connect_args = {}
poolclass = None
if setting.dsn.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool

engine = create_engine(
    setting.dsn,
    connect_args=connect_args,
    poolclass=poolclass,
)
