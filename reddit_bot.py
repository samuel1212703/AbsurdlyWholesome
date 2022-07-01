from logging import exception
from tracemalloc import stop
import praw
import time
import os
from munk import *
import random


username = os.getenv('BOT_NAME')
password = os.getenv('PASSWORD')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# art subreddits doesnt work, as the both claims credit for all the works (:D)
list_of_subreddits = ["bestoflegaladvice", "discussion", "dankmemes", "memes",
                      "oldschoolcool", "interestingasfuck", "mildlyinteresting", "facepalm"]


def bot_login():
    r = praw.Reddit(username=username, password=password, client_id=client_id,
                    client_secret=client_secret, user_agent="Absurdly Wholesome v0.1")
    print("Log in successful")
    return r


def document_karma():
    bot_account = r.redditor(str(username))

    from datetime import date
    today = date.today()

    data = [today, bot_account.link_karma, bot_account.comment_karma]

    import csv
    with open('karma.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def run_bot(r, comments_replied_to):
    document_karma()

    current_subreddit = list_of_subreddits[random.randint(
        1, len(list_of_subreddits)-1)]
    print("Subreddit: " + current_subreddit)
    for comment in r.subreddit(current_subreddit).comments(limit=50):
        print(comment.body)
        if len(comment.body) > 50 and comment.id not in comments_replied_to and comment.author != r.user.me() and comment.is_submitter == False:
            comment_reply = str(generate_comment(comment.body))
            comment.reply(comment_reply)
            comments_replied_to.append(comment.id)
            with open("comments_replied_to.txt", "a") as f:
                f.write(comment.id + "\n")
            with open("reply_history.txt", "a") as f:
                user_text = comment.body.encode('utf-8')
                f.write("######\n" + str(user_text) +
                        "\n" + comment_reply + "\n\n")


def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
        with open("comments_replied_to.txt", "r") as f:
            comments_replied_to = list(filter(None, f.read().split("\n")))
    return comments_replied_to


if __name__ == '__main__':
    r = bot_login()
    comments_replied_to = get_saved_comments()

    while True:
        try:
            run_bot(r, comments_replied_to)
        except praw.exceptions.RedditAPIException:
            print("Reddit api break")

        time.sleep(random.randint(100, 421))
