import random
from typing import Dict, Tuple

class RelationshipCalculator:
    def __init__(self):
        self.vinculum_descriptions = {
            1: "🔴 Равнодушие",
            2: "🔴 Слабые чувства", 
            3: "🟡 Условная верность",
            4: "🟡 Помощь без риска",
            5: "🟢 Уважение",
            6: "🟢 Сильные чувства",
            7: "🔵 Умеренный риск",
            8: "🔵 Ресурсы и влияние",
            9: "💖 Большая опасность",
            10: "💖 Жизнь и смерть",
        }
        
        self.vinculum_effects = {
            1: "Да пошел он. Равнодушие, хотя могут быть личные чувства.",
            2: "Слабые родственные чувства, но помощь только ради выгоды.",
            3: "Верность, пока не конфликтует с вашими планами.", 
            4: "Помощь, если нет риска и не расходится с мировоззрением.",
            5: "Уважение, помощь пока не становится рискованно.",
            6: "Сильные чувства, готовность помочь несмотря на неудобства.",
            7: "Умеренный риск, возможны убийства по кодексу этики.",
            8: "Предоставление ресурсов и помощи влиянием.",
            9: "Готовность на почти любые действия с большой опасностью.",
            10: "Легкая готовность убивать или быть убитым ради Побратима.",
        }

    def roll_vinculum(self) -> Tuple[int, str, str]:
        """Случайный бросок винкулума"""
        value = random.randint(1, 10)
        description = self.vinculum_descriptions[value]
        effect = self.vinculum_effects[value]
        return value, description, effect

    def reroll_vinculum(self, current_value: int) -> Tuple[int, str, str]:
        """Перебросить винкулум с логикой корректировки"""
        new_roll = random.randint(1, 10)
        
        if new_roll > current_value:
            final_value = min(10, current_value + 1)  # Увеличиваем на 1
        elif new_roll == 1:
            final_value = max(1, current_value - 1)  # Уменьшаем на 1
        else:
            final_value = current_value  # Без изменений

        description = self.vinculum_descriptions[final_value]
        effect = self.vinculum_effects[final_value]
        return final_value, description, effect

    def get_description(self, value: int) -> str:
        """Получить описание для числового значения винкулума"""
        return self.vinculum_descriptions.get(value, "❓ Неизвестно")

    def get_effect(self, value: int) -> str:
        """Получить эффект для числового значения винкулума"""
        return self.vinculum_effects.get(value, "❓ Эффект неизвестен")

    def get_all_descriptions(self) -> Dict[int, str]:
        """Получить все описания винкулумов"""
        return self.vinculum_descriptions.copy()

    def get_all_effects(self) -> Dict[int, str]:
        """Получить все эффекты винкулумов"""
        return self.vinculum_effects.copy()