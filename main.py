import discord
import requests
import base64
import json
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='/', intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Check if the message is a lookup command
    if message.content.startswith("/lookup"):
        # Retrieve the Minecraft username from the command argument
        username = message.content[8:]

        # Make a GET request to the Mojang API to retrieve the UUID of the user
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if response.status_code != 200:
            await message.channel.send(f"No UUID found for Minecraft user {username}")
            return
        uuid = response.json()["id"]

        # Use the UUID to get the skin and cape URLs from the Mojang API
        skin_response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        skin_data = skin_response.json()
        properties = skin_data.get("properties", [])
        skin_url = None
        cape_url = None
        for prop in properties:
            if prop.get("name") == "textures":
                skin_url = prop.get("value")
            elif prop.get("name") == "cape":
                cape_url = prop.get("value")

        # Create the embed message
        embed = discord.Embed(title="Minecraft user lookup", color=0x00ff00)
        embed.add_field(name="Username", value=username, inline=True)
        if skin_url:
            decoded_string = base64.b64decode(skin_url).decode("utf-8")
            skin_dict = json.loads(decoded_string)
            skin_url = skin_dict['textures']['SKIN']['url']
            embed.set_thumbnail(url=f"https://crafatar.com/renders/body/{uuid}")
            embed.add_field(name="Skin URL", value=f"[View Skin]({skin_url})", inline=False)
        if cape_url:
            decoded_string = base64.b64decode(cape_url).decode("utf-8")
            cape_dict = json.loads(decoded_string)
            cape_url = cape_dict['textures']['CAPE']['url']
            embed.add_field(name="Cape URL", value=f"[View Cape]({cape_url})", inline=False)

        # Read the W/L record for the user from the file
        with open("assignment.txt", "r") as f:
            for line in f:
                if line.startswith(username):
                    w_l_record = line[len(username):].strip()
                    embed.add_field(name="W/D/L Record", value=w_l_record, inline=False)
                    break

        # Read recent events for the user from the file
        with open("recent_events.txt", "r") as f:
            for line in f:
                if line.startswith("event " + username):
                    events = line[len("event " + username):].strip()
                    embed.add_field(name="Recent Events", value=events, inline=False)
                    break
        
        with open("countries.txt", "r") as f:
            for line in f:
                if line.startswith(username):
                    countries = line[len(username):].strip()
                    embed.add_field(name="Country", value=countries, inline=False)
                    break

        await message.channel.send(embed=embed)

        

    # Check if the message is an assign command
    if message.content.startswith("/assign"):
        # Send a direct message to the user asking for their password
        password_msg = await message.author.send("Please enter your password:")

        # Wait for the user's response in DM
        def check(msg):
            return msg.author == message.author and msg.channel == password_msg.channel
        password_response = await client.wait_for('message', check=check)

        # Check if the password is correct (in this example, the password is "password123")
        if password_response.content == "WBC000":
            # Retrieve the Minecraft username from the command argument
            username = message.content[8:].strip()

            # Prompt the user to enter a W or L
            wl_msg = await message.author.send("Enter W, L or D :")
            wl_response = await client.wait_for('message', check=check)

            # Open the file in read mode and read the contents
            with open("assignment.txt", "r") as f:
                lines = f.readlines()

            # Find the index of the line containing the user's name, if it exists
            user_index = None
            user_found = False
            for i, line in enumerate(lines):
                if line.startswith(username):
                    user_index = i
                    user_found = True
                    break

            # Modify the user's entry if it exists, or create a new entry
            if user_found:
                line = lines[user_index].rstrip('\n')
                lines[user_index] = f"{line} {wl_response.content} •\n"
            else:
                lines.append(f"{username} {wl_response.content} •\n")

            # Open the file in write mode and write the updated contents
            with open("assignment.txt", "w") as f:
                f.writelines(lines)

            # Send a confirmation message to the user
            await message.author.send(f"Assignment recorded for {username}!")
        else:
            await message.author.send("Password is incorrect.")

    # Check if the message is an record_Event command
    if message.content.startswith("/record_event"):

        password_2nd = await message.author.send("Please enter the password:")

        def check(msg):
            return msg.author == message.author and msg.channel == password_2nd.channel
        password_response_2nd = await client.wait_for('message', check=check)

        if password_response_2nd.content == "WBC000":
            # Retrieve the Minecraft username from the command argument
            username = message.content[8:].strip()

            re_message = await message.author.send("Enter event to record : ")
            re_response = await client.wait_for('message', check=check)

            with open("recent_events.txt", "r") as f:
                lines = f.readlines()

            user_index = None
            user_found = False
            for i, line in enumerate(lines):
                if line.startswith(username):
                    user_index = i
                    user_found = True
                    break
            # Modify the user's entry if it exists, or create a new entry
            if user_found:
                line = lines[user_index].rstrip('\n')
                lines[user_index] = f"{line} {re_response.content} •\n"
            else:
                lines.append(f"{username} {re_response.content} •\n")
                
            with open("recent_events.txt", "w") as f:
                f.writelines(lines)

            # Send a confirmation message to the user
            await message.author.send(f"Event assigned to {username}!")
        else:
            await message.author.send("Password is incorrect.")

    if message.content.startswith("/country"):

        password_3rd = await message.author.send("Please enter the password:")

        def check(msg):
            return msg.author == message.author and msg.channel == password_3rd.channel
        password_response_3rd = await client.wait_for('message', check=check)

        if password_response_3rd.content == "":
            # Retrieve the Minecraft username from the command argument
            username = message.content[8:].strip()

            cy_message = await message.author.send("Enter Country : ")
            cy_response = await client.wait_for('message', check=check)

            with open("countries.txt", "r") as f:
                lines = f.readlines()

            user_index = None
            user_found = False
            for i, line in enumerate(lines):
                if line.startswith(username):
                    user_index = i
                    user_found = True
                    break
            # Modify the user's entry if it exists, or create a new entry
            if user_found:
                line = lines[user_index].rstrip('\n')
                lines[user_index] = f"{line} {cy_response.content}\n"
            else:
                lines.append(f"{username} {cy_response.content}\n")
                
            with open("countries.txt", "w") as f:
                f.writelines(lines)

            # Send a confirmation message to the user
            await message.author.send(f"Country Assigned to {username}!")
        else:
            await message.author.send("Password is incorrect.")


client.run("")
# https://discord.com/api/oauth2/authorize?client_id=1099610094708215808&permissions=8&scope=bot