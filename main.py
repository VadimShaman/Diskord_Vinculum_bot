import os
import discord
from discord.ext import commands
from discord import app_commands
import traceback

# Загрузка переменных окружения
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ [ERROR] Токен не найден! Добавь DISCORD_TOKEN в Secrets Replit или .env")
    raise SystemExit

# Настройка intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Используем commands.Bot для discord.py
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/помощь"))
    print(f"[SUCCESS] Бот {bot.user} запущен!")
    print(f"[INFO] Бот работает на {len(bot.guilds)} серверах")

    # Загружаем коги
    try:
        await load_cogs()
        print("[SUCCESS] Все коги загружены!")

        # Debug информация
        print("[DEBUG] Загруженные коги:", list(bot.cogs.keys()))
        
        # Синхронизируем команды
        synced = await bot.tree.sync()
        print(f"[SUCCESS] Синхронизировано {len(synced)} команд")
        
        # Выводим список всех команд для отладки
        commands_list = [cmd.name for cmd in synced]
        print(f"[DEBUG] Доступные команды: {commands_list}")
        
    except Exception as e:
        print(f"[ERROR] Ошибка загрузки когов: {e}")
        traceback.print_exc()

async def load_cogs():
    """Загрузка всех когов (асинхронно)"""
    # ВАЖНО: укажи правильный путь к файлу
    # cogs = ["relationships"]  # если файл в корневой папке
    # ИЛИ:
    cogs = ["cogs.relationships"]  # если файл в папке cogs/

    for cog_name in cogs:
        try:
            print(f"[LOADING] Загружаем ког: {cog_name}")
            await bot.load_extension(cog_name)
            print(f"[SUCCESS] Загружен ког: {cog_name}")
        except Exception as e:
            print(f"[ERROR] Ошибка загрузки {cog_name}: {e}")
            traceback.print_exc()

# Остальные команды (помощь, синхронизировать, перезагрузить) остаются без изменений
@bot.tree.command(name="помощь", description="Справка по командам системы Винкулумов")
async def помощь(interaction: discord.Interaction):
    """Справка по командам"""
    embed = discord.Embed(
        title="[HELP] Помощь по системе Винкулумов",
        description="**Все команды начинаются с `/` и всплывают автоматически**\n\nОсновные команды:",
        color=0x00FF00,
    )

    commands_list = {
        "/добавить [имя]": "Добавить персонажа",
        "/удалить [имя]": "Удалить персонажа", 
        "/персонажи": "Список персонажей",
        "/бросок": "Определить винкулумы между всеми",
        "/бросок_винкулума [персонаж1] [персонаж2]": "Создать винкулум между двумя персонажами",
        "/установить_винкулум [персонаж1] [персонаж2] [значение]": "Установить конкретное значение винкулума",
        "/таблица": "Таблица винкулумов",
        "/винкулум": "Винкулумы персонажей",
        "/перебросить": "Перебросить винкулум",
        "/отношения": "Все отношения системы",
        "/диагностика": "Проверить загрузку команд",
        "/синхронизировать": "Синхронизация команд (владелец)",
        "/перезагрузить": "Перезагрузить коги (владелец)",
    }

    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    await interaction.response.send_message(embed=embed)

# Добавь команду диагностики здесь...

if __name__ == "__main__":
    print("[INFO] Токен найден, запускаем бота...")
    bot.run(token)