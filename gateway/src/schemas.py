from pydantic import BaseModel


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


class AgreementSchema(BaseModel):
    agreement_id: int


class ApplicationSchema(BaseModel):
    application_id: int
