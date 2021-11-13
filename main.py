from discord.ext import commands
import music
import os
import json

with open("./config.json") as f:
    configData = json.load(f)
token = configData["Token"]
cogs = [music]
client = commands.Bot(command_prefix='\\')
client.remove_command('help')
for i in range(len(cogs)):
    cogs[i].setup(client)

client.run(token)