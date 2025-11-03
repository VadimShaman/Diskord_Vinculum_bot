import os
import sys
sys.path.append(os.path.dirname(__file__))
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

# Глобальная переменная для tree
tree = None

@bot.event
async def on_ready():
    global tree
    tree = bot.tree
    
    await bot.change_presence(activity=discord.Game(name="/помощь"))
    print(f"[SUCCESS] Бот {bot.user} запущен!")
    print(f"[INFO] Бот работает на {len(bot.guilds)} серверах")

    # Загружаем коги
    try:
        await load_cogs()
        print("[SUCCESS] Все коги загружены!")

        # Debug информация
        print("[DEBUG] Загруженные коги:", list(bot.cogs.keys()))
        
        # Для discord.py команды находятся в bot.tree
        synced = await tree.sync()
        print(f"[SUCCESS] Синхронизировано {len(synced)} команд")
        
    except Exception as e:
        print(f"[ERROR] Ошибка загрузки когов: {e}")
        traceback.print_exc()


async def load_cogs():
    """Загрузка всех когов (асинхронно)"""
    cogs = ["cogs.relationships"]

    for cog_name in cogs:
        try:
            print(f"[LOADING] Загружаем ког: {cog_name}")
            await bot.load_extension(cog_name)
            print(f"[SUCCESS] Загружен ког: {cog_name}")
        except commands.ExtensionNotFound:
            print(f"[ERROR] Ког {cog_name} не найден (проверьте путь/файл)")
        except commands.ExtensionAlreadyLoaded:
            print(f"[WARNING] Ког {cog_name} уже загружен")
        except commands.NoEntryPointError:
            print(f"[ERROR] Ког {cog_name} не имеет функции setup!")
        except commands.ExtensionFailed as e:
            print(f"[ERROR] Загрузка {cog_name} провалилась (setup error): {e}")
            print("[TIP] Проверьте async def setup(bot) и await bot.add_cog в cogs/relationships.py")
            traceback.print_exc()
        except Exception as e:
            print(f"[ERROR] Неожиданная ошибка загрузки {cog_name}: {e}")
            traceback.print_exc()


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
        "/бросок": "Определить винкулумы",
        "/таблица": "Таблица винкулумов",
        "/винкулум": "Винкулумы персонажей",
        "/перебросить": "Перебросить винкулум",
        "/синхронизировать": "Синхронизация команд (владелец)",
    }

    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.add_field(
        name="💡 Подсказка",
        value="Просто начните вводить `/` и выберите нужную команду из списка! Параметры заполняются автоматически с подсказками.",
        inline=False,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="синхронизировать", description="Синхронизировать команды с Discord (только для владельца)")
async def синхронизировать(interaction: discord.Interaction):
    """Синхронизировать Slash-commands"""
    # ЗАМЕНИТЕ НА ВАШ REAL DISCORD USER ID
    YOUR_OWNER_ID = 1  # <-- ВАЖНО: ЗАМЕНИТЕ НА ВАШ ID!
    
    if interaction.user.id != YOUR_OWNER_ID:
        return await interaction.response.send_message("❌ Недостаточно прав! Эта команда только для владельца бота.", ephemeral=True)

    try:
        # Синхронизируем команды
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"✅ Синхронизировано {len(synced)} команд с Discord!", ephemeral=True)
        print(f"[SUCCESS] Синхронизировано {len(synced)} команд!")
        
        # Выводим список всех команд для отладки
        commands_list = [cmd.name for cmd in synced]
        print(f"[DEBUG] Доступные команды после синхронизации: {commands_list}")
        
    except Exception as e:
        error_msg = f"❌ Ошибка синхронизации: {e}"
        await interaction.response.send_message(error_msg, ephemeral=True)
        print(f"[ERROR] Ошибка синхронизации: {e}")
        traceback.print_exc()


@bot.tree.command(name="перезагрузить", description="Перезагрузить коги (только для владельца)")
async def перезагрузить(interaction: discord.Interaction):
    """Перезагрузить коги"""
    # ЗАМЕНИТЕ НА ВАШ REAL DISCORD USER ID
    YOUR_OWNER_ID = 1  # <-- ВАЖНО: ЗАМЕНИТЕ НА ВАШ ID!
    
    if interaction.user.id != YOUR_OWNER_ID:
        return await interaction.response.send_message("❌ Недостаточно прав! Эта команда только для владельца бота.", ephemeral=True)

    try:
        reloaded_cogs = []
        for cog in ["cogs.relationships"]:
            try:
                await bot.reload_extension(cog)
                reloaded_cogs.append(cog)
                print(f"[RELOAD] Перезагружен ког: {cog}")
            except Exception as e:
                print(f"[ERROR] Ошибка перезагрузки {cog}: {e}")

        if reloaded_cogs:
            await interaction.response.send_message(f"✅ Коги перезагружены: {', '.join(reloaded_cogs)}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Не удалось перезагрузить коги", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка перезагрузки: {e}", ephemeral=True)
        print(f"[ERROR] Ошибка перезагрузки когов: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    print("[INFO] Токен найден, запускаем бота...")
    bot.run(token)