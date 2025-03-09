import requests
import json

from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from time import sleep
from bs4 import BeautifulSoup

from cli import log

SLEEP_TIME = 5
SLEEP_TIME_NO_GAMES = 120
SLEEP_TIME_NO_POINTS = 900

FILTER_URLS = {
    "Special Mode": "search?page={}&point_max={}",
    "All": "search?page={}&point_max={}",
    "Wishlist": "search?page={}&type=wishlist&point_max={}",
    "Recommended": "search?page={}&type=recommended&point_max={}",
    "Copies": "search?page={}&copy_min=2&point_max={}",
    "DLC": "search?page={}&dlc=true&point_max={}",
    "Group": "search?page={}&type=group&point_max={}",
    "New": "search?page={}&type=new&point_max={}",
}

SPECIAL_MODE_URLS = {
    "Free": "search?page={}&point_max=0&{}",
    "Metascore90": "search?page={}&point_max={}&metascore_min=90",
    "Metascore80": "search?page={}&point_max={}&metascore_min=80",
    "Metascore70": "search?page={}&point_max={}&metascore_min=70",
}


class SteamGifts:
    def __init__(self, cookie, gift_type, pinned, min_points, ignored_words):
        self.cookie = {"PHPSESSID": cookie}
        self.gift_type = gift_type
        self.pinned = pinned
        self.min_points = int(min_points)
        self.ignored_words = ignored_words
        self.special_mode_stage = 0

        self.base = "https://www.steamgifts.com"
        self.session = requests.Session()

        self.filter_url = FILTER_URLS[self.gift_type]

    def requests_retry_session(self, retries=5, backoff_factor=0.3):
        session = self.session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 502, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_soup_from_page(self, url):
        r = self.requests_retry_session().get(url)
        r = requests.get(url, cookies=self.cookie)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def update_info(self):
        soup = self.get_soup_from_page(self.base)

        try:
            self.xsrf_token = soup.find("input", {"name": "xsrf_token"})["value"]
            self.points = int(
                soup.find("span", {"class": "nav__points"}).text
            )  # storage points
        except TypeError:
            log("⛔ Cookie is not valid.", "red")
            sleep(SLEEP_TIME)
            exit()

    def get_game_info(self, item):
        game_cost = int(
            item.find_all("span", {"class": "giveaway__heading__thin"})[-1]
            .getText()
            .replace("(", "")
            .replace(")", "")
            .replace("P", "")
        )
        game_name = item.find("a", {"class": "giveaway__heading__name"}).text
        game_id = item.find("a", {"class": "giveaway__heading__name"})["href"].split(
            "/"
        )[2]

        return game_cost, game_name, game_id

    def sleep_if_not_enough_points(self):
        if self.points < self.min_points:
            log(
                f"🛋️ Sleeping to get more points. We have {self.points} points, but we need {self.min_points} to start.",
                "yellow",
            )
            sleep(SLEEP_TIME_NO_POINTS)
            self.start()

    def get_games_list(self, page):
        paginated_url = (
            f"{self.base}/giveaways/{self.filter_url.format(page, self.points)}"
        )
        soup = self.get_soup_from_page(paginated_url)

        return [
            item
            for item in soup.find_all("div", {"class": "giveaway__row-inner-wrap"})
            if "is-faded" not in item.get("class", [])
            and (len(item.get("class", [])) != 2 or self.pinned != 0)
            and all(
                word.lower()
                not in item.find("a", {"class": "giveaway__heading__name"}).text.lower()
                for word in self.ignored_words
                if word != ""
            )
        ]

    def get_game_content(self, page=1):
        n = page
        while True:
            log(f"⚙️ Retrieving games from page {n}...", "magenta")
            games_list = self.get_games_list(page)

            if not len(games_list):
                break
            else:
                log(f"🎁 Found {len(games_list)} games on page {n}.", "green")

            for item in games_list:
                self.sleep_if_not_enough_points()

                game_cost, game_name, game_id = self.get_game_info(item)

                if self.points - game_cost < 0:
                    log(
                        f"⛔ Not enough points to enter: {game_name} ({game_cost} points needed), ignoring",
                        "red",
                    )
                    continue

                if self.entry_gift(game_id):
                    self.points -= game_cost
                    log(
                        f"🎉 One more game! Has just entered {game_name} for {game_cost} points. Points left: {self.points}",
                        "green",
                    )
                    sleep(SLEEP_TIME)
                else:
                    log(f"⛔ Failed to enter {game_name}", "red")
                    sleep(SLEEP_TIME)

            n = n + 1

        if len(self.get_games_list(1)) > 0:
            self.get_game_content()
        elif self.gift_type == "Special Mode":
            log(
                "🌸 [Special Mode] No more games to enter. Changing special mode stage...",
                "yellow",
            )
            self.set_next_special_mode_stage()
        else:
            log("🛋️ No more games to enter. Sleeping for a while...", "yellow")
            sleep(SLEEP_TIME_NO_GAMES)

        self.start()

    def entry_gift(self, game_id):
        payload = {"xsrf_token": self.xsrf_token, "do": "entry_insert", "code": game_id}
        entry = requests.post(
            "https://www.steamgifts.com/ajax.php", data=payload, cookies=self.cookie
        )
        return json.loads(entry.text)["type"] == "success"

    def set_next_special_mode_stage(self):
        if self.special_mode_stage == 0:
            log(f"🌸 [Special Mode] Checking for free games...", "green")
            self.filter_url = SPECIAL_MODE_URLS["Free"]
        elif self.special_mode_stage == 1:
            log(f"🌸 [Special Mode] Checking for wishlist games...", "green")
            self.filter_url = FILTER_URLS["Wishlist"]
        elif self.special_mode_stage == 2:
            log(f"🌸 [Special Mode] Checking for recommended games...", "green")
            self.filter_url = FILTER_URLS["Recommended"]
        elif self.special_mode_stage == 3:
            log(f"🌸 [Special Mode] Checking for games from groups...", "green")
            self.filter_url = FILTER_URLS["Group"]
        elif self.special_mode_stage == 4:
            log(f"🌸 [Special Mode] Checking for Metascore 90+ games...", "green")
            self.filter_url = SPECIAL_MODE_URLS["Metascore90"]
        elif self.special_mode_stage == 5:
            log(f"🌸 [Special Mode] Checking for Metascore 80+ games...", "green")
            self.filter_url = SPECIAL_MODE_URLS["Metascore80"]
        elif self.special_mode_stage == 6:
            log(f"🌸 [Special Mode] Checking for Metascore 70+ games...", "green")
            self.filter_url = SPECIAL_MODE_URLS["Metascore70"]
        elif self.special_mode_stage == 7:
            log(f"🌸 [Special Mode] Checking for new games...", "green")
            self.filter_url = FILTER_URLS["All"]
        else:
            self.start()

        self.special_mode_stage += 1
        self.get_game_content()

    def start(self):
        self.update_info()
        self.sleep_if_not_enough_points()
        self.special_mode_stage = 0

        log(f"🤖 Hoho! I am back! You have {self.points} points. Lets hack.", "blue")

        if self.gift_type == "Special Mode":
            self.set_next_special_mode_stage()
        else:
            self.get_game_content()
