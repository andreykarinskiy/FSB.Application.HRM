import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CandidateStatus(Enum):
    """
    Стадия жизненного цикла кандидата в системе.
    """

    REGISTERED = 1
    """
    Новый кандидат.
    """

    PROPOSED = 2
    """
    Предложен на рассмотрение.
    """

    APPROVED = 3
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

    MALE = 1

    FEMALE = 2


class Candidate(BaseModel):
    """
    Кандидат в будущие сотрудники компании.
    """

    id: int = Field(..., gt=0, description="ID кандидата")

    first_name: str = Field(..., min_length=1, max_length=100, description="Имя")

    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия")

    phone: Optional[str] = Field(None, max_length=20, description="Контактный телефон")

    birth_date: Optional[datetime.datetime] = Field(None, description="Дата рождения")

    sex: Optional[CandidateSex] = Field(None, description="Пол")

    status: CandidateStatus = Field(..., description="Статус кандидата")

    comments: Optional[str] = Field(None, description="Комментарии")
