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


class SteamGifts:
    def __init__(self, cookie, gifts_type, pinned, min_points):
        self.cookie = {"PHPSESSID": cookie}
        self.gifts_type = gifts_type
        self.pinned = pinned
        self.min_points = int(min_points)

        self.base = "https://www.steamgifts.com"
        self.session = requests.Session()

        self.filter_url = {
            "All": "search?page=%d",
            "Wishlist": "search?page=%d&type=wishlist",
            "Recommended": "search?page=%d&type=recommended",
            "Copies": "search?page=%d&copy_min=2",
            "DLC": "search?page=%d&dlc=true",
            "Group": "search?page=%d&type=group",
            "New": "search?page=%d&type=new",
        }

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
        if self.points == 0 or self.points < self.min_points:
            log(
                f"🛋️ Sleeping to get more points. We have {self.points} points, but we need {self.min_points} to start.",
                "yellow",
            )
            sleep(SLEEP_TIME_NO_POINTS)
            self.start()

    def get_game_content(self, page=1):
        n = page
        while True:
            log(f"⚙️ Retrieving games from page {n}...", "magenta")

            filtered_url = self.filter_url[self.gifts_type] % n
            paginated_url = f"{self.base}/giveaways/{filtered_url}"

            soup = self.get_soup_from_page(paginated_url)

            game_list = [
                item
                for item in soup.find_all("div", {"class": "giveaway__row-inner-wrap"})
                if len(item.get("class", [])) != 2 or self.pinned
            ]
            if not len(game_list):
                break
            else:
                log(f"🎁 Found {len(game_list)} games on page {n}.", "green")

            for item in game_list:
                self.sleep_if_not_enough_points()

                game_cost, game_name, game_id = self.get_game_info(item)

                if self.points - game_cost < 0:
                    log(
                        f"⛔ Not enough points to enter: {game_name} ({game_cost} points needed)",
                        "red",
                    )
                    continue
                else:
                    if self.entry_gift(game_id):
                        self.points -= game_cost
                        log(
                            f"🎉 One more game! Has just entered {game_name} for {game_cost} points. Points left: {self.points}",
                            "green",
                        )
                        sleep(SLEEP_TIME)
                    else:
                        log(f"⛔ Failed to enter {game_name}.", "red")
                        sleep(SLEEP_TIME)

            n = n + 1

        log("🛋️ No more games found. Waiting 2 mins to update...", "yellow")
        sleep(SLEEP_TIME_NO_GAMES)
        self.start()

    def entry_gift(self, game_id):
        payload = {"xsrf_token": self.xsrf_token, "do": "entry_insert", "code": game_id}
        entry = requests.post(
            "https://www.steamgifts.com/ajax.php", data=payload, cookies=self.cookie
        )
        return json.loads(entry.text)["type"] == "success"

    def start(self):
        self.update_info()
        self.sleep_if_not_enough_points()

        log(f"🤖 Hoho! I am back! You have {self.points} points. Lets hack.", "blue")

        self.get_game_content()
