from CharacterManager import CharacterManager
from RelationshipManager import RelationshipManager
from RelationshipCalculator import RelationshipCalculator


class RelationshipSystem:
    def __init__(self):
        self.character_manager = CharacterManager()
        self.relationship_manager = RelationshipManager()
        self.calculator = RelationshipCalculator()

    # Делегирование методов для персонажей
    def add_character(self, name: str, added_by: int, added_date: str) -> bool:
        return self.character_manager.add_character(name, added_by, added_date)

    def remove_character(self, name: str) -> bool:
        # Удаляем все отношения персонажа перед удалением
        self.relationship_manager.remove_all_character_relationships(name)
        return self.character_manager.remove_character(name)

    def character_exists(self, name: str) -> bool:
        return self.character_manager.character_exists(name)

    def list_characters(self) -> list:
        return self.character_manager.list_characters()

    # Делегирование методов для отношений
    def create_relationship(
        self,
        from_char: str,
        to_char: str,
        value: int,
        description: str,
        rolled_by: int,
        roll_date: str,
    ) -> None:
        self.relationship_manager.create_relationship(
            from_char, to_char, value, description, rolled_by, roll_date
        )

    def get_relationship(self, from_char: str, to_char: str):
        return self.relationship_manager.get_relationship(from_char, to_char)

    def get_outgoing_relationships(self, character_name: str):
        return self.relationship_manager.get_outgoing_relationships(character_name)

    def get_all_relationships(self):
        return self.relationship_manager.get_all_relationships()

    # Комплексные операции
    def roll_all_relationships(self, rolled_by: int, roll_date: str) -> int:
        """Создать отношения между всеми персонажами"""
        characters = self.character_manager.list_characters()
        relationships_created = 0

        for from_char in characters:
            for to_char in characters:
                if from_char == to_char:
                    continue

                if not self.relationship_manager.relationship_exists(
                    from_char, to_char
                ):
                    value, description = self.calculator.roll_relationship()
                    self.create_relationship(
                        from_char, to_char, value, description, rolled_by, roll_date
                    )
                    relationships_created += 1

        return relationships_created

    def save_data(self) -> None:
        """Сохранить все данные"""
        self.character_manager.save_data()
        self.relationship_manager.save_data()

    def load_data(self) -> None:
        """Загрузить все данные"""
        self.character_manager.load_data()
        self.relationship_manager.load_data()

    # Свойства для обратной совместимости
    @property
    def characters(self):
        return self.character_manager.characters

    @property
    def relationships(self):
        return self.relationship_manager.relationships
