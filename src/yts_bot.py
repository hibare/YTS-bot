#!/usr/bin/env python3

import sys
import json
import logging
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime, timezone
from typing import Dict
import requests
from bs4 import BeautifulSoup
from decouple import config
from apscheduler.schedulers.blocking import BlockingScheduler

# Configure and create a logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def send_notification(text: str) -> int:
    """Send slack notifications"""

    logger.info("Sending slack notification")
    slack_endpoint = config('SLACK_ENDPOINT')
    headers = {
        'Content-type': 'application/json',
    }
    data = dict(
        text=text,
    )
    data = json.dumps(data)
    response = requests.post(slack_endpoint, headers=headers, data=data)
    return response.status_code


def extract(url: str) -> Dict:
    """Extract top movies from link"""

    movies = dict()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
    }

    try:
        response = requests.get(url, headers=headers)

        logger.info("Received respose=%s for URL=%s",
                    response.status_code, url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            popular_downloads = soup.find(id='popular-downloads')
            second_row = popular_downloads.find_all('div', class_="row")[1]
            top_movies = second_row.find_all(
                'div', class_="browse-movie-wrap")

            for movie in top_movies:
                title = movie.find(
                    'a', class_="browse-movie-title").get_text()
                link = urljoin(
                    url,
                    movie.find('a', class_="browse-movie-title").get('href')
                )
                cover_image = urljoin(
                    url, movie.find('img').get('src')
                )

                movies[title] = {
                    "title": title,
                    "link": link,
                    "cover_image": cover_image,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        else:
            logger.error("url=%s, status=%s", url, response.status_code)
    except Exception:
        logger.exception("url=%s", url)

    logger.info("url=%s, movies=%s", url, movies.keys())
    return movies


def yts(data_dir: str = "/data", history: str = "yts_movie_list.txt") -> None:
    urls = ["https://yst.am/", "https://wvw.yts.vc/yify/", "https://yts.lt/"]

    logger.info("Starting run")

    Path(data_dir).mkdir(parents=True, exist_ok=True)
    history_path = Path(data_dir) / history

    movies = dict()
    history = dict()

    for url in urls:
        movies.update(extract(url))

    # Fetch history
    try:
        with open(history_path) as f:
            history = json.loads(f.read())
    except Exception:
        pass

    # Check for new movies
    new_movies = set(movies.keys()) - set(history.keys())

    logger.info("New movies %s", new_movies)

    if new_movies:
        # Send notification & update history file
        for title in new_movies:
            details = movies.get(title)
            text = """Hey found new movie on YTS\n\n*%s* `<%s|view>`\n\n%s""" % (
                title,
                details.get("link"),
                details.get("cover_image")
            )

            try:
                response_code = send_notification(text)
                logger.info("Received notification respose=%s for movie=%s",
                            response_code, title)

                if str(response_code).startswith(('2')):
                    history[title] = details
            except Exception:
                logger.exception(
                    "Failed to send notification, movie=%s", title)

        # Write new history
        with open(history_path, 'w') as f:
            f.write(json.dumps(history))


def main():

    shed = BlockingScheduler()

    interval = config("INTERVAL", 12, cast=int)
    slack_endpoint = config("SLACK_ENDPOINT", None)

    if slack_endpoint is None:
        logger.error("Slack endpoint not configured")
        sys.exit(1)

    logger.info("Adding job")
    logger.info("Interval=%s", interval)

    # shed.add_job(yts, 'interval', hours=interval)
    shed.add_job(yts, 'interval', minutes=1)

    try:
        logger.info("Starting scheduler")
        shed.start()
    except Exception:
        print("failed")


if __name__ == "__main__":
    main()
