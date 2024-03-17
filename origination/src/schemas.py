from pydantic import BaseModel


class ApplicationSchema(BaseModel):
    application_id: int


class CreateApplication(BaseModel):
    product_code: str
    first_name: str
    second_name: str
    third_name: str
    birthday: str
    passport_number: str
    email: str
    phone: str
    salary: float
    disbursment_amount: float
