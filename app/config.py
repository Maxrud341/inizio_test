import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
    SEARCH_HL = os.environ.get("SEARCH_HL", "cs")   # language
    SEARCH_GL = os.environ.get("SEARCH_GL", "cz")   # country
    SEARCH_GOOGLE_DOMAIN = os.environ.get("SEARCH_GOOGLE_DOMAIN", "google.cz") # local google domain
    SEARCH_LOCATION = os.environ.get("SEARCH_LOCATION", "Czechia")             # geo-location
    SEARCH_NUM = int(os.environ.get("SEARCH_NUM", "10"))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "test-mock-api-key")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
