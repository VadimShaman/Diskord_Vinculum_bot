import json
import os
from typing import Dict, Optional

class CharacterManager:
    def __init__(self, data_file: str = "characters.json"):
        self.data_file = data_file
        self.characters = {}
        self.load_data()

    def load_data(self) -> None:
        """Загрузка персонажей из JSON файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.characters = json.load(f)
            else:
                self.characters = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Ошибка загрузки {self.data_file}: {e}")
            self.characters = {}

    def save_data(self) -> None:
        """Сохранение персонажей в JSON файл"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.characters, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Ошибка сохранения {self.data_file}: {e}")

    def add_character(self, name: str, added_by: int, added_date: str) -> bool:
        """Добавить нового персонажа"""
        if name in self.characters:
            return False
        self.characters[name] = {
            "added_by": added_by,
            "added_date": added_date,
        }
        self.save_data()
        return True

    def remove_character(self, name: str) -> bool:
        """Удалить персонажа"""
        if name not in self.characters:
            return False
        del self.characters[name]
        self.save_data()
        return True

    def get_character(self, name: str) -> Optional[dict]:
        """Получить информацию о персонаже"""
        return self.characters.get(name)

    def list_characters(self) -> list:
        """Получить список всех персонажей"""
        return list(self.characters.keys())

    def character_exists(self, name: str) -> bool:
        """Проверить существование персонажа"""
        return name in self.characters

    def get_character_count(self) -> int:
        """Получить количество персонажей"""
        return len(self.characters)