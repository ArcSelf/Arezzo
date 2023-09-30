import cui.Spinner as Spinner


import threading
import os


## https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
YELLOW = "\x1b[0;33m"
WHITE = "\x1b[0;37m"
RED = "\x1b[0;31m"
BLUE = "\x1b[0;34m"
PURPLE = "\x1b[0;35m"
CYAN = "\x1b[0;36m"
GREEN = "\x1b[0;32m"

BOLD_RED = "\x1b[1;31m"



HIDE_CONSOLE_CURSOR = "\033[?25l"


spinner = None


def setY(y):
    print("\033[{};{}H".format(y,1))


def init():
    ## https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    ## Required for colours
    os.system("")



    # Hide console cursor
    print(HIDE_CONSOLE_CURSOR, end="")


def stop_spinner():
    global spinner
    if not spinner is None:
        spinner.stop()
        spinner = None



def set_colour(colour):
    print(colour,end="")



def warning(value):
    print_colour(f"{str(value)}\n",RED)



def debug(value,*,end="\n",debugControl=True):
    if debugControl:
        print(value,end)

def print_colour(text,colour,*,end="",debugControl=True):
    #stop_spinner()
    if debugControl:
        print(f"{colour}{text}{WHITE}",end=end)



def diagnostic(name,value,suffix=""):
    print_colour("{}: {} {}                                                     \n".format(name,str(value),suffix),YELLOW)



def newline(*,debugControl=True):
    if debugControl:
        print()




def progress(value,prefixNewline=True):
    global spinner
    if prefixNewline:
        print()
    set_colour(GREEN)
    spinner = Spinner.Spinner(value)