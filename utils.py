class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ORANGE = '\033[38;5;208m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def format_time(seconds):
    minutes = seconds // 60
    seconds %= 60

    if minutes > 0:
        return f"{int(minutes)} m {int(seconds)} s"
    else:
        return f"{int(seconds)} s"


def printWithColor(text, color_start: Color, color_end: Color = Color.END):
    print(color_start + text + color_end)
