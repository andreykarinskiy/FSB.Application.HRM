import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CandidateStatus(Enum):
    """
    Стадия жизненного цикла кандидата в системе.
    """

    REGISTERED = 1,
    """
    Новый кандидат.
    """

    PROPOSED = 2,
    """
    Предложен на рассмотрение.
    """

    APPROVED = 3,
    """
    Утвержден на должность.
    """

    REJECTED = 4
    """
    Отклонен.
    """


class CandidateSex(Enum):
    """
    Пол кандидата.
    """

    MALE = 1,

    FEMALE = 2


class Candidate(BaseModel):
    """
    Кандидат в будущие сотрудники компании.
    """

    id: int = Field()

    first_name: str = Field()

    last_name: str = Field()

    birth_date: Optional[datetime] = Field()

    sex: Optional[CandidateSex] = Field()

    status: CandidateStatus = Field()

    comments: str = Field()
