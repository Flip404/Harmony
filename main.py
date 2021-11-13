from discord.ext import commands
import music
import os
import json

if os.path.exists(os.getcwd() + "/config.json"):

    with open("./config.json") as f:
        configData = json.load(f)

else:
    configTemplate = {"Token": ""}

    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]
cogs = [music]
client = commands.Bot(command_prefix='\\')
client.remove_command('help')
for i in range(len(cogs)):
    cogs[i].setup(client)

client.run(token)