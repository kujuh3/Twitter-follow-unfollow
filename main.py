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
    print(f"\nOhjelman kautta seurattuja: {followedCount()}")
    choice = input('''\nMitä haluat tehdä?
    1. Seuraa käyttäjän seuraajia
    2. Epäseuraa ohjelman kautta seurattuja käyttäjiä
    3. Lopeta
''')

    actions = {
        1: followUsers,
        2: unfollowAll,
        3: exitprogram
    }

    try:
        actions[int(choice)]()
    except (KeyError, ValueError):
        print("Mitä vittua sä just painoit")
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
    print("\nHaetaan omia seuraajia...")
    my_id = client.get_me().data.id
    my_friends_response = client.get_users_followers(
        id=my_id, max_results=1000)
    allFriends = []
    if my_friends_response.data:
        while True:
            print(f"{len(allFriends)} seuraajaa haettu..")
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
        print("Ei mulla oo kavereita :(\n")
        return allFriends


def followUsers():
    ignoresappend = open("ignores.txt", "a+")
    followingappend = open("followed.txt", "a+")
    file_contents = ignoresappend.read().split("\n")

    myfollowers = getMyfriends()
    blacklist = file_contents + list(set(myfollowers) - set(file_contents))

    name = input("Syötä twitter käyttäjä ilman @ merkkiä: ")
    amount = int(
        input("Kuinka monta seurataan (n.200/päivä on suositeltua): "))
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
                                f"Käyttäjä jo seurattu/seuraa sinua: {x}")
                            pass
                        else:
                            client.follow_user(x.id)
                            ignoresappend.write(f"{x.id}\n")
                            followingappend.write(f"{x.id}\n")
                            ignoresappend.flush()
                            followingappend.flush()
                            counter += 1
                            print(
                                f"\nKäyttäjä seurattu: {x} - ({counter}/{amount})\nAikaa jäljellä: {round((timecounter)/60, 2)}min")
                            sleep(10)
                            timecounter -= 18
                    except (tweepy.TweepyException, tweepy.TooManyRequests) as e:
                        error_handling(e)
            else:
                print("Valmis!")
                break
    ignoresappend.close()
    followingappend.close()


def unfollowAll():
    f = open("followed.txt", "r")
    followed_users = [line.replace("\n", "") for line in f.readlines() if line.strip()]
    f.close()

    if len(followed_users) > 0:
        copylist = followed_users.copy()
        print(f"Ohjelman kautta seurattuja käyttäjiä: {len(followed_users)}\n")
        amount = int(input(
        '''Epäseuraamiset aloitetaan aina vanhimmista seurauksista.
        Montako epäseurataan?: '''))
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
                    print(f"\nKäyttäjä epäseurattu - ({counter}/{amount})\nAikaa jäljellä: {round((timecounter)/60, 2)}min")
                    timecounter-=18
                    sleep(18)
            else:
                print("Valmis!")
                break

    else:
        print("Ei seurattuja käyttäjiä.")
    
if __name__ == "__main__":
    main()