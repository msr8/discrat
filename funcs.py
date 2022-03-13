from PyInquirer import prompt
from examples import custom_style_2
from discord.commands.context import ApplicationContext
import discord
from rich import print as printf
from rich.console import Console

from datetime import datetime
from io import StringIO
from typing import TypeVar
import datetime as dt
import getpass as gp
import os

T = TypeVar('T', ApplicationContext, str)




def ask(module_names):
    choices = [ {'name':i,'checked':True} for i in module_names ]

    questions = [
        {
            'name': 'lol',
            'type': 'checkbox',
            'message': 'Select the modules that the bot has access to',
            'choices': choices,
        }
    ]

    answers = prompt(questions, style=custom_style_2)
    return answers


def a(ctx: T):
    author = ctx.author if isinstance(ctx, ApplicationContext) else ctx
    return f'[grey50]({get_time()})[/] [magenta]<{author}>[/]'

def log_command(ctx: ApplicationContext):
    """
    Logs the command
    
    :param ctx: The ctx object
    :type ctx: ApplicationContext
    """
    printf(f'{a(ctx)} ', end=''); print(f'/{ctx.command}')


def get_user(system: str):
    """
    Get the user name of the current user
    
    :param system: The system obained by platform.system()
    :type system: str
    :return: The name of the user.
    """
    try:
        ret = gp.getuser()
    except:
        try:
            temp_list = os.getcwd().split(os.path.sep)
            ret = temp_list[ temp_list.index('Users') + 1 ]
        except:
            try:
                temp_list = __file__.split(os.path.sep)
                ret = temp_list[ temp_list.index('Users') + 1 ]
            except:
                ret = 'Unable to determine'
    return ret

def get_time(tim: datetime=None):
    """
    Returns the current time or given time in the format dd/mm/yy hh:mm
    
    :param tim = None
    :type tim: datetime
    :return: A string with formatted time like "{day}/{month}/{year} {hour}:{minute}"
    """
    # If time not given, gets current time
    if not tim:    tim = dt.datetime.now()
    # Gets the values
    day = tim.day
    month = tim.month
    year = str(tim.year)[-2:]
    hour = tim.hour
    minute = tim.minute
    # Formats em
    if minute < 10:    minute = f'0{minute}'
    if hour < 10:      hour = f'0{hour}'
    if day < 10:       day = f'0{day}'
    if month < 10:     month = f'0{month}'
    # Returns the formatted time
    return f'{day}/{month}/{year} {hour}:{minute}'

def get_temp(system: str, usr: str):
    """
    Returns the TEMP directory using enviornment variables, if it's None, provides another directory
    
    :param system: The system obained by platform.system()
    :type system: str
    :param usr: The username of the user
    :type usr: str
    :return: The temp directory
    """
    # Gets the TEMP directory using enviornment variables
    temp_dir = os.getenv('TEMP') if system == 'Windows' else os.getenv('TMPDIR')
    # If for some reason its None, provides another directory
    temp_dir = f'C:\\Users\\{usr}\\AppData\\Local\\Temp' if system=='Windows' else '/tmp'
    # Returns it
    return temp_dir


async def handle_error(ctx: ApplicationContext, e, console: Console):
    """
    It logs the error, and then tries to tell the user that there's been an error
    
    :param ctx: Context of command
    :type ctx: discord.ApplicationContext
    :param e: The exception that was raised
    :param console: The console object, which is used to print to log the error
    :type console: rich.Console
    """
    # Prints exception
    print('\n')
    console.print_exception()
    print('\n')
    # Tries to tell the user that theres been an error
    try:
        fp = StringIO(str(e))
        file = discord.File(fp, filename='error.txt')
        await ctx.respond(f'Error :/', file=file)
        printf(f'{a(ctx)} [red1]Told the error[/]')
    except Exception as e:
        printf(f'{a(ctx)} [red1]Couldn\'t tell the error ({e})[/]')


async def is_module_allowed(ctx:ApplicationContext, ALLOWED_MODULES:list, module:str):
    if module in ALLOWED_MODULES:    return True
    await ctx.respond('Fuck off')
    printf(f'{a(ctx)} [red3][i]Told them to fuck off[/][/]')
    return False
