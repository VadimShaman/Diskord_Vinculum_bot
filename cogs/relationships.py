import discord
from discord.ext import commands
import random
import ast
import traceback
import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Импорт должен быть ВНЕ класса
try:
    from RelationshipSystem import RelationshipSystem
    print("[SUCCESS] Импорт RelationshipSystem успешен!")
except ImportError as e:
    print(f"[ERROR] Ошибка импорта RelationshipSystem: {e}")
    # Fallback: попробуем импортировать компоненты по отдельности
    try:
        from CharacterManager import CharacterManager
        from RelationshipManager import RelationshipManager  
        from RelationshipCalculator import RelationshipCalculator
        print("[SUCCESS] Импорт компонентов успешен!")
    except ImportError as e2:
        print(f"[ERROR] Импорт компонентов тоже провалился: {e2}")
        traceback.print_exc()
        raise

class RelationshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.system = RelationshipSystem()
            
            # Теперь используем винкулумы
            self.vinculum_descriptions = self.system.calculator.get_all_descriptions()
            self.vinculum_effects = self.system.calculator.get_all_effects()
            print("[SUCCESS] RelationshipCog инициализирован!")
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации RelationshipCog: {e}")
            traceback.print_exc()
            raise

    @commands.command(name="добавить")
    async def add_character(self, ctx, *, name: str):
        """Добавить нового персонажа"""
        name = name.strip()
        if not name:
            await ctx.send("[ERROR] Имя не может быть пустым!")
            return
            
        if self.system.character_exists(name):
            await ctx.send(f"[ERROR] Персонаж `{name}` уже существует!")
            return
        
        success = self.system.add_character(name, ctx.author.id, ctx.message.created_at.isoformat())
        if success:
            embed = discord.Embed(
                title="[SUCCESS] Персонаж добавлен",
                description=f"Персонаж `{name}` успешно добавлен!",
                color=0x00FF00,
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"[ERROR] Не удалось добавить персонажа `{name}`!")

    @commands.command(name="удалить")
    async def remove_character(self, ctx, *, name: str):
        """Удалить персонажа"""
        name = name.strip()
        if not name:
            await ctx.send("[ERROR] Имя не может быть пустым!")
            return
            
        if not self.system.character_exists(name):
            await ctx.send(f"[ERROR] Персонаж `{name}` не найден!")
            return

        success = self.system.remove_character(name)
        if success:
            await ctx.send(f"[SUCCESS] Персонаж `{name}` и все его отношения удалены!")
        else:
            await ctx.send(f"[ERROR] Не удалось удалить персонажа `{name}`!")

    @commands.command(name="персонажи")
    async def list_characters(self, ctx):
        """Показать список всех персонажей"""
        characters = self.system.list_characters()
        if not characters:
            await ctx.send("[ERROR] Пока нет добавленных персонажей!")
            return

        embed = discord.Embed(
            title="[LIST] Список персонажей",
            description=f"Всего персонажей: {len(characters)}\n\n" +
            "\n".join([f"• {char}" for char in sorted(characters)]),
            color=0x9370DB,
        )
        await ctx.send(embed=embed)

    @commands.command(name="бросок")
    async def roll_vinculums(self, ctx):
        """Бросить кубы для определения винкулумов"""
        if self.system.get_character_count() < 2:
            await ctx.send("[ERROR] Нужно как минимум 2 персонажа!")
            return

        vinculums_created = self.system.roll_all_vinculums(ctx.author.id, ctx.message.created_at.isoformat())

        embed = discord.Embed(
            title="[SUCCESS] Винкулумы определены!",
            description=f"Создано {vinculums_created} направленных винкулумов.",
            color=0x0099FF,
        )
        await ctx.send(embed=embed)

    @commands.command(name="таблица")
    async def show_vinculum_table(self, ctx):
        """Показать таблицу винкулумов (направленная матрица)"""
        if self.system.get_relationship_count() == 0:
            await ctx.send("[ERROR] Винкулумы еще не определены! Используйте `/бросок`")
            return

        characters = sorted(self.system.list_characters())

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
                    rel = self.system.get_relationship(char1, char2)
                    if rel:
                        table += f"    {rel['value']}    "
                    else:
                        table += "    ?    "
            table += "\n"
        table += "```"

        embed = discord.Embed(
            title="[TABLE] Таблица винкулумов (направленная)",
            description=table,
            color=0xFFD700,
        )

        # Легенда
        legend = ""
        for value, desc in self.vinculum_descriptions.items():
            legend += f"{value}: {desc}\n"

        embed.add_field(name="[INFO] Значения винкулума", value=legend, inline=False)
        embed.set_footer(text="Строки: винкулум ОТ персонажа, Столбцы: К персонажу")
        await ctx.send(embed=embed)

    @commands.command(name="винкулум")
    async def show_vinculum_details(self, ctx, char1: str = None, char2: str = None):
        """Показать подробные винкулумы"""
        if self.system.get_relationship_count() == 0:
            await ctx.send("[ERROR] Винкулумы еще не определены!")
            return

        embed = discord.Embed(title="[INFO] Детальные винкулумы", color=0xFF69B4)

        if char1 and char2:
            # Конкретный винкулум между двумя персонажами
            char1 = char1.strip()
            char2 = char2.strip()
            
            if not self.system.character_exists(char1):
                await ctx.send(f"[ERROR] Персонаж `{char1}` не найден!")
                return
            if not self.system.character_exists(char2):
                await ctx.send(f"[ERROR] Персонаж `{char2}` не найден!")
                return

            rel = self.system.get_relationship(char1, char2)
            if rel:
                embed.description = f"**{char1} → {char2}**"
                embed.add_field(
                    name=f"Уровень {rel['value']}: {rel['description']}",
                    value=rel.get('effect', 'Эффект не указан'),
                    inline=False
                )
            else:
                embed.description = f"Винкулум от `{char1}` к `{char2}` не найден!"
                
        elif char1:
            # Все исходящие винкулумы персонажа
            char1 = char1.strip()
            if not self.system.character_exists(char1):
                await ctx.send(f"[ERROR] Персонаж `{char1}` не найден!")
                return

            outgoing = self.system.get_outgoing_relationships(char1)
            if not outgoing:
                embed.description = f"У {char1} пока нет исходящих винкулумов."
            else:
                desc = f"Исходящие винкулумы **{char1}** → другим:\n\n"
                for to_char, rel_data in sorted(outgoing, key=lambda x: x[1]['value'], reverse=True):
                    desc += f"**→ {to_char}**: {rel_data['value']} - {rel_data['description']}\n"
                embed.description = desc
                
                # Добавляем входящие винкулумы
                incoming = self.system.get_incoming_relationships(char1)
                if incoming:
                    incoming_desc = f"Входящие винкулумы к **{char1}**:\n\n"
                    for from_char, rel_data in sorted(incoming, key=lambda x: x[1]['value'], reverse=True):
                        incoming_desc += f"**{from_char} →**: {rel_data['value']} - {rel_data['description']}\n"
                    embed.add_field(name="Входящие", value=incoming_desc, inline=False)
        else:
            # Все винкулумы
            all_rels = self.system.get_all_relationships()
            if not all_rels:
                embed.description = "Пока нет созданных винкулумов!"
            else:
                desc = "Все винкулумы (от → к):\n\n"
                for from_char, to_char, rel_data in sorted(all_rels, key=lambda x: x[2]['value'], reverse=True):
                    desc += f"**{from_char} → {to_char}**: {rel_data['value']} - {rel_data['description']}\n"
                embed.description = desc

        await ctx.send(embed=embed)

    @commands.command(name="перебросить")
    async def reroll_vinculum(self, ctx, char1: str, char2: str):
        """Перебросить винкулум от char1 к char2"""
        char1 = char1.strip()
        char2 = char2.strip()
        if not char1 or not char2:
            await ctx.send("[ERROR] Имена персонажей не могут быть пустыми!")
            return
        if char1 == char2:
            await ctx.send("[ERROR] Нельзя перебросить винкулум к себе!")
            return

        old_rel = self.system.get_relationship(char1, char2)
        if not old_rel:
            await ctx.send(f"[ERROR] Винкулум от `{char1}` к `{char2}` не найден!")
            return

        old_value = old_rel["value"]
        new_value, new_description, new_effect = self.system.calculator.reroll_vinculum(old_value)
        
        # Обновляем винкулум
        self.system.create_vinculum(
            char1, char2, new_value, new_description, new_effect, 
            ctx.author.id, ctx.message.created_at.isoformat()
        )

        embed = discord.Embed(
            title="[SUCCESS] Винкулум переброшен!",
            description=f"**{char1} → {char2}**\nБыло: {old_value} | Стало: {new_value}",
            color=0xFFA500,
        )
        embed.add_field(
            name=f"Уровень {new_value}: {new_description}",
            value=new_effect,
            inline=False
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RelationshipCog(bot))
    print("[SUCCESS] RelationshipCog добавлен через async setup!")