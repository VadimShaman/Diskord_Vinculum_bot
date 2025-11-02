import discord
from discord.ext import commands
import random
import ast
import traceback

try:
    from RelationshipSystem import RelationshipSystem
    print("✅ Импорт RelationshipSystem успешен!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    traceback.print_exc()

class RelationshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.system = RelationshipSystem()
        
        # Теперь используем винкулумы
        self.vinculum_descriptions = self.system.calculator.get_all_descriptions()
        self.vinculum_effects = self.system.calculator.get_all_effects()

    @commands.command(name="бросок")
    async def roll_vinculums(self, ctx):
        """Бросить кубы для определения винкулумов"""
        if len(self.system.characters) < 2:  # ✅ Использовать property
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
        if not self.system.relationships:  # ✅ Использовать property
            await ctx.send("❌ Винкулумы еще не определены! Используйте `/бросок`")
            return

        characters = sorted(self.system.characters.keys())  # ✅ Использовать property
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

    @commands.command(name="добавить")
    async def add_character(self, ctx, *, name: str):
        """Добавить нового персонажа"""
        name = name.strip()
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

        # Используем метод системы для правильного удаления
        success = self.system.remove_character(name)
        if success:
            await ctx.send(f"✅ Персонаж `{name}` и все его винкулумы удалены!")
        else:
            await ctx.send("❌ Ошибка при удалении персонажа!")

    @commands.command(name="персонажи") 
    async def list_characters(self, ctx):
        """Показать список всех персонажей"""
        if not self.system.characters:
            await ctx.send("❌ Пока нет добавленных персонажей!")
            return

        characters = list(self.system.characters.keys())
        embed = discord.Embed(
            title="👥 Список персонажей",
            description=f"Всего персонажей: {len(characters)}\n\n" +
            "\n".join([f"• {char}" for char in sorted(characters)]),
            color=0x9370DB,
        )
        await ctx.send(embed=embed)

    @commands.command(name="перебросить")
    async def reroll_vinculum(self, ctx, char1: str, char2: str):
        """Перебросить винкулум между двумя персонажами"""
        char1 = char1.strip()
        char2 = char2.strip()
        if not char1 or not char2:
            await ctx.send("❌ Имена персонажей не могут быть пустыми!")
            return
        if char1 == char2:
            await ctx.send("❌ Нельзя перебросить винкулум к себе!")
            return

        vinculum = self.system.get_relationship(char1, char2)
        if not vinculum:
            await ctx.send(f"❌ Винкулум от `{char1}` к `{char2}` не найден!")
            return

        old_value = vinculum['value']
        new_value, new_description, new_effect = self.system.calculator.reroll_vinculum(old_value)
    
        # Обновляем винкулум через менеджер
        self.system.relationship_manager.update_relationship(
            char1, char2, new_value, new_description
        )
        # Обновляем эффект отдельно
        rel_key = str((char1, char2))
        if rel_key in self.system.relationships:
            self.system.relationships[rel_key]['effect'] = new_effect
        self.system.save_data()

        embed = discord.Embed(
            title="🔄 Винкулум переброшен!",
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
        print("✅ RelationshipCog добавлен!")