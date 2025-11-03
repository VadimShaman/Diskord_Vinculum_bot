import sys
import os

# Добавляем путь для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from CharacterManager import CharacterManager
    from RelationshipManager import RelationshipManager
    from RelationshipCalculator import RelationshipCalculator
except ImportError as e:
    print(f"[ERROR] Импорт модулей не удался: {e}")
    # Заглушки для тестирования
    class CharacterManager:
        def __init__(self): self.characters = {}
        def add_character(self, *args): return False
        def remove_character(self, *args): return False
        def character_exists(self, *args): return False
        def list_characters(self): return []
    
    class RelationshipManager:
        def __init__(self): self.relationships = {}
        def relationship_exists(self, *args): return False
        def create_vinculum(self, *args): pass
        def get_relationship(self, *args): return None
        def get_outgoing_relationships(self, *args): return []
        def get_incoming_relationships(self, *args): return []
        def get_all_relationships(self): return []
        def remove_all_character_relationships(self, *args): return []
    
    class RelationshipCalculator:
        def __init__(self): pass
        def roll_vinculum(self): return (1, "Тест", "Тест")
        def reroll_vinculum(self, x): return (x, "Тест", "Тест")
        def get_description(self, x): return "Тест"
        def get_effect(self, x): return "Тест"
        def get_all_descriptions(self): return {}
        def get_all_effects(self): return {}

class RelationshipSystem:
    def __init__(self):
        self.character_manager = CharacterManager()
        self.relationship_manager = RelationshipManager()
        self.calculator = RelationshipCalculator()
    
    def get_vinculum_descriptions(self):
        return self.calculator.get_all_descriptions()

    def get_vinculum_effects(self):
        return self.calculator.get_all_effects()
    
    def relationship_exists(self, from_char: str, to_char: str) -> bool:
        return self.relationship_manager.relationship_exists(from_char, to_char)
    
    def add_character(self, name: str, added_by: int, added_date: str) -> bool:
        return self.character_manager.add_character(name, added_by, added_date)

    def remove_character(self, name: str) -> bool:
        self.relationship_manager.remove_all_character_relationships(name)
        return self.character_manager.remove_character(name)

    def character_exists(self, name: str) -> bool:
        return self.character_manager.character_exists(name)

    def list_characters(self) -> list:
        return self.character_manager.list_characters()

    def create_relationship(self, from_char: str, to_char: str, value: int, 
                          description: str, rolled_by: int, roll_date: str) -> None:
        self.relationship_manager.create_relationship(
            from_char, to_char, value, description, rolled_by, roll_date
        )

    def get_relationship(self, from_char: str, to_char: str):
        return self.relationship_manager.get_relationship(from_char, to_char)

    def get_outgoing_relationships(self, character_name: str):
        return self.relationship_manager.get_outgoing_relationships(character_name)

    def get_incoming_relationships(self, character_name: str):
        return self.relationship_manager.get_incoming_relationships(character_name)

    def get_all_relationships(self):
        return self.relationship_manager.get_all_relationships()

    def roll_all_vinculums(self, rolled_by: int, roll_date: str) -> int:
        characters = self.character_manager.list_characters()
        vinculums_created = 0

        for from_char in characters:
            for to_char in characters:
                if from_char == to_char:
                    continue
            
                if not self.relationship_manager.relationship_exists(from_char, to_char):
                    value, description, effect = self.calculator.roll_vinculum()
                    self.create_vinculum(
                        from_char, to_char, value, description, effect, rolled_by, roll_date
                    )
                    vinculums_created += 1

        return vinculums_created

    def create_vinculum(self, from_char: str, to_char: str, value: int, 
                       description: str, effect: str, rolled_by: int, roll_date: str) -> None:
        self.relationship_manager.create_vinculum(
            from_char, to_char, value, description, effect, rolled_by, roll_date
        )

    def save_data(self) -> None:
        self.character_manager.save_data()
        self.relationship_manager.save_data()

    def load_data(self) -> None:
        self.character_manager.load_data()
        self.relationship_manager.load_data()

    @property
    def characters(self):
        return self.character_manager.characters

    @property
    def relationships(self):
        return self.relationship_manager.relationships

    def get_relationship_count(self) -> int:
        return self.relationship_manager.get_relationship_count()

    def roll_single_vinculum(self, from_char: str, to_char: str, rolled_by: int, roll_date: str) -> tuple:
        """Создать винкулум между двумя конкретными персонажами"""
        if from_char == to_char:
            return None, "❌ Нельзя создать винкулум между одним и тем же персонажем!"
        
        if not self.character_exists(from_char):
            return None, f"❌ Персонаж `{from_char}` не найден!"
        
        if not self.character_exists(to_char):
            return None, f"❌ Персонаж `{to_char}` не найден!"
        
        # Бросаем винкулум
        value, description, effect = self.calculator.roll_vinculum()
        
        # Создаем или обновляем отношение
        self.create_vinculum(from_char, to_char, value, description, effect, rolled_by, roll_date)
        
        return (value, description, effect), "✅ Винкулум создан!"

    def set_vinculum_value(self, from_char: str, to_char: str, value: int, set_by: int, set_date: str) -> tuple:
        """Установить конкретное значение винкулума между двумя персонажами"""
        if from_char == to_char:
            return None, "❌ Нельзя создать винкулум между одним и тем же персонажем!"
        
        if not self.character_exists(from_char):
            return None, f"❌ Персонаж `{from_char}` не найден!"
        
        if not self.character_exists(to_char):
            return None, f"❌ Персонаж `{to_char}` не найден!"
        
        # Проверяем допустимость значения
        if value < 1 or value > 10:
            return None, "❌ Значение винкулума должно быть от 1 до 10!"
        
        # Получаем описание и эффект для указанного значения
        description = self.calculator.get_description(value)
        effect = self.calculator.get_effect(value)
        
        # Создаем или обновляем отношение
        self.create_vinculum(from_char, to_char, value, description, effect, set_by, set_date)
        
        return (value, description, effect), "✅ Винкулум установлен!"