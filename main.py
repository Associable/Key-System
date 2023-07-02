import os
import sys
from colorama import init, Fore
from time import sleep

def install_required_packages():
    required_packages = ["discord", "tinydb"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            os.system(f"pip install {package}")

# Check if required packages are installed
packages_installed = True
required_packages = ["discord", "tinydb"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        packages_installed = False
        break

# Print status message and handle package installation
if packages_installed:
    print(Fore.GREEN + "All required packages installed, loading!" + Fore.RESET)
else:
    user_input = input("Do you want to install required packages? (Y/N): ")
    if user_input.lower() == "y":
        install_required_packages()
    else:
        print(Fore.RED + "Some required packages are missing. Please install them manually." + Fore.RESET)
        sys.exit(3)

# Wait for a few seconds
sleep(3)

# Clear the console
os.system("cls")

# Continue with the rest of the code
import string
import random
import discord
from discord import app_commands
from tinydb import TinyDB, Query

class AClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
            os.system("cls")
            await client.wait_until_ready()
            await client.change_presence(status=discord.Status.idle, activity=discord.Game("Playboi Carti")) # change this to whatever you want
            print("------Information------")
            print(f"Logged in as:")
            print(f"Name: {client.user}.")
            print(f"ID: {client.user.id}.")
            print("Credits to lunar")
            print("----------------------")


client = AClient()
tree = app_commands.CommandTree(client)

db = TinyDB('db.json')
user = Query()

async def get_user_info(user_id):
    user_info = db.get(user.userId == user_id)
    if user_info:
        return user_info
    return None

@tree.command(name='gen_key', description='Generates a key (duration is in days)') #guild specific slash command
@app_commands.checks.has_any_role("Creator")
async def selff(interaction: discord.Interaction, duration: int):
    # gen the key
    generation = string.ascii_letters + string.digits + string.punctuation
    key = "paid-" + ''.join(random.choice(generation) for _ in range(16))

    # get username
    user = None
    
    # send all info to the database
    post = {'key': key, "user": user,"ip": None, 'hwid': None, 'duration': duration, 'used': False}
    db.insert(post)

    # make an embed to send in discord
    em = discord.Embed(color=0x0FFF00)
    em.add_field(name="✅ Successfully Generated Key!", value=f'Key: {key}\nExpires: in {duration} days')
    await interaction.response.send_message(embed=em)

# Redeem
@tree.command(name='redeem', description='Redeem your key')
async def redeem_command(interaction: discord.Interaction, key: str):
    user_query = Query()
    valid = False
    try:
        check = db.search(user_query['key'] == key)
        for check in check:
            if check['key'] == key:
                valid = True
                break
    except:
        pass
    
    check = db.search(user_query['key'] == key)
    for check in check:
        if check['key'] == key:
            check_user = check['user']
            if check_user is not None:
                em = discord.Embed(title='Key has already been redeemed.', color=0xff0000)
                await interaction.response.send_message(embed=em)
                return
    if valid:
        user_info = await get_user_info(interaction.user.id)
        if user_info:
            username = user_info['name']
        else:
            username = interaction.user.display_name
        db.update({'user': username, 'used': True}, user_query['key'] == key)
        em = discord.Embed(color=0x2525ff)
        em.add_field(name='Key Redeemed!', value=f'{username} has been assigned to {key}')
        await interaction.response.send_message(embed=em)
    else:
        em = discord.Embed(title='Invalid Key', color=0xff2525)
        await interaction.response.send_message(embed=em)



client.run("MTA4NjA3MzQ1MzI3MjEwOTA1Nw.GO6yvO.vq38h3rimXVkUMXLbi3rrm_DTLIe-xqMSbVj-M")
