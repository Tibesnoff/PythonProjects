# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import selenium
from selenium.webdriver.common.by import By
import time

intents = discord.Intents.all()

load_dotenv('DISCORD_TOKEN.env')
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix="!", intents=intents )
def searchNames(driver, ctx, first, last):
    textbox = driver.find_element(By.ID, 'global-search-select')
    textbox.send_keys(f'{first} {last}')
    time.sleep(1)
    names = driver.find_elements(By.XPATH, (f"//*[contains(text(),'{first} {last}')]"))
    matching_names = []
    link_to_page = ''
    for n in names:
        if str(n.text) == f'{first} {last}':
            matching_names.append(n)
    return matching_names

@client.command(name='gettimes')
async def get_times(ctx, first, last):
    if len(first) == 0 or len(last) == 0:#Fix this
        await ctx.send("Command takes a first and last name")
    await ctx.send(f'Searching times for {first} {last}...')
    driver = selenium.webdriver.Chrome()
    driver.get('https://www.swimcloud.com/?referer=collegeswimming.com')
    matching_names = searchNames(driver, ctx, first, last)
    link_to_page = ''
    if len(matching_names) > 1:
        await ctx.send('Multiple names found\nEnter command !swimlocation location')
        for n in matching_names:
            name_location = f'{n.text}'
            comma = f', '
            location = n.parent.find_element(By.XPATH, f"//*[contains(text(),',')]") #giving problems
            name_location += f'\n {location.text}'
            await ctx.send(name_location)
        return
    if len(matching_names) > 0:
        link_to_page = matching_names[0]
    if type(link_to_page) == str and len(link_to_page) == 0:
        await ctx.send('No times found')
        return
    link_to_page.click()
    name = driver.find_element(By.CLASS_NAME, 'u-mr-')
    if name.text == f'{first} {last}':
        await ctx.send(f'Found times for {first} {last}')

        timesTable = driver.find_element(By.ID, 'js-swimmer-profile-times-container')
        times = timesTable.find_elements(By.TAG_NAME, 'tr')
        timesList = ""

        for t in times:
            if (str(t.text).__contains__('Event')): continue
            if (len(timesList) + len(t.text) > 2000):
                await ctx.send(timesList)
                timesList = ""
            timesList += f'\n{t.text}'
        await ctx.send(timesList)
    else:
        await ctx.send(f'Could not find times')

@client.command(name='swimlocation')
async def get_times_with_location(ctx, first, last, location):
    if len(first) == 0 or len(last) == 0:
        await ctx.send("Command takes a first and last name as well as a location")
    await ctx.send(f'Searching times for {first} {last}...')
    driver = selenium.webdriver.Chrome()
    driver.get('https://www.swimcloud.com/?referer=collegeswimming.com')
    time.sleep(.5)
    matching_names = searchNames(driver, ctx, first, last, 'none')
    link_to_page = ''
    if len(matching_names) > 1:
        for n in matching_names:
            if str(n.parent.find_element(By.XPATH, f"//*[contains(text(),',')]").text) == f"{location}":
                link_to_page = n
        if link_to_page == '':
            await ctx.send('No times found with that location')
            return
    link_to_page.click()
    name = driver.find_element(By.CLASS_NAME, 'u-mr-')
    if name.text == f'{first} {last}':
        await ctx.send(f'Found times for {first} {last}')
        timesTable = driver.find_element(By.ID, 'js-swimmer-profile-times-container')
        times = timesTable.find_elements(By.TAG_NAME, 'tr')
        timesList = ""
        for t in times:
            if (str(t.text).__contains__('Event')): continue
            if (len(timesList) + len(t.text) > 2000):
                await ctx.send(timesList)
                timesList = ""
            timesList += f'\n{t.text}'
        await ctx.send(timesList)
    else:
        await ctx.send(f'Could not find times')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if (message.author == client.user): return
    await client.process_commands(message)
    channel = message.channel
    user_message=str(message.content)
    if(user_message=="Hello" and str(channel)=="bot-testing"):
        await channel.send("Hello World")

client.run(TOKEN)

