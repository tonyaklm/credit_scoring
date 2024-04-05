from enum import Enum


class AgreementStatus(Enum):
    new = 'new'
    scoring = 'active'
    closed = 'finished'

