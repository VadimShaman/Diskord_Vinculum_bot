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
            await interaction.response.send_message("[ERROR] Имя не может быть пустым!")
            return
            
        if self.system.character_exists(name):
            await interaction.response.send_message(f"[ERROR] Персонаж `{name}` уже существует!")
            return
        
        success = self.system.add_character(name, interaction.user.id, interaction.created_at.isoformat())
        if success:
            embed = discord.Embed(
                title="[SUCCESS] Персонаж добавлен",
                description=f"Персонаж `{name}` успешно добавлен!",
                color=0x00FF00,
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"[ERROR] Не удалось добавить персонажа `{name}`!")

    @app_commands.command(name="удалить", description="Удалить персонажа")
    @app_commands.describe(имя="Имя персонажа для удаления")
    async def удалить(self, interaction: discord.Interaction, имя: str):
        """Удалить персонажа"""
        name = имя.strip()
        if not name:
            await interaction.response.send_message("[ERROR] Имя не может быть пустым!")
            return
            
        if not self.system.character_exists(name):
            await interaction.response.send_message(f"[ERROR] Персонаж `{name}` не найден!")
            return

        success = self.system.remove_character(name)
        if success:
            await interaction.response.send_message(f"[SUCCESS] Персонаж `{name}` и все его отношения удалены!")
        else:
            await interaction.response.send_message(f"[ERROR] Не удалось удалить персонажа `{name}`!")

    @app_commands.command(name="персонажи", description="Показать список всех персонажей")
    async def персонажи(self, interaction: discord.Interaction):
        """Показать список всех персонажей"""
        characters = self.system.list_characters()
        if not characters:
            await interaction.response.send_message("[ERROR] Пока нет добавленных персонажей!")
            return

        embed = discord.Embed(
            title="[LIST] Список персонажей",
            description=f"Всего персонажей: {len(characters)}\n\n" +
            "\n".join([f"• {char}" for char in sorted(characters)]),
            color=0x9370DB,
        )
        await interaction.response.send_message(embed=embed)

    # ... остальные команды аналогично переделать на @app_commands.command ...

async def setup(bot):
    await bot.add_cog(Relationships(bot))
    print("[SUCCESS] Relationships Cog добавлен!")