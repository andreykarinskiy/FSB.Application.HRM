import json
import os
from pathlib import Path
from typing import List, Dict

from hrm.core.model import Candidate, CandidateStatus, CandidateSex


class UseCases:
    """
    Бизнес-логика приложения.
    """
    
    _storage_file = Path.home() / ".hrm" / "candidates.json"
    
    def __init__(self):
        """Инициализация in-memory хранилища"""
        self._load_data()

    def _load_data(self) -> None:
        """Загружает данные из файла в память"""
        if self._storage_file.exists():
            try:
                with open(self._storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    candidates_dict = {}
                    for k, v in data.get("candidates", {}).items():
                        # Преобразуем enum из значений обратно в enum
                        if "status" in v:
                            v["status"] = CandidateStatus(v["status"])
                        if "sex" in v and v["sex"] is not None:
                            v["sex"] = CandidateSex(v["sex"])
                        candidates_dict[int(k)] = Candidate(**v)
                    self._candidates: Dict[int, Candidate] = candidates_dict
                    self._next_id: int = data.get("next_id", 1)
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                self._candidates: Dict[int, Candidate] = {}
                self._next_id: int = 1
        else:
            self._candidates: Dict[int, Candidate] = {}
            self._next_id: int = 1

    def _save_data(self) -> None:
        """Сохраняет данные из памяти в файл"""
        self._storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Преобразуем Candidate в словарь для JSON
        candidates_dict = {}
        for candidate_id, candidate in self._candidates.items():
            candidate_dict = candidate.model_dump()
            # Преобразуем enum в их значения для JSON
            if candidate_dict.get("status"):
                candidate_dict["status"] = candidate.status.value
            if candidate_dict.get("sex"):
                candidate_dict["sex"] = candidate.sex.value
            candidates_dict[str(candidate_id)] = candidate_dict
        
        data = {
            "candidates": candidates_dict,
            "next_id": self._next_id
        }
        
        with open(self._storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register_candidate(self, candidate: Candidate) -> int:
        """
        Регистрирует нового кандидата.
        :return: Идентификатор кандидата.
        """
        candidate_id = self._next_id
        self._next_id += 1
        
        # Создаем копию кандидата с установленным ID
        candidate_with_id = candidate.model_copy(update={"id": candidate_id})
        self._candidates[candidate_id] = candidate_with_id
        
        self._save_data()
        
        return candidate_id

    def get_candidate(self, candidate_id: int) -> Candidate:
        """
        Возвращает существующего кандидата.
        :param candidate_id: Идентификатор кандидата.
        :return: Найденный кандидат.
        :raises ValueError: Если кандидат с указанным ID не найден.
        """
        if candidate_id not in self._candidates:
            raise ValueError(f"Кандидат с ID {candidate_id} не найден")
        
        return self._candidates[candidate_id]


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