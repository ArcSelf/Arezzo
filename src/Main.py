# MY_CONSTANT
# my_function
# myValue
# MyClass

# __privateFunction
# _overridableFunction
import Utils
import Graphing
import AudioProcessor

import curses


AUDIO_TO_ANALYSE = r"PWS_TEST_2.wav"


AUDIO_BASE_PATH = "audio"

def test(screen):


    # Initialize color in a separate step
    curses.start_color()

    # Change style: bold, highlighted, and underlined text
    screen.addstr("Regular text\n")
    screen.addstr("Bold\n", curses.A_BOLD)
    screen.addstr("Highlighted\n", curses.A_STANDOUT)
    screen.addstr("Underline\n", curses.A_UNDERLINE)
    screen.addstr("Regular text again\n")

    # Create a custom color set that you might re-use frequently
    # Assign it a number (1-255), a foreground, and background color.
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    screen.addstr("RED ALERT!\n", curses.color_pair(1))

    # Combine multiple attributes with bitwise OR
    screen.addstr("SUPER RED ALERT!\n", curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE | curses.A_BLINK)

    screen.refresh()
    curses.napms(10000)






def start():

    #curses.wrapper(test)

   # return

    Graphing.create_plot(rows=4)

    AudioProcessor.process_audio("{}\\{}...".format(AUDIO_BASE_PATH,AUDIO_TO_ANALYSE))
    Graphing.save_plot()

    Graphing.show_plot()


if __name__ == "__main__":
    start()

