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
            print("------Information------\nLogged in as:\nName: {}. \nID: {}. \nCredits to lunar\n----------------------".format(client.user, client.user.id))

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
    # Define the characters for key generation
    letters = string.ascii_letters  # Uppercase and lowercase letters
    digits = string.digits  # Digits (0-9)
    symbols = string.punctuation.replace("-", "")  # Special characters excluding "-"

    # Generate the key with a combination of characters
    key = ''.join(random.choice(letters + digits + symbols) for _ in range(36))

    # Add a "-" character in the key at a random position
    key = key[:8] + "-" + key[8:]

    # Add the key into the database
    db.insert({'key': key, 'user': interaction.user.name, 'duration': duration, 'redeemed': False, 'active': True})

    # Send the generated key in a response
    em = discord.Embed(color=0x0FFF00)
    em.add_field(name="✅ Successfully Generated Key!", value=f'Key: {key}\nExpires: in {duration} days')
    await interaction.response.send_message(embed=em)

@tree.command(name='whitelist', description='real') #guild specific slash command
@app_commands.checks.has_any_role("Creator")
async def selff(interaction: discord.Interaction, user: discord.User, duration: int):
    # Define the characters for key generation
    letters = string.ascii_letters  # Uppercase and lowercase letters
    digits = string.digits  # Digits (0-9)
    symbols = string.punctuation.replace("-", "")  # Special characters excluding "-"

    # Generate the key with a combination of characters
    key = ''.join(random.choice(letters + digits + symbols) for _ in range(15))

    # Add a "-" character in the key at a random position
    key = key[:8] + "-" + key[8:]

    # Create an embed for the generated key
    embed = discord.Embed(title="Key Generation", color=0x00FF00)
    embed.add_field(name="✅ Successfully Generated Key!", value=f"Key: ```{key}```\nExpires in **{duration}** days")

    # Add the username to the key in the database
    db.insert({'key': key, 'user': user.name, 'duration': duration, 'redeemed': False, 'active': True})

    # Send the embed in a direct message to the specified user
    await user.send(embed=embed)

    # Defer the response and send a message in the channel where the command was used
    await interaction.response.defer()
    await interaction.followup.send(f"✅ Successfully Generated Key!\nThe key has been sent to {user.mention}.")

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

@tree.command(name='key', description='Sends you your key')
async def christina(interaction: discord.Interaction):
    user = interaction.user  # Get the user who invoked the command
    query = Query()  # Create a Query instance

    # Check if the user has an active key in the database
    check = db.search((query.user == user.name) & (query.active == True))

    if check:
        key = check[0]['key']  # Get the key from the database
        embed = discord.Embed(title="Key Redemption", description=f"Success! Here is your key: ```{key}```", color=0x00FF00)
        await user.send(embed=embed)
        await interaction.response.send_message(content="Done! Check your DMs!")
    else:
        embed = discord.Embed(title="Key Redemption", description="Unsuccessful, unfortunately you do not have a key with us.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)





client.run("")
