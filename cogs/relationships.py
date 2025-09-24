# Module-level debug: Confirm file is loaded
print("🔍 Модуль cogs.relationships загружен (файл найден)!")

import discord
from discord.ext import commands
import json
import os
import random
import ast  # Для безопасного парсинга rel_key
from typing import Dict, List
import traceback  # For error traces

# Lazy import: Import RelationshipSystem only when needed
RelationshipSystem = None


class RelationshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            global RelationshipSystem
            if RelationshipSystem is None:
                from Relationship_System import RelationshipSystem

                print("✅ Импорт RelationshipSystem успешен в __init__!")
            self.system = RelationshipSystem()
            print(f"✅ RelationshipCog инициализирован для {bot.user}!")
        except ImportError as e:
            print(f"❌ ImportError RelationshipSystem в __init__: {e}")
            traceback.print_exc()

            # Fallback: Dummy system for testing (remove in production)
            class DummySystem:
                def __init__(self):
                    self.characters = {}
                    self.relationships = {}

                def save_data(self):
                    pass

                def load_data(self):
                    pass

            self.system = DummySystem()
            print(
                "⚠️ Используется dummy RelationshipSystem (команды могут работать частично)"
            )
        except Exception as e:
            print(f"❌ Ошибка инициализации RelationshipCog: {e}")
            traceback.print_exc()
            raise  # Re-raise to prevent partial load

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

        # Debug: List commands after init
        print(
            "📝 Команды в RelationshipCog:", [cmd.name for cmd in self.get_commands()]
        )

    @commands.command(name="добавить")
    async def add_character(self, ctx, *, name: str):
        """Добавить нового персонажа"""
        name = name.strip()  # Удаляем лишние пробелы
        if not name:
            await ctx.send("❌ Имя не может быть пустым!")
            return
        if name in self.system.characters:
            await ctx.send(f"❌ Персонаж `{name}` уже существует!")
            return

        self.system.characters[name] = {
            "added_by": ctx.author.id,
            "added_date": ctx.message.created_at.isoformat(),
        }
        self.system.save_data()

        embed = discord.Embed(
            title="✅ Персонаж добавлен",
            description=f"Персонаж `{name}` успешно добавлен!",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)

    @commands.command(name="удалить")
    async def remove_character(self, ctx, *, name: str):
        """Удалить персонажа"""
        name = name.strip()
        if not name:
            await ctx.send("❌ Имя не может быть пустым!")
            return
        if name not in self.system.characters:
            await ctx.send(f"❌ Персонаж `{name}` не найден!")
            return

        del self.system.characters[name]
        # Удаляем все исходящие (name → other) и входящие (other → name) отношения
        to_remove = []
        for rel_key in list(self.system.relationships):
            try:
                chars = ast.literal_eval(rel_key)
                if name in chars:  # Either direction
                    to_remove.append(rel_key)
            except (ValueError, SyntaxError):
                continue
        for rel_key in to_remove:
            del self.system.relationships[rel_key]

        self.system.save_data()
        await ctx.send(f"✅ Персонаж `{name}` и все его отношения удалены!")

    @commands.command(name="персонажи")
    async def list_characters(self, ctx):
        """Показать список всех персонажей"""
        if not self.system.characters:
            await ctx.send("❌ Пока нет добавленных персонажей!")
            return

        characters = list(self.system.characters.keys())
        embed = discord.Embed(
            title="👥 Список персонажей",
            description=f"Всего персонажей: {len(characters)}\n\n"
            + "\n".join([f"• {char}" for char in sorted(characters)]),
            color=0x9370DB,
        )
        await ctx.send(embed=embed)

    @commands.command(name="бросок")
    async def roll_relationships(self, ctx):
        """Бросить кубы для определения отношений (теперь направленные)"""
        if len(self.system.characters) < 2:
            await ctx.send("❌ Нужно как минимум 2 персонажа!")
            return

        characters = list(self.system.characters.keys())
        relationships_created = 0

        for char1 in characters:
            for char2 in characters:
                if char1 == char2:  # No self-relation
                    continue

                rel_key = str((char1, char2))  # Directed: (from, to), no sorting

                if rel_key not in self.system.relationships:
                    roll = random.randint(1, 10)

                    self.system.relationships[rel_key] = {
                        "value": roll,
                        "description": self.relationship_descriptions[roll],
                        "rolled_by": ctx.author.id,
                        "roll_date": ctx.message.created_at.isoformat(),
                    }
                    relationships_created += 1

        self.system.save_data()

        embed = discord.Embed(
            title="🎲 Отношения определены!",
            description=f"Создано {relationships_created} направленных отношений.",
            color=0x0099FF,
        )
        await ctx.send(embed=embed)

    @commands.command(name="таблица")
    async def show_relationship_table(self, ctx):
        """Показать таблицу отношений (направленная матрица)"""
        if not self.system.relationships:
            await ctx.send("❌ Отношения еще не определены! Используйте `!бросок`")
            return

        characters = sorted(self.system.characters.keys())

        # Создаем таблицу: строки = from, столбцы = to
        table = "```\n"
        table += " " * 15
        for char in characters:
            table += f"{char[:8]:>8} "
        table += "\n" + "-" * (15 + 9 * len(characters)) + "\n"

        for char1 in characters:  # From
            table += f"{char1[:14]:<14} "
            for char2 in characters:  # To
                if char1 == char2:
                    table += "    —    "
                else:
                    rel_key = str((char1, char2))  # Directed from char1 to char2
                    if rel_key in self.system.relationships:
                        rel = self.system.relationships[rel_key]
                        table += f"    {rel['value']}    "
                    else:
                        table += "    ?    "
            table += "\n"
        table += "```"

        embed = discord.Embed(
            title="📊 Таблица отношений (направленная)",
            description=table,
            color=0xFFD700,
        )

        # Легенда
        legend = ""
        for value, desc in self.relationship_descriptions.items():
            legend += f"{value}: {desc}\n"

        embed.add_field(name="🎯 Легенда", value=legend, inline=False)
        embed.set_footer(text="Строки: отношение ОТ персонажа, Столбцы: К персонажу")
        await ctx.send(embed=embed)

    @commands.command(name="отношения")
    async def show_detailed_relationships(self, ctx, *, character_name: str = None):
        """Показать подробные отношения (только исходящие для конкретного персонажа)"""
        if not self.system.relationships:
            await ctx.send("❌ Отношения еще не определены!")
            return

        embed = discord.Embed(title="💞 Детальные отношения", color=0xFF69B4)

        if character_name:
            character_name = character_name.strip()
            if character_name not in self.system.characters:
                await ctx.send(f"❌ Персонаж `{character_name}` не найден!")
                return

            # Только исходящие отношения от character_name к другим
            relationships = []
            other_chars = [c for c in self.system.characters if c != character_name]
            for other_char in other_chars:
                rel_key = str((character_name, other_char))  # Directed: from → to
                if rel_key in self.system.relationships:
                    rel_data = self.system.relationships[rel_key]
                    relationships.append((other_char, rel_data))
                else:
                    relationships.append((other_char, None))  # No relation yet

            if not any(rel[1] for rel in relationships):
                embed.description = f"У {character_name} пока нет отношений."
            else:
                desc = f"Отношения **{character_name}** → другим:\n\n"
                for other_char, rel_data in sorted(
                    relationships,
                    key=lambda x: (x[1]["value"] if x[1] else 0) if x[1] else (0, x[0]),
                    reverse=True,
                ):
                    if rel_data:
                        desc += f"**{character_name} → {other_char}**: {rel_data['value']} - {rel_data['description']}\n"
                    else:
                        desc += f"**{character_name} → {other_char}**: Нет отношения\n"
                embed.description = desc
        else:
            # Все направленные отношения (from → to)
            desc = "Все отношения (от → к):\n\n"
            all_rels = []
            for rel_key, rel_data in self.system.relationships.items():
                try:
                    chars = ast.literal_eval(rel_key)
                    all_rels.append((chars[0], chars[1], rel_data))
                except (ValueError, SyntaxError):
                    continue
            for from_char, to_char, rel_data in sorted(
                all_rels, key=lambda x: x[2]["value"], reverse=True
            ):
                desc += f"**{from_char} → {to_char}**: {rel_data['value']} - {rel_data['description']}\n"
            embed.description = desc

        await ctx.send(embed=embed)

    @commands.command(name="перебросить")
    async def reroll_relationship(self, ctx, char1: str, char2: str):
        """Перебросить отношение от char1 к char2 (с логикой корректировки)"""
        char1 = char1.strip()
        char2 = char2.strip()
        if not char1 or not char2:
            await ctx.send("❌ Имена персонажей не могут быть пустыми!")
            return
        if char1 == char2:
            await ctx.send("❌ Нельзя перебросить отношение к себе!")
            return

        rel_key = str((char1, char2))  # Directed: from char1 to char2

        if rel_key not in self.system.relationships:
            await ctx.send(
                f"❌ Отношение от `{char1}` к `{char2}` не найдено! Используйте `!бросок` сначала."
            )
            return

        old_data = self.system.relationships[rel_key]
        old_value = old_data["value"]

        new_roll = random.randint(1, 10)
        # Логика корректировки
        if new_roll > old_value:
            final_value = min(10, old_value + 1)  # Увеличиваем на 1, макс 10
        elif new_roll == 1:
            final_value = max(1, old_value - 1)  # Уменьшаем на 1, мин 1


# Async setup function (required for Discord.py 2.x cog extensions)
async def setup(bot):
    await bot.add_cog(RelationshipCog(bot))
    print("✅ RelationshipCog добавлен через async setup!")
