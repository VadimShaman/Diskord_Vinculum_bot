import discord
from discord.ext import commands
import random
import ast
import traceback

class RelationshipCog(commands.Cog):
    try:
        from RelationshipSystem import RelationshipSystem
        print("✅ Импорт RelationshipSystem успешен!")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    
    def __init__(self, bot):
        self.bot = bot
        self.system = RelationshipSystem()
        
        # Теперь используем винкулумы
        self.vinculum_descriptions = self.system.calculator.get_all_descriptions()
        self.vinculum_effects = self.system.calculator.get_all_effects()

    @commands.command(name="бросок")
    async def roll_vinculums(self, ctx):
        """Бросить кубы для определения винкулумов"""
        if self.system.character_manager.get_character_count() < 2:
            await ctx.send("❌ Нужно как минимум 2 персонажа!")
            return
        
        vinculums_created = self.system.roll_all_vinculums(
            ctx.author.id,
            ctx.message.created_at.isoformat()
        )
        
        embed = discord.Embed(
            title="🎲 Винкулумы определены!",
            description=f"Создано {vinculums_created} направленных винкулумов.",
            color=0x0099FF,
        )
        await ctx.send(embed=embed)

    @commands.command(name="таблица")
    async def show_vinculum_table(self, ctx):
        """Показать таблицу винкулумов"""
        if not self.system.relationship_manager.get_relationship_count():
            await ctx.send("❌ Винкулумы еще не определены! Используйте `!бросок`")
            return

        characters = sorted(self.system.character_manager.list_characters())
        
        # Создаем таблицу
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
                    rel_key = str((char1, char2))
                    if rel_key in self.system.relationships:
                        rel = self.system.relationships[rel_key]
                        table += f"    {rel['value']}    "
                    else:
                        table += "    ?    "
            table += "\n"
        table += "```"

        embed = discord.Embed(
            title="📊 Таблица Винкулумов (направленная)",
            description=table,
            color=0xFFD700,
        )

        # Легенда винкулумов
        legend = ""
        for value, desc in self.vinculum_descriptions.items():
            effect_short = self.vinculum_effects[value][:30] + "..." if len(self.vinculum_effects[value]) > 30 else self.vinculum_effects[value]
            legend += f"**{value}**: {desc}\n"

        embed.add_field(name="🎯 Значения Винкулума", value=legend, inline=False)
        embed.set_footer(text="Строки: винкулум ОТ персонажа, Столбцы: К персонажу")
        await ctx.send(embed=embed)

    @commands.command(name="винкулум")
    async def show_vinculum_details(self, ctx, char1: str = None, char2: str = None):
        """Показать детали конкретного винкулума"""
        if not char1:
            await ctx.send("❌ Укажите хотя бы одного персонажа: `!винкулум [персонаж]`")
            return
            
        char1 = char1.strip()
        if not self.system.character_exists(char1):
            await ctx.send(f"❌ Персонаж `{char1}` не найден!")
            return
            
        if char2:
            char2 = char2.strip()
            if not self.system.character_exists(char2):
                await ctx.send(f"❌ Персонаж `{char2}` не найден!")
                return
                
            # Показать конкретный винкулум
            vinculum = self.system.get_relationship(char1, char2)
            if not vinculum:
                await ctx.send(f"❌ Винкулум от `{char1}` к `{char2}` не найден!")
                return
                
            embed = discord.Embed(
                title=f"💞 Винкулум: {char1} → {char2}",
                color=0xFF69B4,
            )
            embed.add_field(
                name=f"Уровень {vinculum['value']}: {vinculum['description']}",
                value=vinculum['effect'],
                inline=False
            )
            await ctx.send(embed=embed)
        else:
            # Показать все винкулумы персонажа
            outgoing = self.system.get_outgoing_relationships(char1)
            incoming = self.system.get_incoming_relationships(char1)
            
            embed = discord.Embed(
                title=f"💞 Винкулумы персонажа {char1}",
                color=0xFF69B4,
            )
            
            if outgoing:
                outgoing_desc = ""
                for to_char, rel_data in sorted(outgoing, key=lambda x: x[1]['value'], reverse=True):
                    outgoing_desc += f"**→ {to_char}**: {rel_data['value']} - {rel_data['description']}\n"
                embed.add_field(name="🎯 Исходящие винкулумы", value=outgoing_desc, inline=False)
                
            if incoming:
                incoming_desc = ""
                for from_char, rel_data in sorted(incoming, key=lambda x: x[1]['value'], reverse=True):
                    incoming_desc += f"**{from_char} →**: {rel_data['value']} - {rel_data['description']}\n"
                embed.add_field(name="📥 Входящие винкулумы", value=incoming_desc, inline=False)
                
            if not outgoing and not incoming:
                embed.description = f"У {char1} пока нет винкулумов."
                
            await ctx.send(embed=embed)

    @commands.command(name="помощь")
    async def help_vinculum(self, ctx):
        """Справка по системе винкулумов"""
        embed = discord.Embed(
            title="📖 Помощь по системе Винкулумов",
            description="**Винкулум** - сила кровной связи между Побратимами.\n\nОсновные команды:",
            color=0x00FF00,
        )

        commands_list = {
            "!добавить [имя]": "Добавить персонажа",
            "!бросок": "Определить винкулумы между всеми персонажами", 
            "!таблица": "Таблица винкулумов",
            "!винкулум [имя]": "Все винкулумы персонажа",
            "!винкулум [имя1] [имя2]": "Конкретный винкулум между двумя",
            "!перебросить [имя1] [имя2]": "Перебросить винкулум",
        }

        for cmd, desc in commands_list.items():
            embed.add_field(name=cmd, value=desc, inline=False)

        # Добавляем краткую легенду
        legend = ""
        for value in [1, 5, 10]:  # Показываем ключевые уровни
            legend += f"**{value}**: {self.vinculum_descriptions[value]}\n"
            
        embed.add_field(
            name="🎯 Ключевые уровни винкулума",
            value=legend,
            inline=False
        )

        await ctx.send(embed=embed)