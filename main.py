from discord.ext import commands
import music

cogs = [music]
client = commands.Bot(command_prefix='\\')
client.remove_command('help')
for i in range(len(cogs)):
  cogs[i].setup(client)

client.run("ODk3ODQ5OTM0NDk2Mjc2NTAx.YWbp6Q.RSS69jEftslD1C0GjV9n_7T5Rbw")