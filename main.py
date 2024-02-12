import os
import sys
import string
import random
from colorama import init, Fore
import discord
from discord import app_commands
from tinydb import TinyDB, Query
import fade
import time
from time import sleep

CREATERROLE = "Creator" #Change this with the name of the role you want your admin to be to have access to the bot.


REQUIRED_PACKAGES = ["discord", "tinydb", "colorama", "fade"]
init()

def install_required_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            os.system(f"pip install {package}")

def check_packages_installed():
    return all([package in sys.modules for package in REQUIRED_PACKAGES])

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

def clear_console():
    os.system("cls")

clear_console()

gui = """
/$$       /$$   /$$ /$$   /$$  /$$$$$$  /$$$$$$$ 
| $$      | $$  | $$| $$$ | $$ /$$__  $$| $$__  $$
| $$      | $$  | $$| $$$$| $$| $$  \ $$| $$  \ $$
| $$      | $$  | $$| $$ $$ $$| $$$$$$$$| $$$$$$$/
| $$      | $$  | $$| $$  $$$$| $$__  $$| $$__  $$
| $$      | $$  | $$| $$\  $$$| $$  | $$| $$  \ $$
| $$$$$$$$|  $$$$$$/| $$ \  $$| $$  | $$| $$  | $$
|________/ \______/ |__/  \__/|__/  |__/|__/  |__/
"""

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
            await client.wait_until_ready()
            await client.change_presence(status=discord.Status.dnd, activity=discord.Game("hopelessly in love"))
            print("{gui}\n \n------Information------\nLogged in as:\nName: {user}. \nID: {user.id}. \nCredits to lunar\n----------------------".format(gui=gui, user=client.user))


client = AClient()
tree = app_commands.CommandTree(client)

db = TinyDB('db.json')
user = Query()

async def get_user_info(user_id):
    user_info = db.get(user.userId == user_id)
    return user_info

def generate_key(length=30):
    characters = string.ascii_letters + string.digits + string.punctuation.replace("-", "")
    key = ''.join(random.choice(characters) for _ in range(length))
    return key[:8] + "-" + key[8:]

@tree.command(name='gen_key', description='Generates a key (duration is in days)')
@app_commands.checks.has_any_role(CREATERROLE)
async def generate_key_command(interaction: discord.Interaction, duration: int):
    key = generate_key(30)
    db.insert({'key': key, 'user': interaction.user.name, 'duration': duration, 'redeemed': False, 'active': True})
    em = discord.Embed(color=0x0FFF00)
    em.add_field(name="✅ Successfully Generated Key!", value=f'Key: {key}\nExpires: in {duration} days')
    await interaction.response.send_message(embed=em)

@tree.command(name='whitelist', description='Whitelist a user by generating a key')
@app_commands.checks.has_any_role(CREATERROLE)
async def whitelist_command(interaction: discord.Interaction, user: discord.User, duration: int):
    user_query = Query()
    existing_key = db.search(user_query.user == user.name)

    if existing_key:
        embed = discord.Embed(title="Whitelist Status", color=0xFFFF00)
        embed.add_field(name="⚠️ Already Whitelisted!", value=f"{user.mention} is already whitelisted.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    key = generate_key(30)
    embed = discord.Embed(title="Key Generation", color=0x00FF00)
    embed.add_field(name="✅ Successfully Generated Key!", value=f"Key: ```{key}```\nExpires in **{duration}** days")
    db.insert({'key': key, 'user': user.name, 'duration': duration, 'redeemed': False, 'active': True})
    await user.send(embed=embed)
    await interaction.response.defer()
    await interaction.followup.send(f"✅ Successfully Generated Key!\nThe key has been sent to {user.mention}.")

@tree.command(name='redeem', description='Redeem your key')
async def redeem_command(interaction: discord.Interaction, key: str):
    user_query = Query()
    valid_keys = db.search(user_query['key'] == key)
    if not valid_keys:
        em = discord.Embed(title='Invalid Key', color=0xff2525)
        await interaction.response.send_message(embed=em)
        return
    for check in valid_keys:
        if check['key'] == key and check['user']:
            em = discord.Embed(title='Key has already been redeemed.', color=0xff0000)
            await interaction.response.send_message(embed=em)
            return
    user_info = await get_user_info(interaction.user.id)
    username = user_info['name'] if user_info else interaction.user.display_name
    db.update({'user': username, 'used': True}, user_query['key'] == key)
    em = discord.Embed(color=0x2525ff)
    em.add_field(name='Key Redeemed!', value=f'{username} has been assigned to {key}')
    await interaction.response.send_message(embed=em)

@tree.command(name='check_key', description='Sends you your key')
async def key_command(interaction: discord.Interaction):
    user = interaction.user
    query = Query()
    check = db.search((query.user == user.name) & (query.active == True))
    if check:
        key = check[0]['key']
        embed = discord.Embed(title="Key Redemption", description=f"Success! Here is your key: ```{key}```", color=0x00FF00)
        await user.send(embed=embed)
        await interaction.response.send_message(content="Done! Check your DMs!")
    else:
        embed = discord.Embed(title="Key Redemption", description="Unsuccessful, unfortunately you do not have a key with us.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name='unwhitelist', description='Unwhitelist a user by deleting their key')
@app_commands.checks.has_any_role(CREATERROLE)
async def unwhitelist_command(interaction: discord.Interaction, user: discord.User):
    user_query = Query()
    # Find the key associated with the provided user_id
    key_entry = db.get(user_query.user == user.name)
    if key_entry:
        # Delete the key entry from the database
        db.remove(doc_ids=[key_entry.doc_id])
        response = f"User `{user.name}` (ID: {user.id}) has been successfully unwhitelisted."
        color = 0x00FF00  # Green color for success
    else:
        response = f"No key associated with user `{user.name}` (ID: {user.id}) found."
        color = 0xFF0000  # Red color for failure
    # Send response
    em = discord.Embed(title="Unwhitelist User", description=response, color=color)
    await interaction.response.send_message(embed=em)


client.run("MTE5MzkzOTIzMDIwOTA4OTU0Ng.GNPQ44.DnQuAVaJFQTPfKRQRh1ZNkhWuSwapvGUR29xd0")
