import os
import discord
from discord.ext import commands
from discord import app_commands
import traceback
import asyncio

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
    cogs = ["cogs.relationships"]  # если файл в папке cogs/

    for cog_name in cogs:
        try:
            print(f"[LOADING] Загружаем ког: {cog_name}")
            await bot.load_extension(cog_name)
            print(f"[SUCCESS] Загружен ког: {cog_name}")
        except Exception as e:
            print(f"[ERROR] Ошибка загрузки {cog_name}: {e}")
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
        "/бросок": "Определить винкулумы между всеми",
        "/бросок_винкулума [персонаж1] [персонаж2]": "Создать винкулум между двумя персонажами",
        "/установить_винкулум [персонаж1] [персонаж2] [значение]": "Установить конкретное значение винкулума",
        "/таблица": "Таблица винкулумов",
        "/винкулум [персонаж]": "Винкулумы персонажа",
        "/перебросить [персонаж1] [персонаж2]": "Перебросить винкулум",
        "/отношения": "Все отношения системы",
        "/диагностика": "Проверить загрузку команд",
        "/синхронизировать": "Синхронизация команд (владелец)",
        "/перезагрузить": "Перезагрузить коги (владелец)",
        "/проверка_системы": "Проверить работу компонентов",
        "/тест_команды": "Тест основных команд",
        "/полная_синхронизация": "Полная пересинхронизация (владелец)",
        "/мой_id": "Показать ваш Discord ID",
        "/подробная_диагностика": "Расширенная диагностика",
    }

    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="диагностика", description="Проверить состояние бота и команд")
async def диагностика(interaction: discord.Interaction):
    """Диагностика бота"""
    try:
        # Получаем информацию о загруженных когах
        loaded_cogs = list(bot.cogs.keys())
        
        # Получаем синхронизированные команды
        synced_commands = await bot.tree.fetch_commands()
        command_names = [cmd.name for cmd in synced_commands]
        
        # Информация о владельце
        app_info = await bot.application_info()
        current_owner_id = getattr(bot, 'owner_id', 'Не установлен')
        
        embed = discord.Embed(
            title="🔧 Диагностика системы",
            color=0x9370DB
        )
        
        embed.add_field(
            name="👑 Информация о владельце",
            value=f"**Ваш ID:** `{interaction.user.id}`\n"
                  f"**Текущий OWNER_ID:** `{current_owner_id}`\n"
                  f"**Владелец приложения:** `{app_info.owner.id}`",
            inline=False
        )
        
        embed.add_field(
            name="📊 Загруженные коги",
            value="\n".join(loaded_cogs) if loaded_cogs else "❌ Нет загруженных когов",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Доступные команды",
            value="\n".join([f"`/{cmd}`" for cmd in command_names]) if command_names else "❌ Нет команд",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Состояние",
            value=f"✅ Бот работает\n🖥️ Серверов: {len(bot.guilds)}\n📊 Задержка: {round(bot.latency * 1000)}ms",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка диагностики: {e}")

@bot.tree.command(name="подробная_диагностика", description="Расширенная диагностика системы")
async def подробная_диагностика(interaction: discord.Interaction):
    """Расширенная диагностика бота"""
    try:
        # Информация о загруженных когах
        loaded_cogs = list(bot.cogs.keys())
        cog_details = []
        for cog_name, cog_instance in bot.cogs.items():
            commands = [cmd.name for cmd in cog_instance.get_commands()] if hasattr(cog_instance, 'get_commands') else []
            app_commands = [cmd.name for cmd in cog_instance.app_commands] if hasattr(cog_instance, 'app_commands') else []
            cog_details.append(f"**{cog_name}**: {len(commands)} команд, {len(app_commands)} app-команд")

        # Синхронизированные команды
        synced_commands = await bot.tree.fetch_commands()
        global_commands = [cmd.name for cmd in synced_commands]
        
        # Команды для текущей гильдии
        guild_commands = []
        if interaction.guild:
            try:
                guild_synced = await bot.tree.fetch_commands(guild=interaction.guild)
                guild_commands = [cmd.name for cmd in guild_synced]
            except:
                pass

        # Проверка загрузки когов
        relationships_cog = bot.get_cog("Relationships")
        relationships_loaded = relationships_cog is not None
        system_loaded = hasattr(relationships_cog, 'system') if relationships_cog else False

        embed = discord.Embed(
            title="🔧 Подробная диагностика системы",
            color=0x9370DB
        )

        # Информация о когах
        embed.add_field(
            name="📦 Загруженные коги",
            value="\n".join(cog_details) if cog_details else "❌ Нет загруженных когов",
            inline=False
        )

        # Relationships Cog статус
        cog_status = []
        cog_status.append(f"✅ Cog загружен: {relationships_loaded}")
        if relationships_loaded:
            cog_status.append(f"✅ System инициализирован: {system_loaded}")
            if system_loaded:
                try:
                    characters_count = len(relationships_cog.system.list_characters())
                    cog_status.append(f"✅ Персонажей: {characters_count}")
                except:
                    cog_status.append("❌ Ошибка получения персонажей")
        
        embed.add_field(
            name="🔗 Relationships Cog",
            value="\n".join(cog_status),
            inline=False
        )

        # Команды
        embed.add_field(
            name="🌐 Глобальные команды",
            value="\n".join([f"`/{cmd}`" for cmd in global_commands]) if global_commands else "❌ Нет команд",
            inline=False
        )

        if guild_commands:
            embed.add_field(
                name="🏠 Команды сервера",
                value="\n".join([f"`/{cmd}`" for cmd in guild_commands]),
                inline=False
            )

        # Состояние системы
        system_status = []
        system_status.append(f"🖥️ Серверов: {len(bot.guilds)}")
        system_status.append(f"📊 Задержка: {round(bot.latency * 1000)}ms")
        system_status.append(f"👑 Владелец: {bot.owner_id}")
        
        embed.add_field(
            name="🔄 Состояние системы",
            value="\n".join(system_status),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Ошибка диагностики",
            description=f"```{str(e)}```",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=error_embed)

@bot.tree.command(name="проверка_системы", description="Проверить работу всех компонентов")
async def проверка_системы(interaction: discord.Interaction):
    """Проверка работы системы"""
    try:
        cog = bot.get_cog("Relationships")
        if not cog:
            await interaction.response.send_message("❌ Relationships ког не загружен!")
            return
        
        embed = discord.Embed(title="🔍 Проверка системы", color=0x9370DB)
        
        # Проверяем компоненты
        checks = []
        
        # Проверка CharacterManager
        try:
            chars = cog.system.character_manager.list_characters()
            checks.append(f"✅ CharacterManager: {len(chars)} персонажей")
        except Exception as e:
            checks.append(f"❌ CharacterManager: {e}")
        
        # Проверка RelationshipManager
        try:
            rels = cog.system.relationship_manager.get_all_relationships()
            checks.append(f"✅ RelationshipManager: {len(rels)} отношений")
        except Exception as e:
            checks.append(f"❌ RelationshipManager: {e}")
        
        # Проверка Calculator
        try:
            desc = cog.system.calculator.get_all_descriptions()
            checks.append(f"✅ Calculator: {len(desc)} описаний")
        except Exception as e:
            checks.append(f"❌ Calculator: {e}")
        
        embed.add_field(
            name="Компоненты системы",
            value="\n".join(checks),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка проверки: {e}")

@bot.tree.command(name="тест_команды", description="Тест основных команд")
async def тест_команды(interaction: discord.Interaction):
    """Тест команд"""
    try:
        embed = discord.Embed(title="🧪 Тест команд", color=0x9370DB)
        
        # Тест добавления персонажа
        cog = bot.get_cog("Relationships")
        if cog:
            test_name = "ТестовыйПерсонаж"
            try:
                if not cog.system.character_exists(test_name):
                    success = cog.system.add_character(test_name, interaction.user.id, "2024-01-01")
                    embed.add_field(
                        name="Добавление персонажа",
                        value="✅ Успешно" if success else "❌ Ошибка",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="Добавление персонажа", 
                        value="✅ Уже существует", 
                        inline=True
                    )
                
                # Тест списка персонажей
                chars = cog.system.list_characters()
                embed.add_field(
                    name="Список персонажей",
                    value=f"✅ {len(chars)} шт." if chars else "❌ Нет персонажей",
                    inline=True
                )
                
                # Тест калькулятора
                try:
                    value, desc, effect = cog.system.calculator.roll_vinculum()
                    embed.add_field(
                        name="Калькулятор",
                        value=f"✅ Уровень {value}",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name="Калькулятор",
                        value=f"❌ {e}",
                        inline=True
                    )
                    
            except Exception as e:
                embed.add_field(
                    name="Общий тест",
                    value=f"❌ {e}",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка теста: {e}")

@bot.tree.command(name="мой_id", description="Показать ваш Discord ID")
async def мой_id(interaction: discord.Interaction):
    """Показать ID пользователя"""
    embed = discord.Embed(
        title="🆔 Ваш Discord ID",
        description=f"```{interaction.user.id}```",
        color=0x9370DB
    )
    embed.add_field(
        name="Как использовать",
        value="Добавьте этот ID в переменную `OWNER_ID` в Secrets",
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="синхронизировать", description="Синхронизировать команды (только для владельца)")
async def синхронизировать(interaction: discord.Interaction):
    """Синхронизировать команды с Discord"""
    # Проверяем, является ли пользователь владельцем бота
    if interaction.user.id != bot.owner_id:
        await interaction.response.send_message("❌ Эта команда только для владельца бота!")
        return
    
    try:
        # Синхронизируем команды
        synced = await bot.tree.sync()
        
        embed = discord.Embed(
            title="🔄 Синхронизация завершена",
            description=f"Синхронизировано {len(synced)} команд:",
            color=0x00FF00
        )
        
        command_list = "\n".join([f"`/{cmd.name}`" for cmd in synced])
        embed.add_field(name="Доступные команды", value=command_list, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка синхронизации: {e}")

@bot.tree.command(name="полная_синхронизация", description="Полная пересинхронизация команд (только для владельца)")
async def полная_синхронизация(interaction: discord.Interaction):
    """Полная пересинхронизация всех команд"""
    if interaction.user.id != bot.owner_id:
        await interaction.response.send_message("❌ Эта команда только для владельца бота!", ephemeral=True)
        return
    
    try:
        # Очищаем все команды
        bot.tree.clear_commands(guild=None)
        
        # Перезагружаем коги
        for cog_name in list(bot.cogs.keys()):
            try:
                await bot.unload_extension(f"cogs.{cog_name.lower()}")
            except:
                pass
        
        await load_cogs()
        
        # Синхронизируем глобально
        synced = await bot.tree.sync()
        
        # Синхронизируем для текущего сервера
        if interaction.guild:
            bot.tree.copy_global_to(guild=interaction.guild)
            guild_synced = await bot.tree.sync(guild=interaction.guild)
        
        embed = discord.Embed(
            title="🔄 Полная синхронизация завершена",
            description=f"Синхронизировано {len(synced)} глобальных команд",
            color=0x00FF00
        )
        
        command_list = "\n".join([f"`/{cmd.name}`" for cmd in synced])
        embed.add_field(name="Доступные команды", value=command_list, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка синхронизации: {e}")

@bot.tree.command(name="перезагрузить", description="Перезагрузить коги (только для владельца)")
async def перезагрузить(interaction: discord.Interaction):
    """Перезагрузить все коги"""
    if interaction.user.id != bot.owner_id:
        await interaction.response.send_message("❌ Эта команда только для владельца бота!")
        return
    
    try:
        # Выгружаем все коги
        for cog_name in list(bot.cogs.keys()):
            await bot.unload_extension(f"cogs.{cog_name.lower()}")
        
        # Загружаем коги заново
        await load_cogs()
        
        # Синхронизируем команды
        await bot.tree.sync()
        
        await interaction.response.send_message("✅ Коги успешно перезагружены!")
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка перезагрузки: {e}")

@bot.tree.command(name="тест", description="Тестовая команда для проверки")
async def тест(interaction: discord.Interaction):
    """Тестовая команда"""
    try:
        # Проверяем базовую функциональность
        embed = discord.Embed(
            title="🧪 Тест системы",
            color=0x00FF00
        )
        
        # Проверяем загрузку когов
        relationships_cog = bot.get_cog("Relationships")
        embed.add_field(
            name="🔗 Relationships Cog",
            value="✅ Загружен" if relationships_cog else "❌ Не загружен",
            inline=True
        )
        
        # Проверяем систему
        if relationships_cog:
            system_loaded = hasattr(relationships_cog, 'system')
            embed.add_field(
                name="⚙️ System",
                value="✅ Загружен" if system_loaded else "❌ Не загружен",
                inline=True
            )
            
            if system_loaded:
                try:
                    characters = relationships_cog.system.list_characters()
                    embed.add_field(
                        name="👥 Персонажи",
                        value=f"✅ {len(characters)} шт." if characters else "❌ Нет персонажей",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name="👥 Персонажи",
                        value=f"❌ Ошибка: {e}",
                        inline=True
                    )
        
        # Проверяем команды
        synced_commands = await bot.tree.fetch_commands()
        embed.add_field(
            name="🎯 Доступные команды",
            value=f"✅ {len(synced_commands)} команд",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка теста: {e}")

# Установка владельца бота
@bot.event
async def on_connect():
    # Получаем ID владельца из переменной окружения
    owner_id = os.getenv("OWNER_ID")
    
    if owner_id:
        try:
            bot.owner_id = int(owner_id)
            print(f"[INFO] OWNER_ID установлен из переменной: {bot.owner_id}")
        except ValueError:
            print(f"[WARNING] Неверный OWNER_ID: {owner_id}")
            # Используем владельца приложения
            app_info = await bot.application_info()
            bot.owner_id = app_info.owner.id
            print(f"[INFO] OWNER_ID установлен как владелец приложения: {bot.owner_id}")
    else:
        # Если OWNER_ID не установлен, используем владельца приложения
        app_info = await bot.application_info()
        bot.owner_id = app_info.owner.id
        print(f"[INFO] OWNER_ID не найден, используется владелец приложения: {bot.owner_id}")
    
    print(f"[INFO] Итоговый OWNER_ID: {bot.owner_id}")

@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.CommandNotFound):
        return  # Игнорируем ошибки ненайденных команд
    elif isinstance(error, commands.NotOwner):
        await ctx.send("❌ Эта команда только для владельца бота!")
    else:
        print(f"[ERROR] Ошибка команды: {error}")
        await ctx.send(f"❌ Произошла ошибка: {error}")

if __name__ == "__main__":
    print("[INFO] Токен найден, запускаем бота...")
    try:
        bot.run(token)
    except Exception as e:
        print(f"[FATAL ERROR] Критическая ошибка запуска: {e}")
        traceback.print_exc()