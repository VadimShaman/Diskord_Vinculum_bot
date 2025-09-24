import os
import sys  # For UTF-8 console reconfiguration
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback  # Added for detailed error traces
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

# Создание бота (добавлен case_insensitive=True для нечувствительности к регистру)
bot = commands.Bot(
    command_prefix=["!", "?", "/"], intents=intents, case_insensitive=True
)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!помощь"))
    print(f"✅ Бот {bot.user} запущен!")
    print(f"📊 Бот работает на {len(bot.guilds)} серверах")

    # Debug: Выводим список всех команд для проверки загрузки
    print("📋 Загруженные команды:", [cmd.name for cmd in bot.commands])

    # Загружаем коги (теперь синхронно)
    try:
        load_cogs()  # No await needed
        print("✅ Все коги загружены!")

        # New Debug: Check if cog is actually added
        print("🔍 Загруженные коги:", list(bot.cogs.keys()))
    except Exception as e:
        print(f"❌ Ошибка загрузки когов: {e}")
        traceback.print_exc()  # Full traceback for debugging


def load_cogs():  # Synchronous function
    """Загрузка всех когов"""
    cogs = ["cogs.relationships"]

    for cog in cogs:
        try:
            bot.load_extension(cog)  # Synchronous call, no await
            print(f"✅ Загружен ког: {cog}")
        except Exception as e:
            print(f"❌ Ошибка загрузки {cog}: {e}")
            traceback.print_exc()  # Full traceback, e.g., import errors


@bot.event
async def on_command_error(ctx, error):
    """Обработчик ошибок команд"""
    # Игнорируем ошибки в DM или от ботов
    if not ctx.guild or ctx.author.bot:
        return

    if isinstance(error, commands.CommandNotFound):
        # Если команда не найдена, напоминаем о префиксе
        embed = discord.Embed(
            title="❓ Команда не найдена",
            description=f"Команда `{ctx.invoked_with}` не распознана. Используйте префикс `!`, `?` или `/` перед названием команды.\n\nНапример: `!добавить ИмяПерсонажа`\nДля списка команд: `!помощь`",
            color=0xFF0000,
        )
        await ctx.send(embed=embed, delete_after=10)  # Автоудаление через 10 сек

        # New Debug: Log full error to console
        print(f"⚠️ CommandNotFound для '{ctx.invoked_with}' от {ctx.author}: {error}")
        traceback.print_exc()
    else:
        # Для других ошибок (например, недостаточно аргументов) - стандартное поведение
        await bot.on_command_error(ctx, error)  # Передаем дальше


@bot.command()
async def помощь(ctx):
    """Справка по командам"""
    embed = discord.Embed(
        title="📖 Помощь по системе отношений",
        description="**Важно:** Все команды начинаются с префикса `!`, `?` или `/`.\n\nОсновные команды:",
        color=0x00FF00,
    )

    commands_list = {
        "!добавить [имя]": "Добавить персонажа",
        "!удалить [имя]": "Удалить персонажа",
        "!персонажи": "Список персонажей",
        "!бросок": "Определить отношения",
        "!таблица": "Таблица отношений",
        "!отношения [имя]": "Детальные отношения (опционально)",
        "!перебросить [имя1] [имя2]": "Перебросить отношение",
    }

    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.add_field(
        name="💡 Подсказка",
        value="Имена могут содержать пробелы (например, `!добавить Alice Bob`). Команды нечувствительны к регистру.",
        inline=False,
    )

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
