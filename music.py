import discord
from discord.ext import commands
import youtube_dl
import youtubesearchpython as ysp
import asyncio
import validators

user = ''
url_list = []
title_list = {}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio'}


class music(commands.Cog):

    def _init_(self, client):
        self.client = client

    @commands.command()
    async def disconnect(self, ctx):
        url_list.clear()
        title_list.clear()
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

    async def current_playing(self, ctx, source):
        title, link = title_list[source]
        embed = discord.Embed(title=f"Currently Playing : {title} 🎶", url=link, colour=discord.Colour.blue())
        await ctx.send(embed=embed, delete_after=60)

    @commands.command()
    async def play(self, ctx, *, url: str):
        try:
            num = await self.check_voice_channel(ctx)
            if num:
                url_valid = validators.url(url)
                if not url_valid:
                    new_url = ysp.VideosSearch(url, limit=1)
                    url = new_url.result()['result'][0]['link']
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    url2 = info['formats'][0]['url']
                    title = info['title']
                    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                    url_list.append(source)
                    title_list[source] = [title, url]
                vc = ctx.voice_client
                if not vc.is_playing():
                    await self.current_playing(ctx, source)
                    url_list.remove(source)
                    title_list.pop(source)
                    vc.play(source, after=lambda x=None: asyncio.run(self.check_queue(ctx)))
                    vc.is_playing()
                else:
                    title, link = title_list[source]
                    embed = discord.Embed(title=f"🔔 Added to Queue : {title}", url=link, description="", colour=discord.Colour.blue())
                    await ctx.send(embed=embed, delete_after=60)
        except Exception as e:
            await ctx.send(e, delete_after=30)

    async def check_queue(self, ctx):
        try :
            if url_list:
                voice = ctx.guild.voice_client
                source = url_list.pop(0)
                await self.current_playing(ctx, source)
                title_list.pop(source)
                voice.play(source, after=lambda x=None: asyncio.run(self.check_queue(ctx)))
            else:
                async with timeout(60):
                    await self.disconnect(ctx)
        except RuntimeError:
            pass

    @commands.command()
    async def queue(self, ctx):
        if url_list:
            embed = discord.Embed(title=f'🎶\t🎶\t🎶\t', description=' ', colour=discord.Colour.blue())
            for url in url_list:
                title, link = title_list[url]
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
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        else:
            await ctx.send("You are not currently playing!", delete_after=10)

    @commands.command()
    async def ping(self, ctx):
        ping = round(user.latency * 1000)
        des = f'📶\t{ping} ms'
        embed = discord.Embed(title='🚦Ping🚦', description=des, colour=discord.Colour.blue())
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def help(self, ctx):
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name='🙋Help🙋')
        embed.add_field(name="\\\tplay\n\\\tdisconnect\n\\\tqueue\n\\\tnext\n\\\tping", value="\t🔥\t🔥\t🔥\t",
                        inline=False)
        await ctx.send(embed=embed)


def setup(client):
    global user
    user = client
    client.add_cog(music(client))
