from sqlalchemy import create_engine

from app.config.setting import setting

engine = create_engine(str(setting.dsn))
