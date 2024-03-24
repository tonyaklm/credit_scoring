from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    product_engine_url: str = "http://my_api:5001"
    origination_url: str = "http://my_api:5002"


settings = Settings()
