import json
import os
from typing import Dict, List


class RelationshipSystem:
    def __init__(self):
        self.characters_file = "characters.json"
        self.relationships_file = "relationships.json"
        self.load_data()

    def load_data(self):
        """Загрузка данных из JSON файлов с обработкой ошибок"""
        try:
            # Загрузка персонажей
            if os.path.exists(self.characters_file):
                with open(self.characters_file, "r", encoding="utf-8") as f:
                    self.characters = json.load(f)
            else:
                self.characters = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Ошибка загрузки characters.json: {e}")
            self.characters = {}

        try:
            # Загрузка отношений
            if os.path.exists(self.relationships_file):
                with open(self.relationships_file, "r", encoding="utf-8") as f:
                    self.relationships = json.load(f)
            else:
                self.relationships = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Ошибка загрузки relationships.json: {e}")
            self.relationships = {}

    def save_data(self):
        """Сохранение данных в JSON файлы с обработкой ошибок"""
        try:
            with open(self.characters_file, "w", encoding="utf-8") as f:
                json.dump(self.characters, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Ошибка сохранения characters.json: {e}")

        try:
            with open(self.relationships_file, "w", encoding="utf-8") as f:
                json.dump(self.relationships, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Ошибка сохранения relationships.json: {e}")
