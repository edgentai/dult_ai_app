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
import requests
import os
import json

bearer_token = "AAAAAAAAAAAAAAAAAAAAAOoMoQEAAAAAcGMSViQXxZLhffTROqyAfmWNDKk%3DEQyJCdtcylJLtRqtdI1q1munZhrg8iFadeOrIa0ZAftNsBXXfE"


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
        page.wait_for_timeout(3_000)
        page.locator('"Next"').click()
        try:
            page.fill('input[name="text"]', twitter_login_id)
            page.wait_for_timeout(6_000)
            page.locator('"Next"').click()
        except:
            pass
        page.fill('input[name="password"]', twitter_password)
        page.wait_for_timeout(2_000)
        page.locator('"Log in"').click()

        page.wait_for_timeout(10_000)
        page.goto("https://twitter.com/search?q=bmtc&f=live")

        page.wait_for_selector("//article[@data-testid='tweet']")
        tweets = []
        tweet_index = 0

        for i in range(twitter_scrapper_scroller):
            page.mouse.wheel(0, 15000)
            page.wait_for_timeout(10000)
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



def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def get_tweets_api():
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    
    # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
    # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
    query_params = {'query': '#bmtc','tweet.fields': 'author_id', 'max_results':100}
    
    json_response = connect_to_endpoint(search_url, query_params)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response['data']
