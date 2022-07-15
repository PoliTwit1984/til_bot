import glob
import os
import random
import textwrap
from string import ascii_letters
import datetime

import praw
import tweepy
from PIL import Image, ImageDraw, ImageFont

import config

client = tweepy.Client(config.bearer_token, config.consumer_key,
                       config.consumer_secret, config.access_token,
                       config.access_token_secret)

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)

auth.set_access_token(config.access_token, config.access_token_secret)

api = tweepy.API(auth)


class LPTFetcher:

    def __init__(self, sub="lifeprotips", time_span="week", limit=10):
        self.time_span = time_span
        self.limit = limit
        self.sub = sub
        self.reddit_key = "4PuhlbITTvHWOVdwcD3cyw"
        self.reddit_secret = "zGtU9KorcWW0nfPJt7CARxqWp8mWNA"
        self.user_agent = "politwit"
        self.reddit = praw.Reddit(client_id=self.reddit_key,
                                  client_secret=self.reddit_secret,
                                  user_agent=self.user_agent)

    def get_lpts(self):

        x = 1
        for submission in self.reddit.subreddit(self.sub).top(time_filter=self.time_span, limit=self.limit):
            text = submission.title

            author = submission.author

            # Open image
            img = Image.open(fp='background4.jpg', mode='r')

            # Load custom font
            font = ImageFont.truetype(font='AllerDisplay.ttf', size=52)

            # Create DrawText object
            draw = ImageDraw.Draw(im=img)

            # Calculate the average length of a single character of our font.
            # Note: this takes into account the specific font and font size.
            avg_char_width = sum(font.getsize(
                char)[0] for char in ascii_letters) / len(ascii_letters)

            # Translate this average length into a character count
            max_char_count = int(img.size[0] * .618 / avg_char_width)

            # Create a wrapped text object using scaled character count
            text = textwrap.fill(text=f"{text}", width=max_char_count)

            # Add text to the image
            draw.text(xy=(img.size[0]/2, img.size[1] / 2),
                      text=text, font=font, fill='white', anchor='mm')

            # save the image
            filename = f"{x}.jpg"
            img.save(filename)
            x = x + 1

        return

    def tweet_lpt_image(self, tweet_text="Life Pro Tip of the Day.", del_file=True):

        file_list = []
        for file in glob.glob("*.jpg"):
            file_list.append(file)

        # ! Check to make sure there are still files left to tweet
        if len(file_list) > 0:

            random_image = random.choice(file_list)
            print(random_image)

            media = api.media_upload(random_image)
            tweet_info = api.update_status(
                status=tweet_text, media_ids=[media.media_id])
            date_posted = datetime.datetime.now()
            lpt_tweet_file = open("lpt_tweet_file.txt", "a")
            lpt_tweet_file.write(f"{date_posted}, {tweet_info.id}\n")
            lpt_tweet_file.close()

            if del_file:

                os.remove(random_image)

            tweeted = True

        else:
            print("No more images to tweet. Please add more images.")
            tweeted = False

        return tweeted


r = LPTFetcher(sub="todayilearned", time_span="all", limit=365)
# r.get_lpts()

r.tweet_lpt_image(
    tweet_text="Today I learned the following... #til #todayilearned", del_file=True)
