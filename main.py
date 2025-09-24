import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from Relationship_System import *
from Cog import *

# Загрузка переменных окружения
load_dotenv()

# Настройка intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Создание бота
bot = commands.Bot(command_prefix=["!", "?", "/"], intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!помощь"))
    print(f"✅ Бот {bot.user} запущен!")
    print(f"📊 Бот работает на {len(bot.guilds)} серверах")

    # Загружаем коги
    try:
        await load_cogs()
        print("✅ Все коги загружены!")
    except Exception as e:
        print(f"❌ Ошибка загрузки когов: {e}")


async def load_cogs():
    """Загрузка всех когов"""
    cogs = ["cogs.relationships"]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Загружен ког: {cog}")
        except Exception as e:
            print(f"❌ Ошибка загрузки {cog}: {e}")


@bot.command()
async def помощь(ctx):
    """Справка по командам"""
    embed = discord.Embed(
        title="📖 Помощь по системе отношений",
        description="Основные команды:",
        color=0x00FF00,
    )

    commands_list = {
        "!добавить [имя]": "Добавить персонажа",
        "!удалить [имя]": "Удалить персонажа",
        "!персонажи": "Список персонажей",
        "!бросок": "Определить отношения",
        "!таблица": "Таблица отношений",
        "!отношения [имя]": "Детальные отношения",
        "!перебросить [имя1] [имя2]": "Перебросить отношение",
    }

    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def перезагрузить(ctx):
    """Перезагрузить коги (только для владельца)"""
    if ctx.author.id != ваш_id_владельца:  # Замените на ваш ID
        return await ctx.send("❌ Недостаточно прав!")

    try:
        await load_cogs()
        await ctx.send("✅ Коги перезагружены!")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Токен не найден! Проверьте .env файл")
