from requests_oauthlib import OAuth1Session
import os
import json

consumer_key = "XJfK8j5lEKNRp9z5BBhRc0ECl"
consumer_secret = "82tmGFHB5wmGARP6VD94v6RCL08I2e6Yxpqone0efUMi4j2htP"

access_token = "1670291667142815747-lIJWCPg6k5ntGWSuVtIjQIb5G4KHsp"
access_token_secret = "W9t1PjPjD6PK40Ij6pa7pbrWwO5Yq27JiMTRQ2WIjOPwC"

def tweet_reply(tweet_id, message):
  
  payload = {"text": message, "reply": {"in_reply_to_tweet_id": tweet_id}}

  # Make the request
  oauth = OAuth1Session(
      consumer_key,
      client_secret=consumer_secret,
      resource_owner_key=access_token,
      resource_owner_secret=access_token_secret,
  )
  
  # Making the request
  response = oauth.post(
      "https://api.twitter.com/2/tweets",
      json=payload,
  )
  
  if response.status_code != 201:
      raise Exception(
          "Request returned an error: {} {}".format(response.status_code, response.text)
      )
  
  print("Response code: {}".format(response.status_code))
  
  
