from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    product_engine_url: str = "http://product_engine:8000"
    origination_url: str = "http://origination:8000"


settings = Settings()
