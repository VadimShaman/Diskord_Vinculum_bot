import json
import os
import ast
from typing import Dict, Tuple, Optional, List

class RelationshipManager:
    def __init__(self, data_file: str = "relationships.json"):
        self.data_file = data_file
        self.relationships = {}
        self.load_data()

    def load_data(self) -> None:
        """Загрузка отношений из JSON файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.relationships = json.load(f)
            else:
                self.relationships = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Ошибка загрузки {self.data_file}: {e}")
            self.relationships = {}

    def save_data(self) -> None:
        """Сохранение отношений в JSON файл"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.relationships, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Ошибка сохранения {self.data_file}: {e}")

    def create_relationship(self, from_char: str, to_char: str, value: int, 
                          description: str, rolled_by: int, roll_date: str) -> None:
        """Создать направленное отношение"""
        rel_key = self._create_key(from_char, to_char)
        self.relationships[rel_key] = {
            "value": value,
            "description": description,
            "rolled_by": rolled_by,
            "roll_date": roll_date,
        }
        self.save_data()

    def get_relationship(self, from_char: str, to_char: str) -> Optional[dict]:
        """Получить отношение от одного персонажа к другому"""
        rel_key = self._create_key(from_char, to_char)
        return self.relationships.get(rel_key)

    def update_relationship(self, from_char: str, to_char: str, value: int, 
                           description: str) -> None:
        """Обновить существующее отношение"""
        rel_key = self._create_key(from_char, to_char)
        if rel_key in self.relationships:
            self.relationships[rel_key]["value"] = value
            self.relationships[rel_key]["description"] = description
            self.save_data()

    def remove_relationship(self, from_char: str, to_char: str) -> bool:
        """Удалить отношение"""
        rel_key = self._create_key(from_char, to_char)
        if rel_key in self.relationships:
            del self.relationships[rel_key]
            self.save_data()
            return True
        return False

    def remove_all_character_relationships(self, character_name: str) -> List[str]:
        """Удалить все отношения связанные с персонажем"""
        removed_keys = []
        for rel_key in list(self.relationships.keys()):
            try:
                chars = ast.literal_eval(rel_key)
                if character_name in chars:
                    removed_keys.append(rel_key)
                    del self.relationships[rel_key]
            except (ValueError, SyntaxError):
                continue
        if removed_keys:
            self.save_data()
        return removed_keys

    def get_outgoing_relationships(self, character_name: str) -> List[Tuple[str, dict]]:
        """Получить все исходящие отношения персонажа"""
        outgoing = []
        for rel_key, rel_data in self.relationships.items():
            try:
                from_char, to_char = ast.literal_eval(rel_key)
                if from_char == character_name:
                    outgoing.append((to_char, rel_data))
            except (ValueError, SyntaxError):
                continue
        return outgoing

    def get_incoming_relationships(self, character_name: str) -> List[Tuple[str, dict]]:
        """Получить все входящие отношения персонажа"""
        incoming = []
        for rel_key, rel_data in self.relationships.items():
            try:
                from_char, to_char = ast.literal_eval(rel_key)
                if to_char == character_name:
                    incoming.append((from_char, rel_data))
            except (ValueError, SyntaxError):
                continue
        return incoming

    def get_all_relationships(self) -> List[Tuple[str, str, dict]]:
        """Получить все отношения в системе"""
        all_rels = []
        for rel_key, rel_data in self.relationships.items():
            try:
                from_char, to_char = ast.literal_eval(rel_key)
                all_rels.append((from_char, to_char, rel_data))
            except (ValueError, SyntaxError):
                continue
        return all_rels

    def relationship_exists(self, from_char: str, to_char: str) -> bool:
        """Проверить существование отношения"""
        rel_key = self._create_key(from_char, to_char)
        return rel_key in self.relationships

    def _create_key(self, from_char: str, to_char: str) -> str:
        """Создать ключ для хранения отношения"""
        return str((from_char, to_char))

    def get_relationship_count(self) -> int:
        """Получить количество отношений"""
        return len(self.relationships)
    
    def create_vinculum(self, from_char: str, to_char: str, value: int, 
                       description: str, effect: str, rolled_by: int, roll_date: str) -> None:
        """Создать направленный винкулум"""
        rel_key = self._create_key(from_char, to_char)
        self.relationships[rel_key] = {
            "value": value,
            "description": description,
            "effect": effect,  # Добавляем эффект
            "rolled_by": rolled_by,
            "roll_date": roll_date,
            "type": "vinculum"  # Добавляем тип связи
        }
        self.save_data()