import json
import os
import sqlite3
import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict

from hrm.core.model import Candidate, CandidateStatus, CandidateSex


class CandidateRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Candidate]:
        pass

    @abstractmethod
    def get_by_id(self, candidate_id: int) -> Candidate | None:
        pass

    @abstractmethod
    def insert_or_update(self, candidate: Candidate) -> int:
        pass

    @abstractmethod
    def delete(self, candidate_id: int) -> None:
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Очищает репозиторий от всех данных"""
        pass


class SqliteCandidateRepository(CandidateRepository):
    """
    Репозиторий для хранения кандидатов в DB Sqlite.
    """
    
    def __init__(self, db_file: Path = None):
        """
        Инициализация репозитория.
        :param db_file: Путь к файлу базы данных. Если не указан, используется переменная окружения HRM_DB_PATH,
                        а при её отсутствии - ~/.hrm/candidates.db
        """
        if db_file is None:
            # Проверяем переменную окружения HRM_DB_PATH
            env_db_path = os.getenv("HRM_DB_PATH")
            if env_db_path:
                db_file = Path(env_db_path)
            else:
                db_file = Path.home() / ".hrm" / "candidates.db"
        self._db_file = db_file
        self._init_database()
    
    def _init_database(self) -> None:
        """Создает таблицу candidates, если её нет"""
        self._db_file.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone TEXT,
                    birth_date TEXT,
                    sex INTEGER,
                    status INTEGER NOT NULL,
                    comments TEXT
                )
            """)
            conn.commit()
    
    def _row_to_candidate(self, row: tuple) -> Candidate:
        """
        Преобразует строку из БД в объект Candidate.
        :param row: Кортеж (id, first_name, last_name, phone, birth_date, sex, status, comments)
        :return: Объект Candidate
        """
        candidate_id, first_name, last_name, phone, birth_date_str, sex_value, status_value, comments = row
        
        # Преобразуем birth_date из строки в datetime
        birth_date = None
        if birth_date_str:
            birth_date = datetime.datetime.fromisoformat(birth_date_str)
        
        # Преобразуем enum значения
        sex = CandidateSex(sex_value) if sex_value is not None else None
        status = CandidateStatus(status_value)
        
        return Candidate(
            id=candidate_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            sex=sex,
            status=status,
            comments=comments
        )
    
    def get_all(self) -> List[Candidate]:
        """Возвращает список всех кандидатов"""
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, first_name, last_name, phone, birth_date, sex, status, comments
                FROM candidates
                ORDER BY id
            """)
            rows = cursor.fetchall()
            return [self._row_to_candidate(row) for row in rows]
    
    def get_by_id(self, candidate_id: int) -> Candidate | None:
        """Возвращает кандидата по ID или None, если не найден"""
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, first_name, last_name, phone, birth_date, sex, status, comments
                FROM candidates
                WHERE id = ?
            """, (candidate_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_candidate(row)
            return None
    
    def insert_or_update(self, candidate: Candidate) -> int:
        """
        Вставляет нового кандидата или обновляет существующего.
        :param candidate: Кандидат для вставки/обновления
        :return: ID кандидата
        """
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            
            # Преобразуем данные для сохранения
            birth_date_str = candidate.birth_date.isoformat() if candidate.birth_date else None
            sex_value = candidate.sex.value if candidate.sex else None
            status_value = candidate.status.value
            
            if candidate.id is None:
                # Вставка нового кандидата
                cursor.execute("""
                    INSERT INTO candidates (first_name, last_name, phone, birth_date, sex, status, comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    candidate.first_name,
                    candidate.last_name,
                    candidate.phone,
                    birth_date_str,
                    sex_value,
                    status_value,
                    candidate.comments
                ))
                candidate_id = cursor.lastrowid
            else:
                # Обновление существующего кандидата
                candidate_id = candidate.id
                cursor.execute("""
                    UPDATE candidates
                    SET first_name = ?, last_name = ?, phone = ?, birth_date = ?, 
                        sex = ?, status = ?, comments = ?
                    WHERE id = ?
                """, (
                    candidate.first_name,
                    candidate.last_name,
                    candidate.phone,
                    birth_date_str,
                    sex_value,
                    status_value,
                    candidate.comments,
                    candidate_id
                ))
            
            conn.commit()
            return candidate_id
    
    def delete(self, candidate_id: int) -> None:
        """Удаляет кандидата по ID"""
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
            conn.commit()
    
    def clear_all(self) -> None:
        """Очищает репозиторий от всех данных"""
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM candidates")
            conn.commit()


class JsonCandidateRepository(CandidateRepository):
    """Репозиторий для хранения кандидатов в JSON-файле"""
    
    def __init__(self, storage_file: Path = None):
        """
        Инициализация репозитория.
        :param storage_file: Путь к файлу хранилища. Если не указан, используется ~/.hrm/candidates.json
        """
        self._storage_file = storage_file or (Path.home() / ".hrm" / "candidates.json")
        self._candidates: Dict[int, Candidate] = {}
        self._next_id: int = 1
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
                        # Преобразуем строку обратно в datetime
                        if "birth_date" in v and v["birth_date"] is not None:
                            from datetime import datetime
                            v["birth_date"] = datetime.fromisoformat(v["birth_date"])
                        candidates_dict[int(k)] = Candidate(**v)
                    self._candidates = candidates_dict
                    self._next_id = data.get("next_id", 1)
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                self._candidates = {}
                self._next_id = 1
        else:
            self._candidates = {}
            self._next_id = 1

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
            # Преобразуем datetime в строку для JSON
            if candidate_dict.get("birth_date"):
                candidate_dict["birth_date"] = candidate.birth_date.isoformat() if candidate.birth_date else None
            candidates_dict[str(candidate_id)] = candidate_dict
        
        data = {
            "candidates": candidates_dict,
            "next_id": self._next_id
        }
        
        with open(self._storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[Candidate]:
        """Возвращает список всех кандидатов"""
        return list(self._candidates.values())

    def get_by_id(self, candidate_id: int) -> Candidate | None:
        """Возвращает кандидата по ID или None, если не найден"""
        return self._candidates.get(candidate_id)

    def insert_or_update(self, candidate: Candidate) -> int:
        """
        Вставляет нового кандидата или обновляет существующего.
        :param candidate: Кандидат для вставки/обновления
        :return: ID кандидата
        """
        if candidate.id is None:
            # Новый кандидат - генерируем ID
            candidate_id = self._next_id
            self._next_id += 1
            candidate_with_id = candidate.model_copy(update={"id": candidate_id})
            self._candidates[candidate_id] = candidate_with_id
        else:
            # Обновление существующего кандидата
            candidate_id = candidate.id
            self._candidates[candidate_id] = candidate
        
        self._save_data()
        return candidate_id

    def delete(self, candidate_id: int) -> None:
        """Удаляет кандидата по ID"""
        if candidate_id in self._candidates:
            del self._candidates[candidate_id]
            self._save_data()

    def clear_all(self) -> None:
        """Очищает репозиторий от всех данных"""
        self._candidates = {}
        self._next_id = 1
        self._save_data()
