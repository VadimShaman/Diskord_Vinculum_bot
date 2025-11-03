import discord
from discord.ext import commands
from discord import app_commands
import random
import traceback
import sys
import os
from Relationship_System.CharacterManager import CharacterManager
from Relationship_System.RelationshipManager import RelationshipManager  
from Relationship_System.RelationshipCalculator import RelationshipCalculator
from Relationship_System.RelationshipSystem import RelationshipSystem

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class Relationships(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.system = RelationshipSystem()
            self.vinculum_descriptions = self.system.calculator.get_all_descriptions()
            self.vinculum_effects = self.system.calculator.get_all_effects()
            print("[SUCCESS] Relationships Cog инициализирован!")
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации Relationships Cog: {e}")
            traceback.print_exc()
            raise

    @app_commands.command(name="добавить", description="Добавить нового персонажа")
    @app_commands.describe(имя="Имя персонажа")
    async def добавить(self, interaction: discord.Interaction, имя: str):
        """Добавить нового персонажа"""
        name = имя.strip()
        if not name:
            await interaction.response.send_message("❌ Имя не может быть пустым!")
            return
            
        if self.system.character_exists(name):
            await interaction.response.send_message(f"❌ Персонаж `{name}` уже существует!")
            return
        
        success = self.system.add_character(name, interaction.user.id, interaction.created_at.isoformat())
        if success:
            embed = discord.Embed(
                title="✅ Персонаж добавлен",
                description=f"Персонаж `{name}` успешно добавлен!",
                color=0x00FF00,
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ Не удалось добавить персонажа `{name}`!")

    @app_commands.command(name="удалить", description="Удалить персонажа")
    @app_commands.describe(имя="Имя персонажа для удаления")
    async def удалить(self, interaction: discord.Interaction, имя: str):
        """Удалить персонажа"""
        name = имя.strip()
        if not name:
            await interaction.response.send_message("❌ Имя не может быть пустым!")
            return
            
        if not self.system.character_exists(name):
            await interaction.response.send_message(f"❌ Персонаж `{name}` не найден!")
            return

        success = self.system.remove_character(name)
        if success:
            await interaction.response.send_message(f"✅ Персонаж `{name}` и все его отношения удалены!")
        else:
            await interaction.response.send_message(f"❌ Не удалось удалить персонажа `{name}`!")

    @app_commands.command(name="персонажи", description="Показать список всех персонажей")
    async def персонажи(self, interaction: discord.Interaction):
        """Показать список всех персонажей"""
        characters = self.system.list_characters()
        if not characters:
            await interaction.response.send_message("❌ Пока нет добавленных персонажей!")
            return

        embed = discord.Embed(
            title="📋 Список персонажей",
            description=f"Всего персонажей: {len(characters)}\n\n" +
            "\n".join([f"• {char}" for char in sorted(characters)]),
            color=0x9370DB,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="бросок", description="Определить винкулумы между всеми персонажами")
    async def бросок(self, interaction: discord.Interaction):
        """Создать винкулумы между всеми персонажами"""
        try:
            characters = self.system.list_characters()
            if len(characters) < 2:
                await interaction.response.send_message("❌ Нужно как минимум 2 персонажа для броска! Добавь персонажей через `/добавить`")
                return
            
            rolled_by = interaction.user.id
            roll_date = interaction.created_at.isoformat()
            vinculums_created = self.system.roll_all_vinculums(rolled_by, roll_date)
            
            embed = discord.Embed(
                title="🎲 Винкулумы созданы!",
                description=f"Создано **{vinculums_created}** винкулумов между {len(characters)} персонажами!\n\nИспользуй `/винкулум` чтобы посмотреть отношения.",
                color=0x9370DB
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде бросок: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Произошла ошибка при создании винкулумов!")

    # НОВАЯ КОМАНДА: Бросок винкулума между двумя персонажами
    @app_commands.command(name="бросок_винкулума", description="Определить винкулум между двумя конкретными персонажами")
    @app_commands.describe(персонаж1="Первый персонаж", персонаж2="Второй персонаж")
    async def бросок_винкулума(self, interaction: discord.Interaction, персонаж1: str, персонаж2: str):
        """Создать винкулум между двумя конкретными персонажами"""
        try:
            char1 = персонаж1.strip()
            char2 = персонаж2.strip()
            
            rolled_by = interaction.user.id
            roll_date = interaction.created_at.isoformat()
            
            result, message = self.system.roll_single_vinculum(char1, char2, rolled_by, roll_date)
            
            if result is None:
                await interaction.response.send_message(message)
                return
            
            value, description, effect = result
            
            embed = discord.Embed(
                title="🎲 Винкулум создан!",
                description=f"**{char1}** → **{char2}**",
                color=0x9370DB
            )
            embed.add_field(name="📊 Уровень", value=f"{value}: {description}", inline=False)
            embed.add_field(name="💫 Эффект", value=effect, inline=False)
            embed.set_footer(text=f"Создано пользователем ID: {rolled_by}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде бросок_винкулума: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Произошла ошибка при создании винкулума!")

    # НОВАЯ КОМАНДА: Установить значение винкулума
    @app_commands.command(name="установить_винкулум", description="Установить конкретное значение винкулума между двумя персонажами")
    @app_commands.describe(
        персонаж1="Первый персонаж", 
        персонаж2="Второй персонаж",
        значение="Значение винкулума (от 1 до 10)"
    )
    async def установить_винкулум(self, interaction: discord.Interaction, персонаж1: str, персонаж2: str, значение: int):
        """Установить конкретное значение винкулума между двумя персонажами"""
        try:
            char1 = персонаж1.strip()
            char2 = персонаж2.strip()
            value = значение
            
            set_by = interaction.user.id
            set_date = interaction.created_at.isoformat()
            
            result, message = self.system.set_vinculum_value(char1, char2, value, set_by, set_date)
            
            if result is None:
                await interaction.response.send_message(message)
                return
            
            value, description, effect = result
            
            embed = discord.Embed(
                title="🎯 Винкулум установлен!",
                description=f"**{char1}** → **{char2}**",
                color=0x9370DB
            )
            embed.add_field(name="📊 Уровень", value=f"{value}: {description}", inline=False)
            embed.add_field(name="💫 Эффект", value=effect, inline=False)
            embed.set_footer(text=f"Установлено пользователем ID: {set_by}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде установить_винкулум: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Произошла ошибка при установке винкулума!")

    @app_commands.command(name="винкулум", description="Показать винкулумы персонажа")
    @app_commands.describe(персонаж="Имя персонажа")
    async def винкулум(self, interaction: discord.Interaction, персонаж: str):
        """Показать отношения персонажа"""
        try:
            name = персонаж.strip()
            if not self.system.character_exists(name):
                await interaction.response.send_message(f"❌ Персонаж `{name}` не найден!")
                return
            
            outgoing = self.system.get_outgoing_relationships(name)
            incoming = self.system.get_incoming_relationships(name)
            
            embed = discord.Embed(
                title=f"🔗 Винкулумы {name}",
                color=0x9370DB
            )
            
            if outgoing:
                outgoing_text = ""
                for to_char, rel_data in outgoing:
                    value = rel_data.get('value', 0)
                    desc = rel_data.get('description', '❓ Неизвестно')
                    outgoing_text += f"**→ {to_char}**: {desc} (уровень {value})\n"
                embed.add_field(name="🎯 Отношения к другим", value=outgoing_text, inline=False)
            else:
                embed.add_field(name="🎯 Отношения к другим", value="Нет исходящих отношений", inline=False)
            
            if incoming:
                incoming_text = ""
                for from_char, rel_data in incoming:
                    value = rel_data.get('value', 0)
                    desc = rel_data.get('description', '❓ Неизвестно')
                    incoming_text += f"**← {from_char}**: {desc} (уровень {value})\n"
                embed.add_field(name="📥 Отношения других", value=incoming_text, inline=False)
            else:
                embed.add_field(name="📥 Отношения других", value="Нет входящих отношений", inline=False)
                
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде винкулум: {e}")
            await interaction.response.send_message("❌ Произошла ошибка!")

    @app_commands.command(name="таблица", description="Показать таблицу винкулумов")
    async def таблица(self, interaction: discord.Interaction):
        """Показать таблицу уровней винкулумов"""
        try:
            embed = discord.Embed(
                title="📊 Таблица уровней Винкулумов",
                description="Уровни отношений между персонажами",
                color=0x9370DB
            )
            
            for level in range(1, 11):
                desc = self.vinculum_descriptions.get(level, "❓ Неизвестно")
                effect = self.vinculum_effects.get(level, "❓ Эффект неизвестен")
                embed.add_field(
                    name=f"Уровень {level}: {desc}",
                    value=effect,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде таблица: {e}")
            await interaction.response.send_message("❌ Произошла ошибка!")

    @app_commands.command(name="перебросить", description="Перебросить винкулум между двумя персонажами")
    @app_commands.describe(персонаж1="Первый персонаж", персонаж2="Второй персонаж")
    async def перебросить(self, interaction: discord.Interaction, персонаж1: str, персонаж2: str):
        """Перебросить конкретный винкулум"""
        try:
            char1 = персонаж1.strip()
            char2 = персонаж2.strip()
            
            if not self.system.character_exists(char1):
                await interaction.response.send_message(f"❌ Персонаж `{char1}` не найден!")
                return
            if not self.system.character_exists(char2):
                await interaction.response.send_message(f"❌ Персонаж `{char2}` не найден!")
                return
            
            current_rel = self.system.get_relationship(char1, char2)
            if not current_rel:
                await interaction.response.send_message(f"❌ Между `{char1}` и `{char2}` нет винкулума!")
                return
            
            current_value = current_rel.get('value', 1)
            new_value, new_desc, new_effect = self.system.calculator.reroll_vinculum(current_value)
            
            self.system.relationship_manager.update_relationship(char1, char2, new_value, new_desc)
            
            embed = discord.Embed(
                title="🎲 Винкулум переброшен!",
                description=f"**{char1}** → **{char2}**",
                color=0x9370DB
            )
            embed.add_field(name="📊 Было", value=f"Уровень {current_value}: {current_rel.get('description', '❓')}", inline=False)
            embed.add_field(name="🎯 Стало", value=f"Уровень {new_value}: {new_desc}", inline=False)
            embed.add_field(name="💫 Эффект", value=new_effect, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде перебросить: {e}")
            await interaction.response.send_message("❌ Произошла ошибка при перебросе!")

    @app_commands.command(name="отношения", description="Показать все отношения в системе")
    async def отношения(self, interaction: discord.Interaction):
        """Показать все отношения между персонажами"""
        try:
            all_relationships = self.system.get_all_relationships()
            if not all_relationships:
                await interaction.response.send_message("❌ В системе пока нет отношений!")
                return
            
            embed = discord.Embed(
                title="🔗 Все отношения в системе",
                description=f"Всего отношений: {len(all_relationships)}",
                color=0x9370DB
            )
            
            relationships_text = ""
            for from_char, to_char, rel_data in all_relationships:
                value = rel_data.get('value', 0)
                desc = rel_data.get('description', '❓ Неизвестно')
                relationships_text += f"**{from_char}** → **{to_char}**: {desc} (ур. {value})\n"
                
                if len(relationships_text) > 800:
                    relationships_text += "\n... и другие (слишком много для отображения)"
                    break
            
            embed.add_field(name="📋 Список отношений", value=relationships_text, inline=False)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[ERROR] Ошибка в команде отношения: {e}")
            await interaction.response.send_message("❌ Произошла ошибка!")

async def setup(bot):
    await bot.add_cog(Relationships(bot))
    print("[SUCCESS] Relationships Cog добавлен!")