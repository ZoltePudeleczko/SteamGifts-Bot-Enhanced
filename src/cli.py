import configparser

from pyfiglet import figlet_format
from PyInquirer import (
    Token,
    ValidationError,
    Validator,
    prompt,
    style_from_dict,
)
from termcolor import colored


config = configparser.ConfigParser()
config.read("config.ini")

style = style_from_dict(
    {
        Token.QuestionMark: "#fac731 bold",
        Token.Answer: "#4688f1 bold",
        Token.Selected: "#0abf5b",  # default
        Token.Pointer: "#673ab7 bold",
    }
)


def log(string, color, font="slant", figlet=False):
    if not figlet:
        print(colored(string, color))
    else:
        print(colored(figlet_format(string, font=font), color))


class PointValidator(Validator):
    def validate(self, document):
        value = document.text
        try:
            value = int(value)
        except Exception:
            raise ValidationError(
                message="Value should be greater than 0",
                cursor_position=len(document.text),
            )

        if value <= 0:
            raise ValidationError(
                message="Value should be greater than 0",
                cursor_position=len(document.text),
            )
        return True


def ask(type, name, message, validate=None, choices=[]):
    questions = [
        {
            "type": type,
            "name": name,
            "message": message,
            "validate": validate,
        },
    ]
    if choices:
        questions[0].update(
            {
                "choices": choices,
            }
        )
    answers = prompt(questions, style=style)
    return answers


def link(uri, label=None):
    if label is None:
        label = uri
    parameters = ""
    escape_mask = "\033]8;{};{}\033\\{}\033]8;;\033\\"

    return escape_mask.format(parameters, uri, label)


def write_welcome_message():
    log("SteamGifts Bot+", color="blue", figlet=True)
    log(
        "Welcome to "
        + link(
            "https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced",
            "SteamGifts Bot + Enhanced",
        )
        + "!",
        "green",
    )
    log(
        "Check for updates at "
        + link(
            "https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/releases",
            "github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/releases\n",
        ),
        "green",
    )
    log("Created by: github.com/stilManiac", "white")
    log(
        "Enhanced by: "
        + link("https://github.com/ZoltePudeleczko", "github.com/ZoltePudeleczko\n"),
        "white",
    )


def save_config():
    with open("config.ini", "w") as configfile:
        config.write(configfile)
        print("⚙️ Configuration saved.")


def run():
    from main import SteamGifts as SG

    def askCookie():
        cookie = ask(
            type="input",
            name="cookie",
            message="Enter PHPSESSID cookie:",
        )
        config["DEFAULT"]["cookie"] = cookie["cookie"]
        save_config()
        return cookie["cookie"]

    def askConfig():
        pinned_games = ask(
            type="confirm", name="pinned", message="Should bot enter pinned games?"
        )["pinned"]
        config["DEFAULT"]["pinned_games"] = "1" if pinned_games else "0"

        gift_type = ask(
            type="list",
            name="gift_type",
            message="Select type:",
            choices=["All", "Wishlist", "Recommended", "Copies", "DLC", "Group", "New"],
        )["gift_type"]
        config["DEFAULT"]["gift_type"] = gift_type

        min_points = ask(
            type="input",
            name="min_points",
            message="Minimum points to start working (bot will try to enter giveaways until minimum value is reached):",
            validate=PointValidator,
        )["min_points"]
        config["DEFAULT"]["min_points"] = min_points

        save_config()
        return pinned_games, gift_type, min_points

    def pinned_games_to_string(pinned_games):
        return "Enter" if pinned_games == "1" else "Ignore"

    write_welcome_message()

    if not config["DEFAULT"].get("cookie"):
        cookie = askCookie()
    else:
        current_cookie = config["DEFAULT"].get("cookie")
        re_enter_cookie = ask(
            type="confirm",
            name="reenter",
            message=f"Current cookie: {current_cookie}\nDo you want to enter new cookie?",
        )["reenter"]
        if re_enter_cookie:
            cookie = askCookie()
        else:
            cookie = current_cookie

    if not config["DEFAULT"].get("pinned_games"):
        pinned_games, gift_type, min_points = askConfig()
    else:
        pinned_games = config["DEFAULT"].get("pinned_games")
        gift_type = config["DEFAULT"].get("gift_type")
        min_points = config["DEFAULT"].get("min_points")

        re_enter_config = ask(
            type="confirm",
            name="reenter",
            message=f"Current configuration:\nPinned games: {pinned_games_to_string(pinned_games)}\nGift type: {gift_type}\nMinimum points: {min_points}\n\nDo you want to change this configuration?",
        )["reenter"]
        if re_enter_config:
            pinned_games, gift_type, min_points = askConfig()

    print()
    s = SG(cookie, gift_type, pinned_games, min_points)
    s.start()


if __name__ == "__main__":
    run()
