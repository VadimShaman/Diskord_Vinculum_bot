import traceback
import discord
from discord.ext import commands
import json
import os
import random
import ast  # Для безопасного парсинга rel_key
from typing import Dict, List

# Debug: Test import before using
try:
    from Relationship_System import RelationshipSystem

    print("✅ Импорт RelationshipSystem успешен!")  # This will print on load
except ImportError as e:
    print(f"❌ Ошибка импорта RelationshipSystem: {e}")
    traceback.print_exc()  # Requires import traceback at top, but for simplicity, assume it's handled in main


class RelationshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.system = RelationshipSystem()
            print(
                f"✅ RelationshipCog инициализирован для {bot.user}!"
            )  # Confirm init success
        except Exception as e:
            print(f"❌ Ошибка инициализации RelationshipCog: {e}")
            traceback.print_exc()  # Full error if system fails
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
        # Удаляем все отношения с этим персонажем (безопасный парсинг ключей)
        to_remove = []
        for rel_key in list(
            self.system.relationships
        ):  # Use list() to avoid runtime modification
            try:
                chars = ast.literal_eval(rel_key)
                if name in chars:
                    to_remove.append(rel_key)
            except (ValueError, SyntaxError):
                # Если ключ поврежден, пропускаем
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
        """Бросить кубы для определения отношений"""
        if len(self.system.characters) < 2:
            await ctx.send("❌ Нужно как минимум 2 персонажа!")
            return

        characters = list(self.system.characters.keys())
        relationships_created = 0

        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters):
                if i >= j:  # Чтобы не дублировать отношения
                    continue

                rel_key = str(tuple(sorted([char1, char2])))

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
            description=f"Создано {relationships_created} новых отношений.",
            color=0x0099FF,
        )
        await ctx.send(embed=embed)

    @commands.command(name="таблица")
    async def show_relationship_table(self, ctx):
        """Показать таблицу отношений"""
        if not self.system.relationships:
            await ctx.send("❌ Отношения еще не определены! Используйте `!бросок`")
            return

        characters = sorted(self.system.characters.keys())

        # Создаем таблицу (примечание: длинные имена могут обрезаться)
        table = "```\n"
        table += " " * 15
        for char in characters:
            table += f"{char[:8]:>8} "
        table += "\n" + "-" * (15 + 9 * len(characters)) + "\n"

        for char1 in characters:
            table += f"{char1[:14]:<14} "
            for char2 in characters:
                if char1 == char2:
                    table += "    —    "
                else:
                    rel_key = str(tuple(sorted([char1, char2])))
                    if rel_key in self.system.relationships:
                        rel = self.system.relationships[rel_key]
                        table += f"    {rel['value']}    "
                    else:
                        table += "    ?    "
            table += "\n"
        table += "```"

        embed = discord.Embed(
            title="📊 Таблица отношений", description=table, color=0xFFD700
        )

        # Легенда
        legend = ""
        for value, desc in self.relationship_descriptions.items():
            legend += f"{value}: {desc}\n"

        embed.add_field(name="🎯 Легенда", value=legend, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="отношения")
    async def show_detailed_relationships(self, ctx, *, character_name: str = None):
        """Показать подробные отношения"""
        if not self.system.relationships:
            await ctx.send("❌ Отношения еще не определены!")
            return

        embed = discord.Embed(title="💞 Детальные отношения", color=0xFF69B4)

        if character_name:
            character_name = character_name.strip()
            if character_name not in self.system.characters:
                await ctx.send(f"❌ Персонаж `{character_name}` не найден!")
