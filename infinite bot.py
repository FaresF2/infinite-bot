import discord

from discord.ext import commands, tasks

from discord.voice_client import VoiceClient

from discord.utils import get

import youtube_dl

from random import choice
# ---------------------------------------------------------------------------------------------------------------------



youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
# ---------------------------------------------------------------------------------------------------------------------




client = commands.Bot(command_prefix="-")
client.remove_command('help')
queue = []


@client.event
async def on_ready():
    print("Bot is up and running!")
    await client.change_presence(activity=discord.Activity(name= "-help | Developed by Fares#0001", type=0))

@client.command(name='ping')
async def ping(ctx):
    await ctx.send(f'**Pong!**\n`Latency: {round(client.latency * 1000)} ms`')

@client.command(name='credits')
async def credits(ctx):
    await ctx.send("**Developed by** <@263409149147086850>\n\n\n`note : bot is still under development`")

# ---------------------------------------------------------------------------------------------------------------------
@client.command(aliases=['p', 'P','PLAY'],name='play')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send('You need to enter a voice channel first')
        return
    else:
        channel = ctx.message.author.voice.channel

    try:
        await channel.connect()
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=client.loop)
            voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)

        await  ctx.send(f'**Playing : **{player.title}')
    except Exception:
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=client.loop)
                voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)

            await  ctx.send(f'**Playing : **{player.title}')
        except Exception:
            await ctx.send("A song is already playing, Make sure to skip it first!")


@client.command(name='skip',aliases = ["s","S",'Skip','SKIP'])
async def skip(ctx):
    if not ctx.message.author.voice:
        await ctx.send('You are not in a voice channel with the bot!')
        return
    else:
        voice_client = ctx.message.guild.voice_client
        voice_client.stop()
        await ctx.send("Song skipped!")

@client.command(name='stop',aliases=["STOP","Stop","Disconnect",'disconnect','DISCONNECT','Leave','leave',"LEAVE"])
async def stop(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not in a voice channel with the bot!")
        return
    else:
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()
        await ctx.send("Disconnected!")
# ---------------------------------------------------------------------------------------------------------------------


# --- Error Handling ---
@client.event
async def on_command_error(ctx,error):
     if isinstance(error,commands.MissingPermissions):
     	pass
     elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("There are missing required arguments!, -help if you can't use the command")
     else:
        raise error
# -----------------------



# ----- Clear ------
@client.command(aliases=['c','Clear',"CLEAR"])
@commands.has_permissions(manage_messages = True)
async def clear(ctx,amount=99):
    if amount > 100 :
     await ctx.send("You can't clear more than 100 Messages")
    
    elif amount <= 100 :
        await ctx.channel.purge(limit=amount+1)
        await ctx.send("Messages Deleted Successfully :white_check_mark:", delete_after=2.5)

@clear.error
async def clear_error(ctx,error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You must have **Manage Messages** permission to perform this action!")
	elif isinstance(error,commands.errors.CommandInvokeError):
		await ctx.send("I don't have **Manage Messages** permission to perform this action")
        
# -------------------

# ----- Kick --------
@client.command(aliases=['k', 'K','Kick'])
@commands.has_permissions(kick_members = True)
async def kick(ctx , member : discord.Member ,*, reason= "No Reason Provided"):  
      await member.kick(reason=reason)
      await ctx.send(member.mention + " has been kicked successfully :white_check_mark:")

@kick.error
async def kick_error(ctx,error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You must have **Kick Members** permission to perform this action!")
	elif isinstance(error,commands.errors.CommandInvokeError):
		await ctx.send("I don't have **Kick Members** permission to perform this action")
	else:
		if isinstance(error, commands.errors.MemberNotFound):
			await ctx.send("Member was not found!")

# -------------------


# ----- Ban ---------
@client.command(aliases=['B', 'b','Ban'])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member : discord.Member,*,reason= "No Reason Provided"):
     await member.ban(delete_message_days=0,reason=reason)
     await ctx.send(member.mention + " has been banned successfully :white_check_mark:")

@ban.error
async def ban_error(ctx,error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You must have **Ban Members** permission to perform this action!")
	elif isinstance(error,commands.errors.CommandInvokeError):
		await ctx.send("I don't have **Ban Members** permission to perform this action")
	else:
		if isinstance(error, commands.errors.MemberNotFound):
			await ctx.send("Member was not found!")
#---------------------

# # ----- Unban ------
@client.command(aliases=['Unb', 'UnB','UnBan'])
@commands.has_permissions(ban_members = True)
async def unban(ctx,*,member):
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split('#')

    for banned_entry in banned_users:
      user = banned_entry.user

      if(user.name, user.discriminator)==(member_name,member_disc):
          await ctx.guild.unban(user)
          await ctx.send(f'{user.name}#{user.discriminator} unbanned successfully :white_check_mark:')
          return
    await ctx.send(member+" was not found!") 

@unban.error
async def unban_error(ctx,error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You must have **Ban Members** permission to perform this action!")
	elif isinstance(error,commands.errors.CommandInvokeError):
		await ctx.send("I don't have **Ban Members** permission to perform this action")
	else:
		if isinstance(error, commands.errors.MemberNotFound):
			await ctx.send("Member was not found!")
#--------------------    

# ----- Mute --------
@client.command(aliases=['m', 'Mute','M'])
@commands.has_permissions(manage_roles=True)
async def mute(ctx,member : discord.Member):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if role in member.roles:
        await ctx.send(member.mention + " is already Muted!")
    else:
        await member.add_roles(role)
        await ctx.send(member.mention + " has been muted successfully :white_check_mark:")

@mute.error
async def mute_error(ctx,error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You must have **Manage Roles** permission to perform this action!")
	elif isinstance(error,commands.errors.CommandInvokeError):
		await ctx.send("I don't have **Manage Roles** permission to perform this action or the role **'Muted'** is above my max role!")
	else:
		if isinstance(error, commands.errors.MemberNotFound):
			await ctx.send("Member was not found!")
# -------------------

# ----- UnMute ------
@client.command(aliases=['Unm', 'UnMute','UnM','unm','Unmute'])
@commands.has_permissions(manage_messages=True)
async def unmute(ctx,member : discord.Member):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
   
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send (member.mention + " has been unmuted successfully :white_check_mark:")
    else:
        await ctx.send(member.mention + " is not Muted!")

@unmute.error
async def unmute_error(ctx,error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You must have **Manage Roles** permission to perform this action!")
	elif isinstance(error,commands.errors.CommandInvokeError):
		await ctx.send("I don't have **Manage Roles** permission to perform this action **or** the role **'Muted'** is above my max role!")
	else:
		if isinstance(error, commands.errors.MemberNotFound):
			await ctx.send("Member was not found!")
# -------------------

# --- User Command ---
@client.command(aliases=['whois','info','User','USER'])
async def user(ctx, member : discord.Member):
    embed = discord.Embed(title = "User Info" , color = discord.Colour(0x71368a))
    embed.add_field(name = "Name :", value = member.mention, inline = True)
    embed.add_field(name= "Role :", value = member.top_role)
    embed.add_field(name = "ID :", value = member.id, inline = True)
    embed.add_field(name = "Joined Server :", value = member.joined_at.strftime("`%d/%m/%Y`"))
    embed.add_field(name = "Account Created :", value = member.created_at.strftime("`%d/%m/%Y`"))
    embed.set_image(url = member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.name}"+ '#' + member.discriminator)
    await ctx.send(embed=embed)
# --------------------

# --- Avatar ---
@client.command(aliases=['AVATAR','av','pfp'])
async def avatar(ctx, member : discord.Member):
    t = discord.Embed(color = discord.Colour(0x71368a))
    t.set_author(name = member.name + "#" + member.discriminator,icon_url = member.avatar_url)
    t.set_image(url = member.avatar_url)
    t.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + member.discriminator)
    await ctx.send(embed=t)
# --------------

# help test  

@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title="Help", description="-help <command> for more info about a certain command", color = ctx.author.color)
    
    em.add_field(name="General Commands", value = "avatar , user , ping , credits", inline = False)
    em.add_field(name="Moderation Commands", value = "ban , unban , kick , mute , unmute , clear", inline = False)
    em.add_field(name='Music Commands', value = "play , skip , stop")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def avatar(ctx):
    em = discord.Embed(title = "Avatar", description = "Sends the user's avatar", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-avatar [member]")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)


@help.command()
async def user(ctx):
    em = discord.Embed(title = "User", description = "Sends info about the user", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-user [member]")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def ping(ctx):
    em = discord.Embed(title = "Ping", description = "Sends the bot's latency", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-ping")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def credits(ctx):
    em = discord.Embed(title = "Credits", description = "Credits to the developer", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-credits")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def ban(ctx):
    em = discord.Embed(title = "Ban", description = "Bans the user from the server", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-ban [member]")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def unban(ctx):
    em = discord.Embed(title = "Unban", description = "Unbans the user from the server", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-unban [user#0000] `make sure of capital letters` ")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def kick(ctx):
    em = discord.Embed(title = "Kick", description = "Kicks the user from the server", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-kick [member]")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def mute(ctx):
    em = discord.Embed(title = "Mute", description = "Adds the role \"Muted\" to the user", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-mute [member]")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def unmute(ctx):
    em = discord.Embed(title = "Unmute", description = "Removes the role \"Muted\" from the user", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-unmute [member]")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def clear(ctx):
    em = discord.Embed(title = "Clear", description = "Clears the amount of messages inserted", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-clear [Number of messages]    `max 100` ")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def play(ctx):
    em = discord.Embed(title = "Play", description = "Plays music to the channel you are connected to!", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-play <YT/Soundcloud URL>")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def stop(ctx):
    em = discord.Embed(title = "Stop", description = "Stops the music and leaves the voice channel!", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-stop")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)

@help.command()
async def skip(ctx):
    em = discord.Embed(title = "Skip", description = "Skips the current song!", color = ctx.author.color)
    em.add_field(name = "**Syntax**", value = "-skip")
    em.set_footer(icon_url = ctx.author.avatar_url, text = f'Requested by {ctx.author.name}'+ '#' + ctx.author.discriminator)
    await ctx.send(embed = em)
