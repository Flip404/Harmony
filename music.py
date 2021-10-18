import discord
from discord.ext import commands
import youtube_dl
import youtubesearchpython as ysp
import asyncio

user = ''
url_list = []
title_list = {}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': "bestaudio"}


class music(commands.Cog):

    def _init_(self, client):
        self.client = client

    @commands.command()
    async def disconnect(self, ctx):
        await ctx.message.guild.voice_client.disconnect()

    async def check_voice_channel(self, ctx):
        num = False
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!", delete_after=10)
            return num
        else:
            voice_channel = ctx.message.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)
            num = True
            return num

    @commands.command()
    async def play(self, ctx, *, url: str):
        try:
            num = await self.check_voice_channel(ctx)
            if num:
                new_url = ysp.VideosSearch(url, limit=1)
                link = new_url.result()['result'][0]['link']
                title = new_url.result()['result'][0]['title']
                aa = [title , link]
                await ctx.send(title, delete_after=5)
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(link, download=False)
                    url2 = info['formats'][0]['url']
                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                    url_list.append(source)
                    title_list[source] = aa
                vc = ctx.voice_client
                if not vc.is_playing():
                    url_list.remove(source)
                    title_list.pop(source)
                    vc.play(source, after=lambda x=None: self.check_queue(ctx))
                    vc.is_playing()
        except Exception as e:
            await ctx.send(e, delete_after=5)


    def check_queue(self, ctx):
        if url_list:
            voice = ctx.guild.voice_client
            source = url_list.pop(0)
            title_list.pop(source)
            player = voice.play(source, after=lambda x=None: self.check_queue(ctx))

    @commands.command()
    async def queue(self, ctx):
        if url_list:
            embed = discord.Embed(title=f'🎶\t🎶\t🎶\t', description=' ', colour=discord.Colour.blue())
            for url in url_list:
                title , link = title_list[url]
                embed.add_field(name=title, value=link, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("The queue is currently empty!", delete_after=10)

    @commands.command()
    async def next(self, ctx):
        if url_list:
            vc = ctx.voice_client
            num = await self.check_voice_channel(ctx)
            if num:
                vc.stop()
        else:
            await ctx.send("The queue is currently empty!", delete_after=10)

    @commands.command()
    async def ping(self, ctx):
        global user
        ping = round(user.latency * 1000)
        des = f'📶\t{ping} ms'
        embed = discord.Embed(title='🚦Ping🚦', description=des, colour=discord.Colour.blue())
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def help(self, ctx):
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name='🙋Help🙋')
        embed.add_field(name="\\\tplay\n\\\tdisconnect\n\\\tqueue\n\\\tnext\n\\\tping", value="\t🔥\t🔥\t🔥\t", inline=False)
        await ctx.send(embed=embed)


def setup(client):
    global user
    user = client
    client.add_cog(music(client))
