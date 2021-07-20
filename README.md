# VacTrackOntario
Vaccine Tracker Ontario on Twitter 

[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/VacTrackOntario.svg?style=social&label=Follow%20%40VacTrackOntario)](https://twitter.com/VacTrackOntario)

Project page: https://lindayi.me/vaccinebotto/

## Dependencies
- python (tested on 3.6.9)
- numpy (tested on 1.19.0)
- tweepy (tested on 3.10.0)

## Setup
1. Replace the `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_KEY`, and `TWITTER_ACCESS_SECRET` values with your own Twitter account credentials.
2. Replace the `BASE_PATH` value with the path that you intend to run the script under. The script will read the status file `on_vax_tracker_last_date.ini` from the `BASE_PATH`. Feel free to modify `STATUS_PATH` as well if you do not like the file name or do not intend to store the status file under the same directory as the script.
3. (Optional) Modify parameters such as `ON_POPULATION`, `BAR_LENGTH`, and `TWEET_TEMPLATE`. It may be a good idea to test if your template is over the length limit of a tweet.
4. Set up a crontab job to run the script periodically. For example: 
`*/5 10 * * * python3 /projects/vacbot/on_vax_tracker.py >> /projects/vacbot/on_vax_tracker.log`

For the detailed process of obtaining credentials for your Twitter account, please see https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials
