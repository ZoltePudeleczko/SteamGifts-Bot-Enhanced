import six
import configparser

from pyfiglet import figlet_format
from PyInquirer import (
    Token,
    ValidationError,
    Validator,
    prompt,
    style_from_dict,
)
from prompt_toolkit import document
from termcolor import colored


config = configparser.ConfigParser()

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
        six.print_(colored(string, color))
    else:
        six.print_(colored(figlet_format(string, font=font), color))


class PointValidator(Validator):
    def validate(self, document: document.Document):
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


def run():
    from main import SteamGifts as SG

    def askCookie():
        cookie = ask(
            type="input",
            name="cookie",
            message="Enter PHPSESSID cookie (Only needed to provide once):",
        )
        config["DEFAULT"]["cookie"] = cookie["cookie"]

        with open("config.ini", "w") as configfile:
            config.write(configfile)
        return cookie["cookie"]

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
    log("Created by: github.com/stilManiac", "white")
    log(
        "Enhanced by: "
        + link("https://github.com/ZoltePudeleczko", "github.com/ZoltePudeleczko"),
        "white",
    )

    config.read("config.ini")
    if not config["DEFAULT"].get("cookie"):
        cookie = askCookie()
    else:
        re_enter_cookie = ask(
            type="confirm", name="reenter", message="Do you want to enter new cookie?"
        )["reenter"]
        if re_enter_cookie:
            cookie = askCookie()
        else:
            cookie = config["DEFAULT"].get("cookie")

    pinned_games = ask(
        type="confirm", name="pinned", message="Should bot enter pinned games?"
    )["pinned"]

    gift_type = ask(
        type="list",
        name="gift_type",
        message="Select type:",
        choices=["All", "Wishlist", "Recommended", "Copies", "DLC", "Group", "New"],
    )["gift_type"]

    min_points = ask(
        type="input",
        name="min_points",
        message="Enter minimum points to start working (bot will try to enter giveaways until minimum value is reached):",
        validate=PointValidator,
    )["min_points"]

    s = SG(cookie, gift_type, pinned_games, min_points)
    s.start()


if __name__ == "__main__":
    run()
