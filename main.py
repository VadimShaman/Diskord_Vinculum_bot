import os
import sys  # For UTF-8 console reconfiguration
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs import *

# Force UTF-8 encoding for console output (fixes UnicodeEncodeError on Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except AttributeError:
    # Fallback for older Python versions (not needed for 3.12)
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

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

    # Загружаем коги (теперь синхронно)
    try:
        load_cogs()  # No await needed
        print("✅ Все коги загружены!")
    except Exception as e:
        print(f"❌ Ошибка загрузки когов: {e}")


def load_cogs():  # Changed to synchronous function
    """Загрузка всех когов"""
    cogs = ["cogs.relationships"]

    for cog in cogs:
        try:
            bot.load_extension(cog)  # Synchronous call, no await
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
    # Замените YOUR_OWNER_ID на ваш реальный Discord user ID (число, например, 1234567890)
    YOUR_OWNER_ID = 1234567890  # <-- ВСТАВЬТЕ СЮДА СВОЙ ID
    if ctx.author.id != YOUR_OWNER_ID:
        return await ctx.send("❌ Недостаточно прав!")

    try:
        # Для перезагрузки: сначала выгружаем, потом загружаем заново
        for cog in ["cogs.relationships"]:
            try:
                bot.unload_extension(cog)
                print(f"🔄 Выгружен ког: {cog}")
            except Exception as e:
                print(f"⚠️ Ошибка выгрузки {cog}: {e}")

        load_cogs()  # Synchronous reload
        await ctx.send("✅ Коги перезагружены!")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Токен не найден! Проверьте .env файл")
