import random
from typing import Dict, Tuple


class RelationshipCalculator:
    def __init__(self):
        self.relationship_descriptions = {
            1: "🔴 Вражда",
            2: "🔴 Конфликт",
            3: "🟡 Напряжение",
            4: "🟡 Нейтрально",
            5: "🟢 Дружелюбие",
            6: "🟢 Симпатия",
            7: "🔵 Дружба",
            8: "🔵 Близость",
            9: "💖 Любовь",
            10: "💖 Душа",
        }

    def roll_relationship(self) -> Tuple[int, str]:
        """Случайный бросок отношения"""
        value = random.randint(1, 10)
        description = self.relationship_descriptions[value]
        return value, description

    def reroll_relationship(self, current_value: int) -> Tuple[int, str]:
        """Перебросить отношение с логикой корректировки"""
        new_roll = random.randint(1, 10)

        if new_roll > current_value:
            final_value = min(10, current_value + 1)  # Увеличиваем на 1
        elif new_roll == 1:
            final_value = max(1, current_value - 1)  # Уменьшаем на 1
        else:
            final_value = current_value  # Оставляем без изменений

        description = self.relationship_descriptions[final_value]
        return final_value, description

    def get_description(self, value: int) -> str:
        """Получить описание для числового значения отношения"""
        return self.relationship_descriptions.get(value, "❓ Неизвестно")

    def get_all_descriptions(self) -> Dict[int, str]:
        """Получить все описания отношений"""
        return self.relationship_descriptions.copy()
