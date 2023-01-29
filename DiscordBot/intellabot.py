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

client = commands.Bot(command_prefix="!", intents=intents)


def search_through_name_dropdown(driver, first, last):
    textbox = driver.find_element(By.ID, 'global-search-select')
    textbox.send_keys(f'{first} {last}')
    time.sleep(1)
    names = driver.find_elements(By.XPATH, f"//*[contains(text(),'{first}')]")
    return names


def gather_times(times):
    output_list = []
    running_times = ''
    for t in times:
        if str(t.text).__contains__('Event'):
            continue
        if len(running_times) + len(t.text) > 2000:
            output_list.append(running_times)
            running_times = ""
        running_times += f'\n{t.text}'
    if len(running_times) > 0:
        output_list.append(running_times)
    return output_list


def instantiate_driver_for_times(name):
    first = name[0]
    last = name[1]
    driver = selenium.webdriver.Chrome()
    driver.get('https://www.swimcloud.com/?referer=collegeswimming.com')
    time.sleep(.5)
    names = search_through_name_dropdown(driver, first, last)
    first = first.lower()
    last = last.lower()
    return first, last, names, driver


@client.command(name='get_times')
async def get_times(ctx, *args):
    if len(args) <= 1:
        await ctx.send("Command takes a first and last name")
    first, last, names, driver = instantiate_driver_for_times(args)
    await ctx.send(f'Searching times for {first} {last}...')
    matching_names = []
    link_to_page = ''
    name_count = 0
    names.remove(names[0])
    if len(names) > 1:
        await ctx.send('Multiple names found\nEnter command !swim_location first last location')
        for n in names:
            if str(n.text).lower() == f'{first} {last}':
                matching_names.append(n)
            else:
                matching_names.append('Not Matching')
        for n in matching_names:
            name_count += 1
            if type(n) == str and n == 'Not Matching':
                continue
            name_location = f'{n.text}'
            location = n.find_elements(By.XPATH, f"//*[contains(text(), ', ')]")[name_count-1]
            name_location += f'\n {location.text}'
            await ctx.send(name_location)
        return
    if len(matching_names) == 0:
        link_to_page = names[0]
    if type(link_to_page) == str and len(link_to_page) == 0:
        await ctx.send('No times found')
        return
    link_to_page.click()
    name = driver.find_element(By.CLASS_NAME, 'u-mr-')
    if str(name.text).lower() == f'{first} {last}':
        await ctx.send(f'Found times for {first} {last}')
        times_table = driver.find_element(By.ID, 'js-swimmer-profile-times-container')
        times = times_table.find_elements(By.TAG_NAME, 'tr')
        times_list = gather_times(times)
        for t in times_list:
            await ctx.send(t)
    else:
        await ctx.send(f'Could not find times')


@client.command(name='swim_location')
async def get_times_with_location(ctx, *args):
    if len(args) <= 2:  # Fix this
        await ctx.send("Command takes a first and last name as well as a location")
    first, last, names, driver = instantiate_driver_for_times(args)
    await ctx.send(f'Searching times for {first} {last}...')
    matching_names = []
    given_location = ''
    for i in args:
        if i.lower() == first or i.lower() == last:
            continue
        given_location += i.lower()
    link_to_page = ''
    name_count = 0
    names.remove(names[0])
    for n in names:
        if str(n.text).lower() == f'{first} {last}':
            matching_names.append(n)
        else:
            matching_names.append('Not Matching')
    for n in matching_names:
        name_count += 1
        if type(n) == str and n == 'Not Matching':
            continue
        location = n.find_elements(By.XPATH, f"//*[contains(text(), ', ')]")[name_count - 1]
        if str(location.text).replace(' ', '').lower() == given_location:
            link_to_page = names[name_count-1]
            break
    if len(matching_names) == 0:
        link_to_page = names[0]
    if type(link_to_page) == str and len(link_to_page) == 0:
        await ctx.send('No times found')
        return
    link_to_page.click()
    name = driver.find_element(By.CLASS_NAME, 'u-mr-')
    if str(name.text).lower() == f'{first} {last}':
        await ctx.send(f'Found times for {first} {last}')
        times_table = driver.find_elements(By.ID, 'js-swimmer-profile-times-container')
        if len(times_table) == 0:
            await ctx.send(f'Person was found but no times are on their page')
            return
        times = times_table[0].find_elements(By.TAG_NAME, 'tr')
        times_list = gather_times(times)
        for t in times_list:
            await ctx.send(t)
    else:
        await ctx.send(f'Could not find times')


@client.command(name='help_page')
async def help(ctx, *page_num):
    help_list = ['Welcome to help\nType help followed by page number to change pages\n\nCreated by Tyler Besnoff', 'Intellabot commands\n    ! is used in front of a command name to call a command\n\n    get_times "First" "Last"\n        Returns list of times for the given name\n        If there are multiple names matching the name entered the !swim_location command will need to be used\n\n    swim_location "First" "Last" "Location"\n        Returns list of times for the given name and location']
    page = int(page_num[0])if len(page_num) > 0 else 0
    await ctx.send(help_list[page])


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)
    channel = message.channel
    user_message = str(message.content)
    if user_message == "Hello" and str(channel) == "bot-testing":
        await channel.send("Hello World")

client.run(TOKEN)
