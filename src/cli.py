import configparser
import questionary

from pyfiglet import figlet_format
from termcolor import colored

config = configparser.ConfigParser()
config.read("config.ini")


def log(string, color, font="slant", figlet=False):
    if not figlet:
        print(colored(string, color))
    else:
        print(colored(figlet_format(string, font=font), color))


class PointValidator:
    def validate(self, document):
        value = document.text
        try:
            value = int(value)
        except Exception:
            raise ValueError("Value must be greater than 0")

        if value <= 0:
            raise ValueError("Value must be greater than 0")
        return True


def ask(type, name, message, validate=None, choices=None, default=None):
    if type == "input":
        answer = questionary.text(message, default=default or "").ask()
        return {name: answer}
    elif type == "confirm":
        answer = questionary.confirm(
            message, default=(default if default is not None else True)
        ).ask()
        return {name: answer}
    elif type == "list":
        answer = questionary.select(message, choices=choices, default=default).ask()
        return {name: answer}
    else:
        raise ValueError(f"Unsupported question type: {type}")


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
        log("⚙️ Configuration saved.", "green")


def run():
    from main import SteamGifts as SG

    def askCookie(default=None):
        cookie = ask(
            type="input",
            name="cookie",
            message=f"Enter PHPSESSID cookie:",
            default=default,
        )
        value = cookie["cookie"] if cookie["cookie"] else default
        config["DEFAULT"]["cookie"] = value
        return value

    def askConfig(default_pinned=None, default_gift_type=None, default_min_points=None):
        pinned_games = ask(
            type="confirm",
            name="pinned",
            message=f"Should bot enter pinned games?",
            default=(default_pinned == "1"),
        )["pinned"]
        config["DEFAULT"]["pinned_games"] = "1" if pinned_games else "0"

        gift_type = ask(
            type="list",
            name="gift_type",
            message=f"Select type:",
            choices=[
                "Special Mode",
                "All",
                "Wishlist",
                "Recommended",
                "Copies",
                "DLC",
                "Group",
                "New",
            ],
            default=default_gift_type,
        )["gift_type"]
        config["DEFAULT"]["gift_type"] = gift_type

        min_points = ask(
            type="input",
            name="min_points",
            message=f"Minimum points to start working:",
            default=default_min_points,
        )["min_points"]
        min_points = min_points if min_points else default_min_points
        config["DEFAULT"]["min_points"] = min_points
        return pinned_games, gift_type, min_points

    def askIgnoredWords(default=None):
        ignored_words = ask(
            type="input",
            name="ignored_words",
            message=f"Enter words you want to ignore (comma separated):",
            default=default,
        )["ignored_words"]
        value = ignored_words if ignored_words else default
        config["DEFAULT"]["ignored_words"] = value
        return value.split(",")

    def pinned_games_to_string(pinned_games):
        return "Enter" if pinned_games == "1" else "Ignore"

    write_welcome_message()

    if not config["DEFAULT"].get("cookie"):
        cookie = askCookie()
        save_config()

    if not config["DEFAULT"].get("pinned_games"):
        pinned_games, gift_type, min_points = askConfig()
        save_config()

    if not config["DEFAULT"].get("ignored_words"):
        ignored_words = askIgnoredWords()
        save_config()

    cookie = config["DEFAULT"].get("cookie")
    pinned_games = config["DEFAULT"].get("pinned_games")
    gift_type = config["DEFAULT"].get("gift_type")
    min_points = config["DEFAULT"].get("min_points")
    ignored_words = config["DEFAULT"].get("ignored_words").split(",")

    re_enter_config = ask(
        type="confirm",
        name="reenter",
        message=f"Current configuration:\nCookie: {cookie}\nPinned games: {pinned_games_to_string(pinned_games)}\nGift type: {gift_type}\nMinimum points: {min_points}\nIgnored words: {ignored_words}\n\nDo you want to change this configuration?",
    )["reenter"]
    if re_enter_config:
        cookie = askCookie(default=cookie)
        pinned_games, gift_type, min_points = askConfig(
            default_pinned=pinned_games,
            default_gift_type=gift_type,
            default_min_points=min_points,
        )
        ignored_words = askIgnoredWords(default=",".join(ignored_words))
        save_config()

    log("Bot is starting...", "blue")
    s = SG(cookie, gift_type, pinned_games, min_points, ignored_words)
    s.start()


if __name__ == "__main__":
    run()
