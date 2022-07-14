import praw
import time
import os
from munk import generate_comment
import random
from difflib import SequenceMatcher

# Set to false in the beginning, and then later, when you have enough data 
# on which subreddits, you can lower the search rate by setting it to true 
# (setting to true also increases the chance of the bot responding to a comment, 
# that was made from the bots comment, thereby starting a conversation)
use_custom_subreddit_list = False
# Setting this to 10, means 1 in 10 chance to select a random subreddit (lower in the beginning, higher for stable use when subreddit ratings are calculated)
random_subreddit_rate = 3  # Only useful if use_custom_subreddit_list is set to True
max_comments_on_single_thread = 25
max_search_on_thread = 4
sleep_time = random.randint(45, 180)  # In seconds
list_of_excluded_subreddit = ["interestingasfuck", "oldschoolcool", "art"]

bot_name = "AbsurdlyWholesome"
username = os.getenv('BOT_NAME')
password = os.getenv('PASSWORD')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
should_wait = True

replies_filename = "comments_replied_to.txt"

# Art subreddits doesnt work, as the both claims credit for all the works (:D)
# Oldschoolcool and subreddits with similar advanced and abstract topics, doesnt work well either, and often leads to angering people
list_of_subreddits = {}

# Get subreddit ratings from file, create if doesn't exist
with open("subreddit_rating.txt", "a+") as f:
    for line in f.readlines():
        list_of_subreddits.update(
            {line.split(":")[0]: float(line.split(":")[1].replace("\n", ""))})


def bot_login():
    try:
        r = praw.Reddit(username=username, password=password, client_id=client_id,
                        client_secret=client_secret, user_agent="Absurdly Wholesome v0.1")
        print("\n!!!Log in: successful")
    except e:
        print("Log in: failed\nError: {e}\nExiting...")
        exit()
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


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def generate_response_comment(comment, parent_comment, is_self_post=False):
    if(is_self_post):
        return str(generate_comment(
            comment.body, parent_comment.body[0]), True)
    try:
        return str(generate_comment(
            comment.body, parent_comment.body[0]))
    except AttributeError:
        return str(generate_comment(
            comment.body))


def document_comment_and_response(comment, comment_reply):
    with open(replies_filename, "a") as f:
        f.write(comment.id + "\n")
    with open("reply_history.txt", "a") as f:
        user_text = comment.body.encode('utf-8')
        f.write("########################\n" + str(user_text) +
                "\n" + str(comment_reply) + "\n\n")


def run_bot(r, comments_replied_to, current_subreddit, should_bot_wait):
    print("\n!!!Subreddit: " + current_subreddit)

    comment_amount = 0
    document_karma()

    for comment in r.subreddit(str(current_subreddit)).comments(limit=random.randint(1, max_comments_on_single_thread)):
        if comment.author.is_mod == False and len(comment.body) > 50 and comment.id not in comments_replied_to and comment.author != r.user.me() and comment.is_submitter == False and "bot" not in str(comment.author):
            print("\n############Comment######\n",
                  comment.body)
            print("\n---Generating response...")

            # Check for parent comment
            parent_comment = ""
            if(comment.parent() != None):
                parent_comment = comment.parent()

            # Generate response and reply (could be better programmed)
            comment_reply = generate_response_comment(
                comment, parent_comment, comment.is_submitter)

            # Last checks before sendoff: did the bot just copy the exact or near exact sentence?
            if(comment_reply != "" and similar(comment.body, comment_reply) > 0.7):
                print("\n---Comment is too similar to the original, skipping...")
                break

            # Reply to comment
            print("\nResponse generated: " + comment_reply)
            comment.reply(body=comment_reply)
            comments_replied_to.append(comment.id)

            # Document comment and response in a separate file
            document_comment_and_response(comment, parent_comment)

            comment_amount += 1
        if (comment_amount > max_search_on_thread):
            break

    # If no comment was made, no need to wait
    if(comment_amount):
        should_bot_wait = True
    else:
        should_bot_wait = False  # If the bot didn't make any comments, it should not wait
        print("\n---No comments found matching requirements, continueing...")

    return should_bot_wait


def get_saved_comments():
    if not os.path.isfile(replies_filename):
        comments_replied_to = []
    else:
        with open(replies_filename, "r") as f:
            comments_replied_to = list(filter(None, f.read().split("\n")))
    return comments_replied_to


def document_subreddit_rating(subreddit_ratings):
    sorted_list_of_subreddits = sorted(
        subreddit_ratings.items(), key=lambda x: x[1], reverse=True)
    with open("subreddit_rating.txt", "w+") as f:
        for subreddits in sorted_list_of_subreddits:
            print(subreddits[0] + ": " + str(subreddits[1]))
            f.write(subreddits[0] + ": " + str(
                subreddits[1]) + "\n")

def weighted_subreddit_selection():
    # Reset values in weighted dictionary and make a copy containing amounts of comments
    for i in list_of_subreddits:
        list_of_subreddits[i] = 0.0
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

    print(list_of_subreddits)

    # Document ratings in a separate file
    document_subreddit_rating(list_of_subreddits)

    if random.randint(0, random_subreddit_rate) == 1 or use_custom_subreddit_list == False:
        print("\n---Random subreddit selection")
        return r.random_subreddit().display_name
    else:
        # Return the subreddit with the highest average karma based on weights
        return random.choices(list(list_of_subreddits.keys()), weights=list(list_of_subreddits.values()), k=1)[0]


round_count = 0
current_subreddit = ""

if __name__ == '__main__':
    r = bot_login()
    comments_replied_to = get_saved_comments()
    print("\n---Starting bot...")
    while True:
        round_count += 1
        print("ROUND: #" + str(round_count))
        try:
            # Select a subreddit to comment on
            while current_subreddit in list_of_excluded_subreddit or current_subreddit == "":
                print("\n---Trying to generate a subreddit...")
                current_subreddit = weighted_subreddit_selection()

            # Comment on the selected subreddit
            should_wait = run_bot(r, comments_replied_to,
                                  current_subreddit, should_wait)
        except praw.exceptions.RedditAPIException as e:
            print("\nReddit api break: " + str(e))

        if(should_wait):
            # Sleep for a number of seconds, to simulate human behaviour and avoid spam
            print("\n---Sleeping for " + str(sleep_time) + " seconds...")
            time.sleep(sleep_time)

        should_wait = True
