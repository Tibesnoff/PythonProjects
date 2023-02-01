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
        for n in names:
            if str(n.text).lower() == f'{first} {last}':
                matching_names.append(n)
            else:
                matching_names.append('Not Matching')
        flag = 0
        if type(matching_names) != str:
            for i in matching_names:
                if str(i.text).lower() == (f'{first} {last}'):
                    await ctx.send('Multiple names found\nEnter command !swim_location first last location')
                    flag = 1
                    break
        if flag == 0:
            await ctx.send('No times found')
            return
        location = names[0].find_elements(By.XPATH, f"//*[contains(text(), ', ')]")
        for n in matching_names:
            name_count += 1
            if type(n) == str and n == 'Not Matching':
                continue
            name_location = f'{str(n.text)}'
            name_location += f'\n{location[name_count].text}'
            await ctx.send(name_location)
        return
    if len(names) == 0:
        await ctx.send('No times found')
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
    flag = 0
    if type(matching_names) != str:
        for i in matching_names:
            if str(i.text).lower() == (f'{first} {last}'):
                matching_names.append(i)
                flag = 1
            else:
                matching_names.append('Not Matching')
    if flag == 0:
        await ctx.send('No times found')
        return
    print(matching_names)
    for n in matching_names:
        name_count += 1
        if type(n) == str and n == 'Not Matching':
            continue
        location = n.find_elements(By.XPATH, f"//*[contains(text(), ', ')]")[name_count - 1]
        if str(location.text).replace(' ', '').lower() == given_location:
            link_to_page = names[name_count - 1]
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


@client.command(name='ttt')
async def setup_tik_tak_toe(ctx, player: discord.User, reset=1):
    try:
        if reset == 0:
            await ctx.send('Game is resetting')
            reset_game()
        else:
            await ctx.send('You did not elect to reset the game\nReenter the ttt command with the number 0 after your opponent')
            return
    except Exception:
        print(Exception)
    ttt_data = get_ttt_data()
    if type(ttt_data) == str and ttt_data == 'corrupt':
        reset_game()
        await ctx.send('Game file corrupt')
        return
    else:
        file_contents = ttt_data[0]
    if len(file_contents) == 5:
        ttt_board = ttt_data[7]
        player1 = ttt_data[4]
        player2 = ttt_data[5]
        round_counter = int(ttt_data[6])
        if round_counter == 0:
            player1 = str(ctx.author.name)
            player2 = str(player.name)
            file_contents[0] = player1
            file_contents[1] = player2
            await ctx.send(f"Player1: {player1}\nPlayer2: {player2}")
    else:
        reset_game()
        await ctx.send('Game file corrupt')
        return
    write_to_ttt_file(ttt_data[1], ttt_data[2], ttt_board, player1, player2, round_counter, ttt_data[3])
    ttt_data[3].close()


def get_ttt_data():
    path = '../DiscordBot/'
    file = 'ttt_board.txt'
    try:
        ttt_board_file = open('ttt_board.txt', 'r')
    except Exception as exc:
        ttt_board_file = open(os.path.join(path, file), 'r+')
    file_contents = ttt_board_file.readlines()
    if len(file_contents) == 5:
        ttt_board = []
        player1 = file_contents[0].strip()
        player2 = file_contents[1].strip()
        game_board = file_contents[2].strip().split(',')
        player_board = file_contents[3].strip().split(',')
        round_counter = int(file_contents[4])
        for i in game_board:
            for j in player_board:
                ttt_board.append((int(i), int(j)))
                player_board.remove(j)
                break
    else:
        return 'corrupt'
    return file_contents, path, file, ttt_board_file, player1, player2, round_counter, ttt_board, game_board


def write_to_ttt_file(path, file, ttt_board, player1, player2, round_counter, ttt_file):
    ttt_file.close()
    ttt_board_file = open(os.path.join(path, file), 'w')
    game_board = ''
    player_board = ''
    for i in ttt_board:
        game_board += f'{str(i[0])},'
        player_board += f'{str(i[1])},'
    overwrite_string = f'{str(player1)}\n{str(player2)}\n{str(game_board[:-1])}\n{str(player_board[:-1])}\n{round_counter}'
    ttt_board_file.write(overwrite_string)
    ttt_board_file.close()
    return


@client.command(name='p')
async def play_ttt(ctx, spot):
    try:
        spot = int(spot)
    except Exception:
        await ctx.send('Enter a number')
        return
    ttt_data = get_ttt_data()
    if not (str(ctx.author.name) == str(ttt_data[4])) ^ (str(ctx.author.name) == str(ttt_data[5])):
        await ctx.send('You are not playing the game right now')
        return
    file_contents = ttt_data[0]
    if len(file_contents) == 5:
        ttt_board = ttt_data[7]
        player1 = ttt_data[4]
        player2 = ttt_data[5]
        round_counter = int(ttt_data[6])
        if (round_counter+1) % 2 == 0:
            if str(ctx.author.name) == str(player1):
                await ctx.send('It is not your turn')
                return
            if check_not_taken(ttt_board, spot) == 1:
                await ctx.send(f'That spot is already taken\n')
                return
            ttt_board[spot - 1] = edit_tuple(ttt_board[spot - 1], 1, 1)
        else:
            if str(ctx.author.name) == str(player2):
                await ctx.send('It is not your turn')
                return
            if check_not_taken(ttt_board, spot) == 1:
                await ctx.send(f'That spot is already taken\n')
                return
            ttt_board[spot - 1] = edit_tuple(ttt_board[spot - 1], 1, 0)
        ttt_board[spot - 1] = edit_tuple(ttt_board[spot - 1], 0, 1)
        ttt_board = tuple(ttt_board)
        round_counter += 1
    else:
        reset_game()
        await ctx.send('Game file corrupt')
        return
    write_to_ttt_file(ttt_data[1], ttt_data[2], ttt_board, player1, player2, str(round_counter), ttt_data[3])
    analysis = analyze_ttt_board(ttt_board)
    result = analysis[2]
    if analysis[1]:
        if type(result) == int:
            winner = player1 if result == 0 else player2
            await ctx.send(f'Winner is {winner}')
        elif type(result) == str and result == 'Tie':
            await ctx.send('Tie')
    await ctx.send(analysis[0])
    ttt_data[3].close()


def check_not_taken(board, loc):

    return board[loc-1][0] == 1


def edit_tuple(tup, i, val):
    return tup[:i] + (val,) + tup[i+1:]


def reset_game():
    with open('ttt_board.txt', 'w') as ttt_board_file:
        with open('ttt_reset.txt', 'r') as ttt_reset_file:
            ttt_board_file.writelines(ttt_reset_file.readlines())


def print_board(board):
    symbols = [":white_large_square: ", ":regional_indicator_x: ", ":o2: "]
    board_str = ''
    for i in range(9):
        board_str += symbols[board[i][1]+1]
        if i == 2 or i == 5:
            board_str += '\n'
    return board_str



def get_equal(x: int, y: int, z: int):
    return x == y and x == z and y == z


def get_sum(x: int, y: int, z: int):
    return x + y + z


def analyze_ttt_board(board):
    winning_combinations = [[(0, 0), (1, 0), (2, 0)], [(3, 0), (4, 0), (5, 0)], [(6, 0), (7, 0), (8, 0)], [(0, 0), (3, 0), (6, 0)], [(1, 0), (4, 0), (7, 0)], [(2, 0), (5, 0), (8, 0)], [(0, 0), (4, 0), (8, 0)], [(2, 0), (4, 0), (6, 0)],]
    for combination in winning_combinations:
        won = True
        winner = None
        for index in combination:
            square = board[index[0]]
            if square[0] != 1 or square[1] != combination[0][1]:
                won = False
                break
            winner = int(square[1])
        if won:
            break
    if not won:
        if board[0][1] == board[4][1] and board[0][0] == 1 and board[4][0] == 1 and board[8][0] == 1:
            won = True
            winner = 'Tie'
        if board[2][1] == board[4][1] and board[2][0] == 1 and board[4][0] == 1 and board[6][0] == 1:
            won = True
            winner = 'Tie'
    if won:
        reset_game()

    return print_board(board), won, winner


@client.command(name='help_page')
async def help(ctx, *page_num):
    help_list = ['Welcome to help\nType help followed by page number to change pages\n\nCreated by Tyler Besnoff',
                 'Intellabot commands\n    ! is used in front of a command name to call a command\n\n    get_times "First" "Last"\n        Returns list of times for the given name\n        If there are multiple names matching the name entered the !swim_location command will need to be used\n\n    swim_location "First" "Last" "Location"\n        Returns list of times for the given name and location']
    page = int(page_num[0]) if len(page_num) > 0 else 0
    await ctx.send(help_list[page])


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


global said_hello_to_ano
said_hello_to_ano = False

def set_said_hello_to_ano(val):
    global said_hello_to_ano
    said_hello_to_ano = val

@client.event
async def on_message(message):
    channel = message.channel
    if message.author == client.user:
        return
    if str(message.author.name) == 'Ano Bot' and globals().get('said_hello_to_ano') == False:
        await channel.send('Hello Ano')
        set_said_hello_to_ano(True)
    await client.process_commands(message)
    user_message = str(message.content)
    if user_message == "Hello" and str(channel) == "bot-testing":
        await channel.send("Hello World")


client.run(TOKEN)
