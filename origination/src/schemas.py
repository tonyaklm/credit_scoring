from pydantic import BaseModel
import datetime


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
    term: int
    interest: float
    disbursment_amount: float


class BaseApplication(BaseModel):
    id: int
    agreement_id: int
    product_code: str
    time_of_application: datetime.datetime
    status: str

class FinishApplication(BaseModel):
    agreement_id: int
    product_code: str

