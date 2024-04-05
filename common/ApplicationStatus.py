from enum import Enum


class ApplicationStatus(Enum):
    new = 'new'
    scoring = 'scoring'
    closed = 'closed'
