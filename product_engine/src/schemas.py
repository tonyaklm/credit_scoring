from pydantic import BaseModel


class CreateProduct(BaseModel):
    title: str
    code: str
    min_term: int
    max_term: int
    min_principal: float
    max_principal: float
    min_interest: float
    max_interest: float
    min_origination: float
    max_origination: float


class ProductSchema(BaseModel):
    id: int
    title: str
    code: str
    min_term: int
    max_term: int
    min_principal: float
    max_principal: float
    min_interest: float
    max_interest: float
    min_origination: float
    max_origination: float


class CreateAgreement(BaseModel):
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


class AgreementSchema(BaseModel):
    agreement_id: int


class CreateClient(BaseModel):
    first_name: str
    second_name: str
    third_name: str
    birthday: str
    passport_number: str
    email: str
    phone: str
    salary: float


class ClientSchema(BaseModel):
    id: int
    client_name: str
    client_age: int
    client_phone_number: str
    client_passport_number: str
    client_salary: float


class ProducerMessage(BaseModel):
    agreement_id: int
    client_id: int
    principal_amount: float
