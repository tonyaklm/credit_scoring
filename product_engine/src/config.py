from pydantic_settings import BaseSettings

my_api = ""


class Settings(BaseSettings):
    origination_url: str = f"http://{my_api}:5002"
    database_url: str = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/product_engine"
    kafka_url: str = "kafka:29092"
    kafka_produce_topic: str = "new-agreements"


settings = Settings()
