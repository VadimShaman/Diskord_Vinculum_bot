# cogs/relationships.py
import discord
from discord.ext import commands
import random
import ast
import traceback

# Импорт из новой структуры
try:
    from Relationship_System.RelationshipSystem import RelationshipSystem

    print("✅ Импорт RelationshipSystem успешен!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    # Fallback система...


class RelationshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.system = RelationshipSystem()

        # Описания отношений теперь в Calculator
        self.relationship_descriptions = self.system.calculator.get_all_descriptions()

    @commands.command(name="добавить")
    async def add_character(self, ctx, *, name: str):
        name = name.strip()
        if not name:
            await ctx.send("❌ Имя не может быть пустым!")
            return

        if self.system.character_exists(name):
            await ctx.send(f"❌ Персонаж `{name}` уже существует!")
            return

        # Используем новый метод
        success = self.system.add_character(
            name, ctx.author.id, ctx.message.created_at.isoformat()
        )

        if success:
            embed = discord.Embed(
                title="✅ Персонаж добавлен",
                description=f"Персонаж `{name}` успешно добавлен!",
                color=0x00FF00,
            )
            await ctx.send(embed=embed)

    @commands.command(name="бросок")
    async def roll_relationships(self, ctx):
        """Бросить кубы для всех отношений"""
        if self.system.character_manager.get_character_count() < 2:
            await ctx.send("❌ Нужно как минимум 2 персонажа!")
            return

        # Используем новый метод
        relationships_created = self.system.roll_all_relationships(
            ctx.author.id, ctx.message.created_at.isoformat()
        )

        embed = discord.Embed(
            title="🎲 Отношения определены!",
            description=f"Создано {relationships_created} направленных отношений.",
            color=0x0099FF,
        )
        await ctx.send(embed=embed)

    @commands.command(name="отношения")
    async def show_detailed_relationships(self, ctx, *, character_name: str = None):
        if not self.system.relationship_manager.get_relationship_count():
            await ctx.send("❌ Отношения еще не определены!")
            return

        embed = discord.Embed(title="💞 Детальные отношения", color=0xFF69B4)

        if character_name:
            character_name = character_name.strip()
            if not self.system.character_exists(character_name):
                await ctx.send(f"❌ Персонаж `{character_name}` не найден!")
                return

            # Используем новый метод
            outgoing_rels = self.system.get_outgoing_relationships(character_name)

            if not outgoing_rels:
                embed.description = f"У {character_name} пока нет отношений."
            else:
                desc = f"Отношения **{character_name}** → другим:\n\n"
                for other_char, rel_data in sorted(
                    outgoing_rels, key=lambda x: x[1]["value"], reverse=True
                ):
                    desc += f"**{character_name} → {other_char}**: {rel_data['value']} - {rel_data['description']}\n"
                embed.description = desc
        else:
            # Все отношения
            all_rels = self.system.get_all_relationships()
            desc = "Все отношения (от → к):\n\n"
            for from_char, to_char, rel_data in sorted(
                all_rels, key=lambda x: x[2]["value"], reverse=True
            ):
                desc += f"**{from_char} → {to_char}**: {rel_data['value']} - {rel_data['description']}\n"
            embed.description = desc

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RelationshipCog(bot))
    print("✅ RelationshipCog добавлен!")
