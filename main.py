import os
import sys
import string
import random
import datetime
import pymongo
import discord
from discord import app_commands
from discord.ext import commands
from colorama import init, Fore
import time
from typing import Optional 

# Constants
CREATERROLE = "panel access"
BUYERROLE = "Customer"
REQUIRED_PACKAGES = ["discord", "pymongo", "colorama"]
MONGO_URI = ""
DB_NAME = ""
COLLECTION_NAME = ""
TOKEN_FILE = "token.txt"

# Emoji Constants
EMOJI_FLAMES = "<a:flames:1218848265814937630>"
EMOJI_ARROW = "<:black_arrow:1218851568175157298>"
EMOJI_VERIFIED = "<a:Verified_Black_Animated:1218852684845682778>"

gui = """
/$$       /$$   /$$ /$$   /$$  /$$$$$$  /$$$$$$$ 
| $$      | $$  | $$| $$$ | $$ /$$__  $$| $$__  $$
| $$      | $$  | $$| $$$$| $$| $$  \ $$| $$  \ $$
| $$      | $$  | $$| $$ $$ $$| $$$$$$$$| $$$$$$$/
| $$      | $$  | $$| $$  $$$$| $$__  $$| $$__  $$       on top
| $$      | $$  | $$| $$\  $$$| $$  | $$| $$  \ $$
| $$$$$$$$|  $$$$$$/| $$ \  $$| $$  | $$| $$  | $$
|________/ \______/ |__/  \__/|__/  |__/|__/  |__/
"""

# Function to install required packages
def install_required_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            os.system(f"pip install {package}")

# Check if all required packages are installed
def check_packages_installed():
    return all([package in sys.modules for package in REQUIRED_PACKAGES])

# Print status message
def print_status_message(installed):
    if installed:
        print(Fore.GREEN + "All required packages installed, loading!" + Fore.RESET)
    else:
        user_input = input("Do you want to install required packages? (Y/N): ")
        if user_input.lower() == "y":
            install_required_packages()
        else:
            print(Fore.RED + "Some required packages are missing. Please install them manually." + Fore.RESET)
            sys.exit(3)

# Clear console
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

# Load token
def load_token():
    with open(TOKEN_FILE, "r") as file:
        return file.read().strip()

# Generate a key
def generate_key(length=15):
    characters = string.ascii_letters + string.digits + string.punctuation.replace("-", "")
    key = ''.join(random.choice(characters) for _ in range(length))
    return key[:8] + "-" + key[8:]

# Generate a key document
def generate_key_document(user, duration, hwid=None):
    return {
        'key': generate_key(),
        'user': user,
        'duration': duration,
        'hwid': hwid or "",
        'redeemed': False,
        'active': False,
        'generated_time': datetime.datetime.utcnow()
    }

# Define bot class
class AClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
            clear_console()
            await self.change_presence(status=discord.Status.dnd, activity=discord.Game("hopelessly in love"))
            print(f"{gui}\n \n------Information------\nLogged in as:\nName: {self.user}. \nID: {self.user.id}. \nCredits to lunar\n----------------------")

# Command tree
intents = discord.Intents.default()
intents.message_content = True
client = AClient()
tree = app_commands.CommandTree(client)

# MongoDB connection
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# Commands
@tree.command(name='gen_key', description='Generates a key (duration is in days)')
@app_commands.checks.has_any_role(CREATERROLE)
async def generate_key_command(interaction: discord.Interaction, duration: int, hwid: Optional[str] = None):
    key_document = generate_key_document(interaction.user.name, duration, hwid)
    
    collection.insert_one(key_document)
    key = key_document['key']
    collection.update_one({'key': key}, {"$set": {'active': True}})
    
    em = discord.Embed(title="𝕍estra | Auth", description=f"{EMOJI_FLAMES} ** License generated successfully! ** {EMOJI_FLAMES}", color=0xFFFFFF)
    em.add_field(name=f"{EMOJI_ARROW} Generated License:", value=f"```{key}```", inline=False)
    em.add_field(name="Expires:", value=f"In **{duration}** days", inline=False)
    
    if hwid:
        em.add_field(name="HWID:", value=hwid, inline=False)

    em.set_footer(text="authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
    await interaction.response.send_message(embed=em)

@tree.command(name='whitelist', description='Whitelist a user by generating a key (duration is in days)')
@app_commands.checks.has_any_role(CREATERROLE)
async def whitelist_command(interaction: discord.Interaction, user: discord.User, duration: int, hwid: Optional[str] = None):
    if collection.find_one({"user": user.name}):
        embed = discord.Embed(title="Whitelist Status", description=f"{EMOJI_VERIFIED} {user.mention} is already whitelisted.", color=0xFFFFFF)
        embed.set_footer(text="authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    key_document = generate_key_document(user.name, duration, hwid)
    key = key_document['key']
    collection.insert_one(key_document)
    
    embed = discord.Embed(title="Whitelist Success", description=f"{EMOJI_ARROW} Successfully Whitelisted {user.mention}!", color=0xFFFFFF)
    embed.add_field(name="Generated Key:", value=f"```{key}```", inline=False)
    embed.add_field(name="Expires in:", value=f"**{duration}** days", inline=False)
    if hwid:
        embed.add_field(name="HWID:", value=hwid, inline=False)
    embed.set_footer(text="authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)

    await user.send(embed=embed)
    await interaction.response.defer()
    await interaction.followup.send(f"{EMOJI_ARROW} Successfully Generated Key!\nThe key has been sent to {user.mention}.", ephemeral=True)

@tree.command(name='redeem', description='Redeem your key')
async def redeem_key_command(interaction: discord.Interaction, key: str):
    user = interaction.user.name
    key_entry = collection.find_one({"key": key})

    if key_entry:
        if key_entry['active']:
            if not key_entry['redeemed']:
                collection.update_one({"key": key}, {"$set": {'redeemed': True, 'user': user}})
                response = f"{EMOJI_VERIFIED} Key `{key}` redeemed successfully by {user}."
                color = 0xFFFFFF
            else:
                response = f"{EMOJI_VERIFIED} Key `{key}` has already been redeemed."
                color = 0xFF0000
        else:
            response = f"{EMOJI_VERIFIED} Key `{key}` is not active."
            color = 0xFF0000
    else:
        response = f"{EMOJI_VERIFIED} No key `{key}` found."
        color = 0xFF0000
    
    em = discord.Embed(title="Redeem Key", description=response, color=color)
    em.add_field(name="Redeemed Key:", value=f"```{key}```", inline=False)
    em.set_footer(text="Authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
    await interaction.response.send_message(embed=em)

@tree.command(name='check_key', description='Sends you your key')
async def key_command(interaction: discord.Interaction):
    user = interaction.user
    check = collection.find_one({"user": user.name, "active": True})

    if check:
        key = check['key']
        embed = discord.Embed(title="Key Redemption", description=f"{EMOJI_FLAMES} Success! Here is your key: ```{key}```", color=0xFFFFFF)
        embed.set_footer(text="Authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
        await user.send(embed=embed)
        await interaction.response.send_message(content=f"{EMOJI_ARROW} Done! Check your DMs!", ephemeral=True)
    else:
        embed = discord.Embed(title="Key Redemption", description=f"{EMOJI_ARROW} Unsuccessful, unfortunately you do not have a key with us.", color=0xFFFFFF)
        embed.set_footer(text="Authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name='delete_key', description='Unwhitelist a user by deleting their key')
@app_commands.checks.has_any_role(CREATERROLE)
async def unwhitelist_command(interaction: discord.Interaction, user: discord.User):
    result = collection.delete_one({"user": user.name})

    if result.deleted_count > 0:
        response = f"User `{user.name}` (ID: {user.id}) has been successfully removed."
        color = 0x00FF00
    else:
        response = f"No key associated with user `{user.name}` (ID: {user.id}) found."
        color = 0xFF0000

    em = discord.Embed(title="Unwhitelist User", description=response, color=color)
    await interaction.response.send_message(embed=em)

@tree.command(name='give-role', description='Give a role to a user')
@app_commands.checks.has_any_role(CREATERROLE)
async def giverole_command(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message("I don't have permission to manage roles.")
        return
    
    if role.position >= interaction.guild.me.top_role.position:
        await interaction.response.send_message("I cannot assign this role because it is higher than my top role.")
        return
    
    if role in user.roles:
        await interaction.response.send_message(f"{user.mention} already has the {role.name} role.")
        return
    
    await user.add_roles(role)
    await interaction.response.send_message(f"Successfully gave {user.mention} the {role.name} role.")

@tree.command(name='sync', description='Owner only')
async def sync_command(interaction: discord.Interaction):
    if interaction.user.id == 754386737542725725:
        await tree.sync()
        print('Command tree synced.')
    else:
        await interaction.response.send_message('You must be the owner to use this command!')

@tree.command(name='resethwid', description='Resets hardware ID')
@app_commands.checks.has_any_role(BUYERROLE)
async def resethwid_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_key = collection.find_one({"user": interaction.user.name})

    if not user_key:
        embed = discord.Embed(title="Reset Hardware ID", description="[-] No license connected, please buy a license.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)
        return

    cooldown_key = f"cooldown_{user_id}"
    cooldown_time = collection.find_one({"key": cooldown_key})

    if cooldown_time and time.time() - cooldown_time["time"] < 259200:
        cooldown_remaining = 259200 - (time.time() - cooldown_time["time"])
        cooldown_hours = int(cooldown_remaining // 3600)
        cooldown_minutes = int((cooldown_remaining % 3600) // 60)
        embed = discord.Embed(title="Reset Hardware ID", description=f"[-] Please wait {cooldown_hours} hours and {cooldown_minutes} minutes longer to use this command again.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)
        return

    collection.update_one({"user": interaction.user.name}, {"$set": {"hwid": ""}})
    
    if cooldown_time:
        collection.delete_one({"_id": cooldown_time["_id"]})
    
    collection.update_one({"key": cooldown_key}, {"$set": {"time": time.time()}}, upsert=True)
    
    embed = discord.Embed(title="Reset Hardware ID", description=f"{EMOJI_VERIFIED} Done! Your Hardware ID is reset and will be on cooldown for 3 days.", color=0xFFFFFF)
    embed.set_footer(text="authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
    await interaction.response.send_message(embed=embed)

@tree.command(name='force_resethwid', description='Force reset hardware ID without cooldown (Admin only)')
@app_commands.checks.has_any_role(CREATERROLE)
async def force_resethwid_command(interaction: discord.Interaction, user: discord.User):
    if not collection.find_one({"user": user.name}):
        embed = discord.Embed(title="Force Reset Hardware ID", description="No license connected for the specified user.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)
        return

    collection.update_one({"user": user.name}, {"$set": {"hwid": ""}})
    embed = discord.Embed(title="Force Reset Hardware ID", description=f"{EMOJI_VERIFIED} Done! Hardware ID for {user.mention} has been reset.", color=0xFFFFFF)
    embed.set_footer(text="Authenticated by: " + interaction.user.name, icon_url=interaction.user.avatar)
    await interaction.response.send_message(embed=embed)

# Main function
if __name__ == "__main__":
    clear_console()
    print_status_message(check_packages_installed())
    client.run(load_token())
