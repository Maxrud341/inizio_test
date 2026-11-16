import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
    SEARCH_HL = os.environ.get("SEARCH_HL", "cs")   # language
    SEARCH_GL = os.environ.get("SEARCH_GL", "cz")   # country
    SEARCH_NUM = int(os.environ.get("SEARCH_NUM", "10"))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
