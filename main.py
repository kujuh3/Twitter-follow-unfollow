import os
import tweepy
from dotenv import load_dotenv
from time import sleep
from random import uniform

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
                       access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET, wait_on_rate_limit=True)

def followedCount():
    followedfile = open("followed.txt", "r")
    followedfiletotal = len(followedfile.read().split("\n"))-1
    followedfile.close()

    return followedfiletotal

def exitprogram():
    os._exit(1)

def main():
    print(f"\nAmount followed through this program: {followedCount()}")
    choice = input('''\nWhat would you like to do?
    1. Follow users of another user
    2. Unfollow users followed from this program
    3. Exit
''')

    actions = {
        1: followUsers,
        2: unfollowAll,
        3: exitprogram
    }

    try:
        actions[int(choice)]()
    except (KeyError, ValueError):
        print("What the fuck did you just press?")
        main()
    finally:
        main()


def error_handling(e):
    error = type(e)
    if error == tweepy.TooManyRequests:
        print("You've hit a limit! Sleeping for 30 minutes.")
        sleep(60 * 30)
    if error == tweepy.TweepyException:
        print('Uh oh. Could not complete task. Sleeping 10 seconds.')
        sleep(10)


def getMyfriends():
    print("\nFetching your own followers...")
    my_id = client.get_me().data.id
    my_friends_response = client.get_users_followers(
        id=my_id, max_results=1000)
    allFriends = []
    if my_friends_response.data:
        while True:
            print(f"{len(allFriends)} followers fetched..")
            if "next_token" not in my_friends_response.meta:
                for user in my_friends_response:
                    for x in user:
                        if hasattr(x, "id"):
                            allFriends.append(x.id)
                break
            else:
                for user in my_friends_response:
                    for x in user:
                        if hasattr(x, "id"):
                            allFriends.append(x.id)
                sleep(5)
                next_token = my_friends_response.meta["next_token"]
                my_friends_response = client.get_users_followers(
                    id=my_id, max_results=1000, pagination_token=next_token)
        return allFriends
    else:
        print("I have no friends :(\n")
        return allFriends


def followUsers():
    ignoresappend = open("ignores.txt", "a+")
    followingappend = open("followed.txt", "a+")
    file_contents = ignoresappend.read().split("\n")

    myfollowers = getMyfriends()
    blacklist = file_contents + list(set(myfollowers) - set(file_contents))

    name = input("Insert twitter username without @ sign: ")
    amount = int(
        input("How many would you like to follow?: "))
    user = client.get_user(username=name)
    followers = client.get_users_followers(
        id=user.data.id, max_results=1000)
    counter = 0
    timecounter = amount*18
    for user in followers:
        for x in user:
            if counter < amount:
                if hasattr(x, "id"):
                    try:
                        if str(x.id) in blacklist:
                            print(
                                f"User has previously been followed or is following you: {x}")
                            pass
                        else:
                            client.follow_user(x.id)
                            ignoresappend.write(f"{x.id}\n")
                            followingappend.write(f"{x.id}\n")
                            ignoresappend.flush()
                            followingappend.flush()
                            counter += 1
                            print(
                                f"\nUser followed: {x} - ({counter}/{amount})\nTime remaining: {round((timecounter)/60, 2)}min")
                            sleep(18)
                            timecounter -= 18
                    except (tweepy.TweepyException, tweepy.TooManyRequests) as e:
                        error_handling(e)
            else:
                print("Job done!")
                break
    ignoresappend.close()
    followingappend.close()


def unfollowAll():
    f = open("followed.txt", "r")
    followed_users = [line.replace("\n", "") for line in f.readlines() if line.strip()]
    f.close()

    if len(followed_users) > 0:
        copylist = followed_users.copy()
        print(f"Users followed through this program: {len(followed_users)}\n")
        amount = int(input(
        '''Unfollows always start from the oldest.
           How many would you like to unfollow?: '''))
        counter = 0
        timecounter = (len(followed_users)-1)*18

        for user in followed_users:
            if counter < amount:
                try:
                    client.unfollow_user(target_user_id=user)
                except (tweepy.TweepyException, tweepy.TooManyRequests) as e:
                    error_handling(e)
                finally:
                    copylist.remove(user)
                    #Well update the file this way so that sudden exits wont have an effect on future runs
                    with open("followed.txt", "w") as outfile:
                        for line in copylist:
                            outfile.write(line+"\n")
                    counter+=1
                    print(f"\nUser unfollowed - ({counter}/{amount})\nTime remaining: {round((timecounter)/60, 2)}min")
                    timecounter-=18
                    sleep(18)
            else:
                print("Ready!")
                break

    else:
        print("No followed users found.")
    
if __name__ == "__main__":
    main()
