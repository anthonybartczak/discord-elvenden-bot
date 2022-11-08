import asyncio
import typing
import discord
from json import load
import random
import content.tables as tab
import content.pictures as pic
from os import getenv
from dotenv import load_dotenv

load_dotenv()

TEST_GUILD_ID = "868802153014263848"

# Main colors used for the bot's embeded messages formating.
MAIN_COLOR = 0x8b54cf
ERROR_COLOR = 0xff0000
SUCCESS_COLOR = 0x16bd00

# Bot token imported from .env
BOT_TOKEN = getenv('BOT_TOKEN')

# Footer text (version + update date) for every single command.
FOOTER_TEXT = 'Elvie v1.00 - WFRP 4ED\nOstatnia aktualizacja: 8/11/2022'

with open('content/talents.json', encoding="utf8") as jf:
    talents_json = load(jf)
talent_list = list(talents_json.keys())

with open('content/abilities.json', encoding="utf8") as jf:
    abilities_json = load(jf)
abilities_list = list(abilities_json.keys())

# Discord intents declarations -> can be modified at https://discord.com/developers/
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents, command_prefix=".e")
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name=".help"))
    await tree.sync(guild=discord.Object(id=TEST_GUILD_ID))

@tree.command(name = "servers", description = "Sprawdź do ilu serwerów jest połączony Elvie.")
async def servers(ctx):
    servers = list(client.guilds)
    description = 'Połączony z **' + str(len(servers)) + '** serwerami\n\n'
    embed=discord.Embed(title='Lista serwerów', description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.response.send_message(embed=embed)

@tree.command(name = "help", description = "Pokazuje instrukcję bota Elvie.")
async def help(ctx):
    description = \
        'Poniżej znajdziesz listę obecnie dostępnych poleceń. Argumenty oznaczone `*` są opcjonalne:\n\n'\
        '**advance <c/u> <start> <cel> <t*>**\nOblicz koszt rozwoju od `start` do `cel` cechy lub umiejętności (`c` lub `u`). Argument `t` obniża koszt rozwinięcia o 5 PD. Przykładowo:\n`.advance c 12 15` albo `.advance u 5 14 t`\n\n'\
        '**advance_table <m*>**\nWyświetl tabelę *Koszt rozwoju cech i umiejętności w PD*. Argument `m` wyświetla tabelę w wersji na urządzenia mobilne. Przykładowo:\n`.advance_table` albo `.advance_table m`\n\n'\
        '**talent <nazwa>**\nWyświetl opis talentu `nazwa`. Nazwa musi zostać podana z uwzględnieniem polskich znaków oraz bez użycia nawiasów. Przykładowo:\n`.talent bardzo szybki` albo `.talent magia tajemna`\n\n'\
        '**ability <nazwa>**\nWyświetl opis umiejętności `nazwa`. Nazwa musi zostać podana z uwzględnieniem polskich znaków oraz bez użycia nawiasów. Przykładowo:\n`.ability rzemiosło` albo `.ability mocna głowa`\n\nPodziękowania dla Kazyleusz#2024.\n\n'\
        '**miscast <w*>**\nWylosuj mniejszą lub większą (parametr `w`) manifestację. Przykładowo:\n`.miscast` albo `.miscast w`\n\n'\
        '**corruption <p*>**\nWylosuj spaczenie fizyczne lub zepsucie psychiczne (parametr `p`). Przykładowo:\n`.corruption` albo `.corruption p`\n\n'\
        '**fortune**\nWylosuj 4 karty, wybierz jedną i sprawdź czy `Ranald` wysłucha Twej modlitwy.\n\n'\
        '**invite**\nWygeneruj `URL`, dzięki któremu będziesz mógł zaprosić Elviego na własny serwer.\n\n'\

    embed=discord.Embed(title='Krótka instrukcja bota Elvie', description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.response.send_message(embed=embed)

@tree.command(name = "invite", description = "Wygeneruj zaproszenie dla bota Elvie.")
async def invite(ctx):
    embed=discord.Embed(title='Link do zaproszenia', description='https://discord.com/api/oauth2/authorize?client_id=864205486056669244&permissions=1084516330561&scope=bot%20applications.commands', color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.response.send_message(embed=embed)

@tree.command(name = "advance", description = "Oblicz koszt rozwinięcia cechy lub umiejętności.")
async def advance(ctx, type: str, init: int, goal: int, talent: str=None):

    ability_map = {5:10, 10:15, 15:20, 20:30, 25:40, 30:60, 35:80, 40:110, 45:140, 50:180, 55:220, 60:270, 65:320, 70:380, 9999:440}
    attribute_map = {5:25, 10:30, 15:40, 20:50, 25:70, 30:90, 35:120, 40:150, 45:190, 50:230, 55:280, 60:330, 65:390, 70:450, 9999:520}

    if type == 'c':
        chosen_map = attribute_map
        choice = 'cechy'
    elif type == 'u':
        chosen_map = ability_map
        choice = 'umiejętności'

    current = init
    cost_sum = 0

    dif = goal - init
    for key, value in chosen_map.items():
        while current < key and dif != 0:
            cost_sum += value
            current += 1
            dif -= 1

    description = \
        'Twoja początkowa wartość **' + choice + '** to: **' + str(init) + '**\n'\
        'Twoja docelowa wartość **' + choice + '** to: **' + str(goal) + '**\n\n'
    if talent == 't':
        description += 'Jeden z Twoich talentów obniża koszt o **5 PD** za każde rozwinięcie.\n\n'\
        'Finalny koszt rozwinięcia to: **' + str(cost_sum - 5 * (goal - init)) + ' PD**'
    else:
        description += 'Koszt rozwinięcia to: **' + str(cost_sum) + ' PD**'

    embed=discord.Embed(title='Rozwinięcie ' + choice, description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)

    await ctx.response.send_message(embed=embed)

@tree.command(name = "miscast", description = "Wylosuj mniejszą lub większą manifestację.")
async def miscast(ctx, type: str='m'):
    roll = random.randint(1,100)

    if type == 'w':
        table = tab.MISCAST_MAJOR
        name = 'Większa'
    else:
        table = tab.MISCAST_MINOR
        name = 'Mniejsza'

    for i, r in enumerate(range(5, 101, 5)):
        if roll <= r:
            miscast = table[i]
            break

    embed=discord.Embed(title=name + ' manifestacja!', description='Wyrzuciłeś **' + str(roll) + '**...\n\n' + miscast, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.response.send_message(embed=embed)

@tree.command(name = "corruption", description = "Wylosuj spaczenie fizyczne lub psychiczne.")
async def corruption(ctx, type: str='f'):
    roll = random.randint(1,100)

    if type == 'p':
        table = tab.CORRUPTION_MENTAL
        name = 'zepsucie psychiczne!'
    else:
        table = tab.CORRUPTION_PHYSICAL
        name = 'spaczenie fizyczne!'

    for i, r in enumerate(range(5, 101, 5)):
        if roll <= r:
            corruption = table[i]
            break

    embed=discord.Embed(title='Wylosowano ' + name, description='Wyrzuciłeś **' + str(roll) + '**...\n\n' + corruption, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.response.send_message(embed=embed)

@tree.command(name = "fortune", description = "Wylosuj kartę i sprawdź czy Ranald przygląda się Twoim losom!")
async def fortune(ctx):
    await ctx.response.send_message("Jak sobie życzysz...")
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    author = ctx.user
    winner = random.choice(reactions)
    index = reactions.index(winner)
    win_card = pic.WIN_CARDS[index]

    embed=discord.Embed(title='Punkt szczęścia użyty!', description='Czyli Twoja dobra passa się skończyła i nagle chcesz, by sam **Ranald** Ci dopomógł?\n\nDobrze, wybierz kartę śmiertelniku...\n\n', color=MAIN_COLOR)
    embed.set_image(url=pic.CARD_REVERSE)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    message = await ctx.channel.send(embed=embed)
    for emoji in reactions:
        await message.add_reaction(emoji)

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=45.0, check= lambda reaction, user: user == author and str(reaction.emoji) in reactions)

    except asyncio.TimeoutError:
        embed=discord.Embed(title='Za późno...', description=author.mention + ', Twój czas się skończył.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        await ctx.channel.send(embed=embed)
    else:
        if str(reaction.emoji) == winner:
            embed=discord.Embed(title='🤞 Twój wybór...', description='Świetnie ' + author.mention + ', dziś Ranald wysłuchał Twej prośby!', color=SUCCESS_COLOR)
            embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
            embed.set_image(url=win_card)
        else:
            lose_card = pic.LOSE_CARDS[reactions.index(str(reaction.emoji))]
            embed=discord.Embed(title='🤞 Twój wybór...', description=author.mention + ', to był bardzo zły wybór...\n\nSzczęśliwą kartą była karta nr ' + str(winner), color=ERROR_COLOR)
            embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
            embed.set_image(url=lose_card)

        await ctx.channel.send(embed=embed)


@tree.command(name = "advance_table", description = "Wyświetl tabele rozwinięcia cech lub umiejętności.")
async def advance_table(ctx, version: str='pc'):
    if version == 'm':
        image = pic.ADVANCE_TABLE_PIC
        embed=discord.Embed(title='Koszt rozwoju cech i umiejętności w PD', description='', color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        embed.set_image(url=image)
    else:
        description = tab.ADV_TABLE
        embed=discord.Embed(title='Koszt rozwoju cech i umiejętności w PD', description=description, color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.response.send_message(embed=embed)

@tree.command(name = "talent", description = "Wyświetl opis talentu.")
async def talent(ctx, *, talent_name: str):
    talent_name = talent_name.replace(' ','_').lower()

    if talent_name in talents_json:
        talent = talents_json[talent_name]
        await ctx.response.send_message('Talent name found!')
        embed=discord.Embed(title=talent['name'], description=talent['description'], color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        embed.add_field(name="Maksimum", value=talent['max'], inline=True)
        embed.add_field(name="Testy", value=talent['tests'], inline=True)
    else:
        embed=discord.Embed(title='⚠️Nie znalazłem talentu⚠️', description='Pamiętaj o składni podanej w poleceniu **.help**.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)

    await ctx.channel.send(embed=embed)

@talent.autocomplete('talent_name')
async def fruits_autocomplete(
    interaction: discord.Interaction,
    current: str,
    ) -> typing.List[discord.app_commands.Choice[str]]:
        talent_list
        return [
            discord.app_commands.Choice(name=talent, value=talent)
            for talent in talent_list if current.lower() in talent.lower()
        ]

@tree.command(name = "ability", description = "Wyświetl opis umiejętności.")
async def ability(ctx, *, ability_name: str):
    ability_name = ability_name.replace(' ','_').lower()

    if ability_name in abilities_json:
        ability = abilities_json[ability_name]
        await ctx.response.send_message('Ability name found!')
        embed=discord.Embed(title=ability['name'], description=ability['description'], color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        embed.add_field(name="Typ", value=ability['type'], inline=False)
        embed.add_field(name="Cecha", value=ability['attribute'], inline=False)
        embed.add_field(name="Talenty", value=ability['talents'], inline=False)
    else:
        embed=discord.Embed(title='⚠️Nie znalazłem umiejętności⚠️', description='Pamiętaj o składni podanej w poleceniu **.help**.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)

    await ctx.channel.send(embed=embed)

tree.copy_global_to(guild=discord.Object(id=TEST_GUILD_ID))

if __name__ == '__main__':
    client.run(BOT_TOKEN)