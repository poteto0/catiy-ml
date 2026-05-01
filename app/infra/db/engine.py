from sqlalchemy import create_engine

from app.config.setting import setting

connect_args = {}
if setting.dsn.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(setting.dsn, connect_args=connect_args)
