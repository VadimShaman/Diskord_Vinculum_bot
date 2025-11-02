import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback

# Загрузка переменных окружения
load_dotenv()

# Настройка intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Создание бота (добавлен case_insensitive=True для нечувствительности к регистру)
bot = commands.Bot(command_prefix=["/"], intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/помощь"))
    print(f"[SUCCESS] Бот {bot.user} запущен!")
    print(f"[INFO] Бот работает на {len(bot.guilds)} серверах")

    # Debug: Выводим список всех команд для проверки загрузки (до загрузки когов)
    print("[DEBUG] Загруженные команды (до когов):", [cmd.name for cmd in bot.commands])

    # Загружаем коги (теперь асинхронно)
    try:
        await load_cogs()
        print("[SUCCESS] Все коги загружены!")

        # Enhanced Debug: Check if cog is actually added
        print("[DEBUG] Загруженные коги:", list(bot.cogs.keys()))
        print("[DEBUG] Полный список команд (после когов):", [cmd.name for cmd in bot.commands])
        if not bot.cogs:
            print("[WARNING] ВНИМАНИЕ: Ни один ког не загружен! Проверьте ошибки выше.")
    except Exception as e:
        print(f"[ERROR] Ошибка загрузки когов: {e}")
        traceback.print_exc()


async def load_cogs():  # Async function for Discord.py 2.x
    """Загрузка всех когов (асинхронно)"""
    cogs = ["cogs.relationships"]

    for cog_name in cogs:
        try:
            print(f"[LOADING] Загружаем ког: {cog_name}")
            await bot.load_extension(cog_name)  # Await the async method
            print(f"[SUCCESS] Загружен ког: {cog_name}")
        except discord.ext.commands.ExtensionNotFound:
            print(f"[ERROR] Ког {cog_name} не найден (проверьте путь/файл)")
        except discord.ext.commands.ExtensionAlreadyLoaded:
            print(f"[WARNING] Ког {cog_name} уже загружен")
        except discord.ext.commands.NoEntryPointError:
            print(f"[ERROR] Ког {cog_name} не имеет функции setup!")
        except discord.ext.commands.ExtensionFailed as e:
            print(f"[ERROR] Загрузка {cog_name} провалилась (setup error): {e}")
            print("[TIP] Проверьте async def setup(bot) и await bot.add_cog в cogs/relationships.py")
            traceback.print_exc()  # Full traceback
        except Exception as e:
            print(f"[ERROR] Неожиданная ошибка загрузки {cog_name}: {e}")
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
            title="[ERROR] Команда не найдена",
            description=f"Команда `{ctx.invoked_with}` не распознана. Используйте префикс `/` перед названием команды.\n\nНапример: `/добавить ИмяПерсонажа`\nДля списка команд: `/помощь`",
            color=0xFF0000,
        )
        await ctx.send(embed=embed, delete_after=10)  # Автоудаление через 10 сек

        # Debug: Log full error to console
        print(f"[WARNING] CommandNotFound для '{ctx.invoked_with}' от {ctx.author}: {error}")
        traceback.print_exc()
    else:
        # Для других ошибок (например, недостаточно аргументов) - стандартное поведение
        await bot.on_command_error(ctx, error)  # Передаем дальше


@bot.command()
async def помощь(ctx):
    """Справка по командам"""
    embed = discord.Embed(
        title="[HELP] Помощь по системе Винкулумов",
        description="**Важно:** Все команды начинаются с префикса `/`.\n\nОсновные команды:",
        color=0x00FF00,
    )

    commands_list = {
        "/добавить [имя]": "Добавить персонажа",
        "/удалить [имя]": "Удалить персонажа", 
        "/персонажи": "Список персонажей",
        "/бросок": "Определить винкулумы",
        "/таблица": "Таблица винкулумов",
        "/винкулум [имя]": "Винкулумы персонажа",
        "/винкулум [имя1] [имя2]": "Конкретный винкулум",
        "/перебросить [имя1] [имя2]": "Перебросить винкулум",
    }

    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.add_field(
        name="[TIP] Подсказка",
        value="Имена могут содержать пробелы (например, `/добавить Alice Bob`). Команды нечувствительны к регистру.",
        inline=False,
    )

    await ctx.send(embed=embed)


@bot.command()
async def перезагрузить(ctx):
    """Перезагрузить коги (только для владельца)"""
    # Замените YOUR_OWNER_ID на ваш реальный Discord user ID (число, например, 1234567890)
    YOUR_OWNER_ID = 1  # <-- ВСТАВЬТЕ СЮДА СВОЙ ID
    if ctx.author.id != YOUR_OWNER_ID:
        return await ctx.send("[ERROR] Недостаточно прав!")

    try:
        # Для перезагрузки: используем reload_extension (async в 2.x)
        for cog in ["cogs.relationships"]:
            try:
                await bot.reload_extension(cog)  # Await reload (unload + load)
                print(f"[RELOAD] Перезагружен ког: {cog}")
            except discord.ext.commands.ExtensionFailed as e:
                print(f"[ERROR] Перезагрузка {cog} провалилась (setup error): {e}")
                await ctx.send(f"[WARNING] Ошибка перезагрузки {cog}: {e}")
            except Exception as e:
                print(f"[WARNING] Ошибка перезагрузки {cog}: {e}")
                # Fallback: unload then load
                try:
                    await bot.unload_extension(cog)
                    await bot.load_extension(cog)
                    print(f"[RELOAD] Перезагружен через unload/load: {cog}")
                except Exception as fallback_e:
                    print(f"[ERROR] Fallback failed for {cog}: {fallback_e}")
                    await ctx.send(f"[ERROR] Fallback failed: {fallback_e}")

        await ctx.send("[SUCCESS] Коги перезагружены!")
    except Exception as e:
        await ctx.send(f"[ERROR] Ошибка: {e}")


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token:
        print(f"[INFO] Токен найден, запускаем бота...")
        bot.run(token)
    else:
        print("[ERROR] Токен не найден! Проверьте .env файл")