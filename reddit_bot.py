from logging import exception
from tracemalloc import stop
import praw
import time
import os
from munk import *
import munk
import random

fully_dynamic = False
continous_subreddit_optimization = True
use_custom_subreddit_list = True
# Setting this to 10, means 1 in 10 chance to select a random subreddit
random_subreddit_rate = 10
max_comments_on_single_thread = 2
list_of_excluded_subreddit = ["interestingasfuck", "oldschoolcool", "art"]

if(fully_dynamic):
    continous_subreddit_optimization = True
    use_custom_subreddit_list = False
    random_subreddit_rate = 10
    max_comments_on_single_thread = 3

bot_name = "AbsurdlyWholesome"
username = os.getenv('BOT_NAME')
password = os.getenv('PASSWORD')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# Art subreddits doesnt work, as the both claims credit for all the works (:D)
# Oldschoolcool and subreddits with similar advanced and abstract topics, doesnt work well either, and often leads to angering people
list_of_subreddits = {}

with open("subreddit_rating.txt") as f:
    for line in f.readlines():
        list_of_subreddits.update(
            {line.split(":")[0]: float(line.split(":")[1].replace("\n", ""))})


def bot_login():
    r = praw.Reddit(username=username, password=password, client_id=client_id,
                    client_secret=client_secret, user_agent="Absurdly Wholesome v0.1")
    print("Log in successful")
    return r


def document_karma():
    bot_account = r.redditor(str(username))

    from datetime import datetime
    today = datetime.now()

    data = [today, bot_account.link_karma, bot_account.comment_karma]

    if bot_account.comment_karma != 0:
        import csv
        with open('karma.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(data)


def run_bot(r, comments_replied_to, current_subreddit):

    document_karma()

    for comment in r.subreddit(current_subreddit).comments(limit=random.randint(1, max_comments_on_single_thread)):
        if comment.author.is_mod == False and len(comment.body) > 80 and comment.id not in comments_replied_to and comment.author != r.user.me() and comment.is_submitter == False and "bot" not in str(comment.author):
            print("########################\n\nComment:",
                  comment.body)
            print("Generating response...")

            # Check for parent comment
            parent_comment = ""
            if(comment.parent() != None):
                parent_comment = comment.parent()
            
            # Generate response and reply
            comment_reply = str(generate_comment(
                comment.body, parent_comment.body))

            print("Response generated:" + comment_reply + "\n######")
            comment.reply(body=comment_reply)
            comments_replied_to.append(comment.id)

            # Document comment and response in a separate file
            with open("comments_replied_to.txt", "a") as f:
                f.write(comment.id + "\n")
            with open("reply_history.txt", "a") as f:
                user_text = comment.body.encode('utf-8')
                f.write("########################\n" + str(user_text) +
                        "\n" + comment_reply + "\n\n")


def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
        with open("comments_replied_to.txt", "r") as f:
            comments_replied_to = list(filter(None, f.read().split("\n")))
    return comments_replied_to


def weighted_subreddit_selection():
    # Reset values in weighted dictionary and make a copy containing amounts of comments
    for i in list_of_subreddits:
        list_of_subreddits[i] = 0
    subreddit_comment_amount = list_of_subreddits.copy()

    for comment in r.redditor(bot_name).comments.new(limit=None):
        if comment.subreddit.display_name not in list_of_excluded_subreddit and comment.subreddit.display_name not in list_of_subreddits.keys():
            list_of_subreddits.update({comment.subreddit.display_name: 0})
            subreddit_comment_amount.update(
                {comment.subreddit.display_name: 0})

        for subreddit in list_of_subreddits.keys():
            if subreddit == comment.subreddit.display_name:
                list_of_subreddits[subreddit] += comment.score
                subreddit_comment_amount[subreddit] += 1

    # Calculate average rate of karma for subreddits
    for i in list_of_subreddits.keys():
        if subreddit_comment_amount[i] != 0:
            list_of_subreddits[i] = list_of_subreddits[i] / \
                subreddit_comment_amount[i]

    # One in hundred chance to select a random subreddit
    if random.randint(0, random_subreddit_rate) == 0:
        if(use_custom_subreddit_list):
            return random.choice(list_of_subreddits)[0]
        else:
            # MIGHT NOT WORK CORRECLY
            return r.subreddit("all").hot(limit=1)[0].subreddit.display_name

    # Document ratings in a separate file
    document_subreddit_rating()

    # Return the subreddit with the highest average karma
    return random.choices(list(list_of_subreddits.keys()), weights=list(list_of_subreddits.values()), k=1)[0]


def document_subreddit_rating():
    sorted_list_of_subreddits = sorted(
        list_of_subreddits.items(), key=lambda x: x[1], reverse=True)
    with open("subreddit_rating.txt", "w") as f:
        var = 0
        for i in sorted_list_of_subreddits:
            f.write(sorted_list_of_subreddits[var][0] + ": " + str(
                sorted_list_of_subreddits[var][1]) + "\n")
            var += 1


if __name__ == '__main__':
    r = bot_login()
    comments_replied_to = get_saved_comments()

    while True:
        try:
            # Select a subreddit to comment on
            if continous_subreddit_optimization:
                current_subreddit = weighted_subreddit_selection()
            else:
                current_subreddit = list_of_subreddits.values()[random.randint(
                    1, len(list_of_subreddits.values())-1)]

            print("Subreddit: " + current_subreddit)

            # Comment on the selected subreddit
            run_bot(r, comments_replied_to, current_subreddit)
        except praw.exceptions.RedditAPIException as e:
            print("Reddit api break: " + str(e))

        # Sleep for a while to simulate human behaviour, and avoid spam
        sleep_time = random.randint(10, 30)
        print("Sleeping for " + str(sleep_time) + " seconds...")
        time.sleep(sleep_time)
