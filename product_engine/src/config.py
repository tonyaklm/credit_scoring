from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    origination_url: str = "http://origination:8000"
    database_url: str = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/product_engine"
    kafka_url: str = "kafka:29092"
    kafka_produce_topic: str = "new-agreements"


settings = Settings()
