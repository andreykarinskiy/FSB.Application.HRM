from typing import List

from hrm.core.model import Candidate

class UseCases:
    """
    Бизнес-логика приложения.
    """

    def register_candidate(self, candidate: Candidate) -> int:
        """
        Регистрирует нового кандидата.
        :return: Идентификатор кандидата.
        """
        return 1


    def get_candidate(self, candidate_id: int) -> Candidate:
        """
        Возвращает существующего кандидата.
        :param candidate_id: Идентификатор кандидата.
        :return: Найденный кандидат.
        """
        pass


    def get_all_candidates(self) -> List[Candidate]:
        """
        Возвращает список всех кандидатов.
        :return: Список кандидатов.
        """
        pass


    def edit_candidate(self, candidate: Candidate) -> Candidate:
        """
        Редактирование кандидата.
        :param candidate: Изменяемый кандидат.
        :return: Измененный кандидат.
        """
        pass


    def delete_candidate(self, candidate_id: int) -> None:
        """
        Удаление кандидата.
        :param candidate_id: Уникальный идентификатор.
        """
        pass


    def get_total_candidates(self) -> int:
        """
        Возвращение общего количества кандидатов.
        """
        pass


    def accept_candidate(self, candidate_id: int) -> None:
        """
        Принимает кандидата в качестве нового сотрудника.
        Меняет статус кандидата на APPROVED.
        :param candidate_id: Уникальный идентификатор кандидата.
        """
        pass


    def reject_candidate(self, candidate_id: int) -> None:
        """
        Отклоняет кандидата.
        Меняет статус кандидата на REJECTED.
        :param candidate_id: Уникальный идентификатор кандидата.
        """
        pass