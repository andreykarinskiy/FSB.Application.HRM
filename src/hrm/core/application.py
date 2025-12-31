import datetime
from typing import List

from hrm.core.model import Candidate, CandidateStatus
from hrm.core.persistence import CandidateRepository, JsonCandidateRepository


class UseCases:
    """
    Бизнес-логика приложения.
    """
    
    def __init__(self, repository: CandidateRepository):
        """
        Инициализация UseCases.
        :param repository: Репозиторий для работы с кандидатами. Если не указан, создается JsonCandidateRepository.
        """
        self._repository = repository

    def register_candidate(self, candidate: Candidate) -> int:
        """
        Регистрирует нового кандидата.
        :return: Идентификатор кандидата.
        """
        return self._repository.insert_or_update(candidate)

    def get_candidate(self, candidate_id: int) -> Candidate:
        """
        Возвращает существующего кандидата.
        :param candidate_id: Идентификатор кандидата.
        :return: Найденный кандидат.
        :raises ValueError: Если кандидат с указанным ID не найден.
        """
        candidate = self._repository.get_by_id(candidate_id)
        if candidate is None:
            raise ValueError(f"Кандидат с ID {candidate_id} не найден")
        return candidate


    def get_all_candidates(self) -> List[Candidate]:
        """
        Возвращает список всех кандидатов.
        :return: Список кандидатов.
        """
        return self._repository.get_all()


    def edit_candidate(self, candidate: Candidate) -> Candidate:
        """
        Редактирование кандидата.
        :param candidate: Изменяемый кандидат.
        :return: Измененный кандидат.
        :raises ValueError: Если кандидат с указанным ID не найден или ID не указан.
        """
        if candidate.id is None:
            raise ValueError("ID кандидата должен быть указан для редактирования")
        
        existing_candidate = self._repository.get_by_id(candidate.id)
        if existing_candidate is None:
            raise ValueError(f"Кандидат с ID {candidate.id} не найден")
        
        # Сохраняем ID и статус из существующего кандидата, обновляем время изменения
        updated_candidate = candidate.model_copy(update={
            "id": existing_candidate.id,
            "status": existing_candidate.status,
            "updated_at": datetime.datetime.now()
        })
        
        candidate_id = self._repository.insert_or_update(updated_candidate)
        return self._repository.get_by_id(candidate_id)


    def delete_candidate(self, candidate_id: int) -> None:
        """
        Удаление кандидата.
        :param candidate_id: Уникальный идентификатор.
        :raises ValueError: Если кандидат с указанным ID не найден.
        """
        candidate = self._repository.get_by_id(candidate_id)
        if candidate is None:
            raise ValueError(f"Кандидат с ID {candidate_id} не найден")
        self._repository.delete(candidate_id)

    def clear_all_candidates(self) -> None:
        """
        Очищает репозиторий от всех данных.
        Используется для приемочных тестов.
        """
        self._repository.clear_all()


    def get_total_candidates(self) -> int:
        """
        Возвращение общего количества кандидатов.
        :return: Общее количество кандидатов в системе.
        """
        return len(self._repository.get_all())


    def accept_candidate(self, candidate_id: int) -> None:
        """
        Принимает кандидата в качестве нового сотрудника.
        Меняет статус кандидата на APPROVED.
        :param candidate_id: Уникальный идентификатор кандидата.
        :raises ValueError: Если кандидат с указанным ID не найден.
        """
        candidate = self._repository.get_by_id(candidate_id)
        if candidate is None:
            raise ValueError(f"Кандидат с ID {candidate_id} не найден")
        
        updated_candidate = candidate.model_copy(update={
            "status": CandidateStatus.APPROVED,
            "updated_at": datetime.datetime.now()
        })
        self._repository.insert_or_update(updated_candidate)


    def reject_candidate(self, candidate_id: int) -> None:
        """
        Отклоняет кандидата.
        Меняет статус кандидата на REJECTED.
        :param candidate_id: Уникальный идентификатор кандидата.
        :raises ValueError: Если кандидат с указанным ID не найден.
        """
        candidate = self._repository.get_by_id(candidate_id)
        if candidate is None:
            raise ValueError(f"Кандидат с ID {candidate_id} не найден")
        
        updated_candidate = candidate.model_copy(update={
            "status": CandidateStatus.REJECTED,
            "updated_at": datetime.datetime.now()
        })
        self._repository.insert_or_update(updated_candidate)