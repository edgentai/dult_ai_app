from bs4 import BeautifulSoup
import re
import string
import time
import pandas as pd
from ftfy import fix_text
from playwright.sync_api import sync_playwright
from src.grievance_handler.constants import (
    twitter_scrapper_scroller,
    twitter_email_id,
    twitter_login_id,
    twitter_password,
)


def clean_tweets(tweets):
    tweets = re.sub(r"http\S+", "", tweets)
    cleaned_tweets = " ".join(re.sub("(@[\w_]+)|([\W_])", " ", tweets).split())
    cleaned_tweets = fix_text(cleaned_tweets)
    cleaned_tweets = cleaned_tweets.encode("ascii", errors="ignore").decode()
    return cleaned_tweets


def parse_tweets(t):
    all_tweets = list()
    try:
        text = t.find("div", attrs={"data-testid": "tweetText"}).getText()
        userinfo = t.find("div", attrs={"data-testid": "User-Name"})
        try:
            user_id = t.getText().split("·")[0]
        except:
            user_id = None
            # print(userinfo)
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
        pass
    return all_tweets


def get_tweets():
    list_tweets = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # go to url and login
        page.goto("https://twitter.com/i/flow/login")
        # get HTML
        page.wait_for_timeout(6_000)
        page.fill('input[name="text"]', twitter_email_id)
        page.locator('"Next"').click()
        try:
            page.fill('input[name="text"]', twitter_login_id)
            page.locator('"Next"').click()
        except:
            pass
        page.fill('input[name="password"]', twitter_password)
        page.locator('"Log in"').click()

        page.wait_for_timeout(2_000)
        page.goto("https://twitter.com/search?q=bmtc&f=live")

        page.wait_for_selector("//article[@data-testid='tweet']")
        tweets = []
        tweet_index = 0

        for i in range(twitter_scrapper_scroller):
            page.mouse.wheel(0, 15000)
            page.wait_for_timeout(1000)
            new_tweets = page.query_selector_all("//article[@data-testid='tweet']")
            for tweet in new_tweets:
                html = tweet.inner_html()
                soup = BeautifulSoup(html)
                new_tweets = parse_tweets(soup)
                new_tweets = [dict(t) for t in {tuple(d.items()) for d in new_tweets}]
                list_tweets.extend(new_tweets)
                list_tweets = [dict(t) for t in {tuple(d.items()) for d in list_tweets}]
            page.mouse.wheel(0, 15000)
        page.wait_for_timeout(20_000)
    return list_tweets
