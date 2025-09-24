import discord
from discord.ext import commands
import random


class RelationshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.system = RelationshipSystem()
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

    @commands.command(name="добавить")
    async def add_character(self, ctx, *, name: str):
        """Добавить нового персонажа"""
        if name in self.system.characters:
            await ctx.send(f"Персонаж `{name}` уже существует!")
            return

        self.system.characters[name] = {
            "added_by": ctx.author.id,
            "added_date": str(ctx.message.created_at),
        }
        self.system.save_data()

        embed = discord.Embed(
            title="✅ Персонаж добавлен",
            description=f"Персонаж `{name}` успешно добавлен в систему!",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)

    @commands.command(name="удалить")
    async def remove_character(self, ctx, *, name: str):
        """Удалить персонажа"""
        if name not in self.system.characters:
            await ctx.send(f"Персонаж `{name}` не найден!")
            return

        del self.system.characters[name]
        # Удаляем все отношения с этим персонажем
        for rel_key in list(self.system.relationships.keys()):
            if name in rel_key:
                del self.system.relationships[rel_key]

        self.system.save_data()
        await ctx.send(f"Персонаж `{name}` и все его отношения удалены!")

    @commands.command(name="бросок")
    async def roll_relationships(self, ctx):
        """Бросить кубы для определения отношений"""
        if len(self.system.characters) < 2:
            await ctx.send("Нужно как минимум 2 персонажа для определения отношений!")
            return

        characters = list(self.system.characters.keys())
        relationships_created = 0

        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters):
                if i >= j:  # Чтобы не дублировать отношения A-B и B-A
                    continue

                # Создаем ключ для отношений (сортированный, чтобы A-B и B-A были одинаковыми)
                rel_key = tuple(sorted([char1, char2]))

                if str(rel_key) not in self.system.relationships:
                    # Бросаем d10 для отношения
                    roll = random.randint(1, 10)

                    self.system.relationships[str(rel_key)] = {
                        "value": roll,
                        "description": self.relationship_descriptions[roll],
                        "rolled_by": ctx.author.id,
                        "roll_date": str(ctx.message.created_at),
                    }
                    relationships_created += 1

        self.system.save_data()

        embed = discord.Embed(
            title="🎲 Отношения определены!",
            description=f"Создано {relationships_created} новых отношений между персонажами.",
            color=0x0099FF,
        )
        await ctx.send(embed=embed)

    @commands.command(name="таблица")
    async def show_relationship_table(self, ctx):
        """Показать таблицу отношений"""
        if not self.system.relationships:
            await ctx.send("Отношения еще не определены! Используйте команду `!бросок`")
            return

        characters = sorted(self.system.characters.keys())
        if len(characters) == 0:
            await ctx.send("Нет добавленных персонажей!")
            return

        # Создаем таблицу
        table = "```\n"
        table += " " * 15
        for char in characters:
            table += f"{char[:8]:>8} "  # Обрезаем длинные имена
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

        # Добавляем легенду
        legend = ""
        for value, desc in self.relationship_descriptions.items():
            legend += f"{value}: {desc}\n"

        embed.add_field(name="🎯 Легенда", value=legend, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="отношения")
    async def show_detailed_relationships(self, ctx, *, character_name: str = None):
        """Показать подробные отношения конкретного персонажа"""
        if character_name and character_name not in self.system.characters:
            await ctx.send(f"Персонаж `{character_name}` не найден!")
            return

        if not self.system.relationships:
            await ctx.send("Отношения еще не определены!")
            return

        embed = discord.Embed(title="💞 Детальные отношения", color=0xFF69B4)

        if character_name:
            # Показать отношения для конкретного персонажа
            relationships = []
            for rel_key, rel_data in self.system.relationships.items():
                chars = eval(rel_key)  # Безопасно т.к. наши ключи - кортежи
                if character_name in chars:
                    other_char = chars[0] if chars[1] == character_name else chars[1]
                    relationships.append((other_char, rel_data))

            if not relationships:
                embed.description = (
                    f"У {character_name} пока нет определенных отношений."
                )
            else:
                desc = ""
                for other_char, rel_data in sorted(
                    relationships, key=lambda x: x[1]["value"], reverse=True
                ):
                    desc += f"**{other_char}**: {rel_data['value']} - {rel_data['description']}\n"
                embed.description = f"Отношения **{character_name}**:\n\n{desc}"
        else:
            # Показать все отношения
            desc = ""
            for rel_key, rel_data in sorted(
                self.system.relationships.items(),
                key=lambda x: x[1]["value"],
                reverse=True,
            ):
                chars = eval(rel_key)
                desc += f"**{chars[0]}** ❤ **{chars[1]}**: {rel_data['value']} - {rel_data['description']}\n"

            embed.description = desc

        await ctx.send(embed=embed)

    @commands.command(name="персонажи")
    async def list_characters(self, ctx):
        """Показать список всех персонажей"""
        if not self.system.characters:
            await ctx.send("Пока нет добавленных персонажей!")
            return

        characters = list(self.system.characters.keys())
        embed = discord.Embed(
            title="👥 Список персонажей",
            description=f"Всего персонажей: {len(characters)}\n\n"
            + "\n".join([f"• {char}" for char in sorted(characters)]),
            color=0x9370DB,
        )
        await ctx.send(embed=embed)

    @commands.command(name="перебросить")
    async def reroll_relationship(self, ctx, char1: str, char2: str):
        """Перебросить отношение между двумя персонажами"""
        rel_key = str(tuple(sorted([char1, char2])))

        if rel_key not in self.system.relationships:
            await ctx.send(f"Отношения между `{char1}` и `{char2}` не найдены!")
            return

        # Новый бросок
        new_roll = random.randint(1, 10)
        old_roll = self.system.relationships[rel_key]["value"]

        self.system.relationships[rel_key].update(
            {
                "value": new_roll,
                "description": self.relationship_descriptions[new_roll],
                "rerolled_by": ctx.author.id,
                "reroll_date": str(ctx.message.created_at),
            }
        )
        self.system.save_data()

        embed = discord.Embed(
            title="🎲 Отношение переброшено!",
            description=f"**{char1}** ❤ **{char2}**\nСтарое: {old_roll} → Новое: {new_roll}\n{self.relationship_descriptions[new_roll]}",
            color=0xFFA500,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RelationshipCog(bot))
