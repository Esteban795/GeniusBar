import builtins
from discord.ext.commands.core import command
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import aiosqlite
import asyncio

load_dotenv()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),description="Le bot du GeniusBar !",intents=discord.Intents.all())
TOKEN = os.getenv("BOT_TOKEN")


class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self,guild:discord.Guild):
        """Create the role muted as soon as the bot joins the guild, if no muted role exists. Disable send messages permissions and speak permissions for muted role in every channel"""
        for role in guild.roles:
            if role.name.lower() == "muted":
                return
        mutedRole = await guild.create_role(name="Muted",permissions=discord.Permissions(send_messages=False,speak=False))
        for channel in guild.channels:
            await channel.set_permissions(mutedRole, send_messages = False, speak = False)
    
    @commands.command(aliases=["addrole","roleadd"])
    @commands.has_permissions(manage_roles=True)
    async def giverole(self,ctx,user:discord.Member,role:discord.Role):
        await user.add_roles(role)
        embedVar = discord.Embed(description=f"{user} was granted the {role} role.",color=0xaaffaa)
        embedVar.set_footer(text=f"Requested by {ctx.author}.")
        await ctx.send(embed=embedVar)

    @commands.command(aliases=["rmvrole"])
    @commands.has_permissions(manage_roles = True)
    async def removerole(self,ctx,user : discord.Member, role:discord.Role): # $removerole [member] [role]
        await user.remove_roles(role)
        embedVar = discord.Embed(description=f"{user} lost the {role} role.",color=0xaaffaa)
        embedVar.set_footer(text=f"Requested by {ctx.author}.")
        await ctx.send(embed=embedVar)

    @commands.command(aliases=["gtfo"])
    @commands.has_permissions(kick_members = True)
    async def kick(self,ctx, user: discord.Member, *,reason="Not specified."): # $kick [member] [reason]
        PMembed = discord.Embed(title="Uh oh. Looks like you did something quite bad !",color=0xff0000)
        PMembed.add_field(name=f"You were kicked from {ctx.guild} by {ctx.author}.",value=f"Reason : {reason}")
        await user.send(embed=PMembed)
        await user.kick(reason=reason)
        embedVar = discord.Embed(description=f"{user} was successfully kicked from the server.",color=0xaaffaa)
        embedVar.set_footer(text=f"Requested by {ctx.author}.")
        await ctx.send(embed=embedVar)

    @commands.command()
    @commands.has_permissions()
    async def mute(self,ctx,user:discord.Member,time:str=None):
        mutedRole = [role for role in ctx.guild.roles if role.name == "Muted"][0]
        await user.add_roles(mutedRole)
        if time is not None:
            await asyncio.sleep(int(time))
            await user.remove_roles(mutedRole)
    
    @commands.command(aliases=["demute"])
    @commands.has_permissions()
    async def unmute(self,ctx,user:discord.Member):
        mutedRole = [role for role in ctx.guild.roles if role.name == "Muted"][0]
        await user.remove_roles(mutedRole)

    @commands.command(aliases=["banl","bl"])
    @commands.has_permissions(administrator = True)
    async def banlist(self,ctx): #Displays current banlist from the server
        bans = await ctx.guild.bans()
        if len(bans) == 0:
            embedVar = discord.Embed(title="Uh oh. Looks like no one is banned on this server. Those are good news !",color=0xaaffaa)
            embedVar.set_footer(text=f"Requested by {ctx.author}.")
            await ctx.send(embed=embedVar)
        else:
            embedVar = discord.Embed(title="Here are all the people banned on this server : ",color=0xaaffaa)
            pretty_list = ["• {}#{} for : {} ".format(entry.user.name,entry.user.discriminator,entry[0]) for entry in bans]
            embedVar.add_field(name=f"There are {len(pretty_list)} of them ! ",value="\n".join(pretty_list))
            embedVar.set_footer(text=f"Requested by {ctx.author}.")
            await ctx.send(embed=embedVar)

    @commands.command(aliases=["b","bna"])
    @commands.has_permissions(ban_members = True)
    async def ban(self,ctx,user : discord.Member,time:str=None, *,reason="Not specified."): # $ban [user] [reason]
        embedVar = discord.Embed(title="Uh oh. Looks like you did something QUITE bad !",color=0xff0000)
        embedVar.add_field(name=f"You were banned from {ctx.guild} by {ctx.author}.",value=f"Reason : {reason}")
        embedVar.set_footer(text=f"Requested by {ctx.author}.")
        await user.send(embed=embedVar)
        await user.ban(reason=reason)
        if time is not None:
            await asyncio.sleep(int(time))
            await ctx.guild.unban(user,reason="Ban duration is over.")

    @commands.command(aliases=["u","unbna"])
    @commands.has_permissions(ban_members = True)
    async def unban(self,ctx,person,*,reason="Not specified."):
        bans = await ctx.guild.bans()
        if len(bans) == 0:
            embedVar = discord.Embed(title="Uh oh. Looks like no one is banned on this server. Those are good news !",color=0xaaffaa)
            return await ctx.send(embed=embedVar)
        elif person == "all":
            for entry in bans:
                user = await bot.fetch_user(entry.user.id)
                await ctx.guild.unban(user)
                embedVar = discord.Embed(title="All members have been successfully unbanned !",color=0xaaffaa)
                return await ctx.send(embed=embedVar)
        count = 0
        dictionary = dict()
        string = ""
        continuer = True
        for entry in bans:
            if "{0.name}#{0.discriminator}".format(entry.user) == person:
                user = await bot.fetch_user(entry.user.id)
                embedVar = discord.Embed(title="{0.name}#{0.discriminator} is now free to join us again !".format(entry.user),color=0xaaffaa)
                embedVar.set_footer(text=f"Requested by {ctx.author}.")
                await ctx.send(embed=embedVar)
                return await ctx.guild.unban(user,reason=reason)
            elif entry.user.name == person:
                    count += 1
                    key = f"{count}- {entry.user.name}#{entry.user.discriminator}"
                    dictionary[key] = entry.user.id
                    string += f"{key}\n"
        if continuer:
            if count >= 1:
                embedVar = discord.Embed(title=f"Uh oh. According to what you gave me, '{person}', I found {count} {'person' if count == 1 else 'people'} named like this.",color=0xaaaaff)
                embedVar.add_field(name="Here is the list of them : ",value=string)
                embedVar.add_field(name="How to pick the person you want to unban ?",value="Just give me the number before their name !")
                embedVar.set_footer(text=f"Requested by {ctx.author}.")
                await ctx.send(embed=embedVar)   
                def check(m):
                    return m.author == ctx.author 
                ans = await bot.wait_for('message',check=check, timeout=10)
                try:
                    emoji = '\u2705'
                    lines = string.split("\n")
                    identifier = int(dictionary[lines[int("{0.content}".format(ans)) - 1]])
                    user = await bot.fetch_user(identifier)
                    await ctx.guild.unban(user)
                    await ans.add_reaction(emoji)
                    embedVar = discord.Embed(title="{0.name}#{0.discriminator} is now free to join us again !".format(user),color=0xaaffaa)
                    embedVar.set_footer(text=f"Requested by {ctx.author}.")
                    await ctx.send(embed=embedVar)
                except:
                    emoji = '\u2705'
                    embedVar = discord.Embed(title="Uh oh. Something went wrong.",color=0xffaaaa)
                    embedVar.add_field(name="For some reasons, I couldn't unban the user you selected.",value="Please try again !")
                    embedVar.set_footer(text=f"Requested by {ctx.author}.")
                    await ctx.send(embed=embedVar)
            else:
                await ctx.send("I can't find anyone with username '{}'. Try something else !".format(person))

    @commands.command(aliases=["p","perrms"])
    @commands.has_permissions(administrator = True)
    async def perms(self,ctx,member:discord.Member):
        embedVar = discord.Embed(title=f"You asked for {member}'s permissions on {ctx.guild}.",color=0xaaaaff)
        embedVar.add_field(name="Here they are : ",value="\n".join(["• {}".format(i[0]) for i in member.guild_permissions if i[1] is True]))
        await ctx.author.send(embed=embedVar)

    @commands.command(aliases=["clear","clearmsg"])
    @commands.has_permissions(manage_messages = True) 
    async def purge(self,ctx,Amount:int=2): #Delete "Amount" messages from the current channel. $purge [int]
        await ctx.channel.purge(limit=Amount + 1)


class Tags(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self,guild:discord.Guild):
        async with aiosqlite.connect("dbs/tags.db") as db:
            await db.execute(f"CREATE TABLE IF NOT EXISTS tags(tag_name TEXT,description TEXT);")
            await db.commit()
    
    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        pass
    
    @commands.group(invoke_without_command=True)
    async def tag(self,ctx,*,tag_name):
        if ctx.invoked_subcommand is None:
            async with aiosqlite.connect("dbs/tags.db") as db:
                async with db.execute(f"SELECT description FROM tags WHERE tag_name = '{tag_name}';") as cursor:
                    async for row in cursor:
                        await ctx.send(row[0])

    @tag.command()
    async def add(self,ctx,tag_name,*,description):
        async with aiosqlite.connect("dbs/tags.db") as db:
            await db.execute(f"INSERT INTO tags VALUES('{tag_name}','{description}')")
            await db.commit()
            await ctx.send(f"Successfully added '{tag_name}' tag.")
    
    @tag.command()
    async def edit(self,ctx,tag_name,*,description):
        async with aiosqlite.connect("dbs/tags.db") as db:
            await db.execute(f"UPDATE tags SET description = REPLACE(description,(SELECT description FROM tags WHERE tag_name = '{tag_name}'),'{description}')")
            await db.commit()
            await ctx.send(f"Succesfully edited '{tag_name}' tag.")

    @tag.command()
    async def remove(self,ctx,*,tag_name):
        async with aiosqlite.connect("dbs/tags.db") as db:
            await db.execute(f"DELETE FROM tags WHERE tag_name = '{tag_name}';")                     
            await db.commit()
            await ctx.send(f"Successfully removed {tag_name} tag.")


class Tickets(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(aliases=["refreshtickets","updatetickets"])
    async def refresh(self,ctx):
        url = "https://lbjs.fr/geniusbar/geniustab.php"
        page = requests.get(url)
        html = page.text
        soup = BeautifulSoup(html,'lxml')
        mydivs = soup.find("tbody").find_all("tr")
        print(mydivs)
        for div in mydivs:
            date = div.find("td",class_="datedemande coldate").text[:-9]
            nom = "\n".join(list(div.find("td",class_="colnom").strings))
            content = list(div.find("td",class_="colmess").strings)
            t = div.find("td",class_="colmess").find("a",attrs={"data-title": content[0]})
            identifier = div.find("td",class_="colnum").text
            if t:
                url = f"https://lbjs.fr/geniusbar{t['href'][1:]}"
                if os.path.isdir("uploaded_files"):
                    os.chdir("uploaded_files")
                img = requests.get(url,allow_redirects=True)
                if not os.path.isfile(f"{t['href'][10:]}"):
                    open(f"{t['href'][10:]}","wb").write(img.content)
            print(f"Date : {date}")
            print(f"Nom : {nom}")
            print(f"Contenu du ticket : {content}")
            print(f"T : {t}")
            print(f"id : {identifier}")
            

            



@bot.event
async def on_ready():
    print(f'Logged as {bot.user.name}')

bot.add_cog(Moderation(bot))
bot.add_cog(Tags(bot))
bot.add_cog(Tickets(bot))

bot.run(TOKEN)

            