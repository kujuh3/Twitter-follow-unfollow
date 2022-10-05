Mass follow and or unfollow users of another user

I guess you could also call it a follower churn bot.

##
<h2>Usage</h2>

<h3>Install required libraries:</h3>
<code>pip install tweepy</code>
<code>pip install dotenv</code>
##

<h2>Logic</h2>
Data written to files are in realtime so random quits wont matter
<br><br>
<li>Ignores.txt file contains users that have been previously followed by the program -> these users will be ignored in future
<li>Followed.txt contains users that have been followed but not unfollowed
<br>
<h3>Input and actions</h3>
<li>1. Ask for user whos followers to be followed -> ask for amount -> follow users -> add users that have been followed to ignores and followed file.
<li>2. Ask for amount of users to be unfollowed -> unfollow given amount of users from oldest to latest -> delete entries from followed list
<li>3. Exit
