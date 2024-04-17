from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    scoring_url: str = "http://scoring:8000"
    product_engine_url: str = "http://product_engine:8000"
    database_url: str = "postgresql+asyncpg://origination:origination@postgresql:5432/origination"
    kafka_url: str = "kafka:29092"
    kafka_consume_topic: str = "new-agreements"


settings = Settings()
