from bs4 import BeautifulSoup
import re
import string
import time
import pandas as pd
from ftfy import fix_text
from playwright.sync_api import sync_playwright
from src.constants import twitter_scrapper_scroller


def clean_tweets(tweets):
    tweets = re.sub(r"http\S+", "", tweets)
    cleaned_tweets = " ".join(re.sub("(@[\w_]+)|([\W_])", " ", tweets).split())
    cleaned_tweets = fix_text(cleaned_tweets)
    cleaned_tweets = cleaned_tweets.encode("ascii", errors="ignore").decode()
    return cleaned_tweets


def parse_tweets(soup):
    all_tweets = list()
    for t in soup.find_all("article", attrs={"data-testid": "tweet"}):
        try:
            text = t.find("div", attrs={"data-testid": "tweetText"}).getText()
            userinfo = t.find("div", attrs={"data-testid": "User-Name"})
            try:
                user_id = t.getText().split("·")[0]
            except:
                user_id = None
                print(userinfo)
            try:
                date = userinfo.find("time")["datetime"]
            except:
                date = None
            all_tweets.append(
                {
                    "user_message": clean_tweets(text),
                    "platform_name": "twitter",
                    "user_name": user_id,
                    "datetime": date,
                }
            )
        except:
            continue
    return all_tweets


def get_tweets():
    list_tweets = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # go to url
        page.goto("https://twitter.com/search?q=bmtc&f=live")
        # get HTML
        page.wait_for_timeout(6_000)

        for _ in range(twitter_scrapper_scroller):
            soup = BeautifulSoup(page.content())
            new_tweets = parse_tweets(soup)
            new_tweets = [dict(t) for t in {tuple(d.items()) for d in new_tweets}]
            list_tweets.extend(new_tweets)
            list_tweets = [dict(t) for t in {tuple(d.items()) for d in list_tweets}]

            # adding scroll function
            page.mouse.wheel(0, 15000)
            time.sleep(3)
    return list_tweets
