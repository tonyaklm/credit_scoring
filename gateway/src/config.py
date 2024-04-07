from pydantic_settings import BaseSettings

my_api = ""


class Settings(BaseSettings):
    product_engine_url: str = f"http://{my_api}:5001"
    origination_url: str = f"http://{my_api}:5002"


settings = Settings()
