import requests
import json
import numpy
import tweepy
from datetime import datetime, timedelta
import os

VAX_URL_PREFIX = "https://data.ontario.ca/api/3/action/datastore_search?resource_id=775ca815-5028-4e9b-9dd4-6975ff1be021&sort=_id%20asc&filters={%22Date%22:%22"
VAX_URL_POSTFIX = "%22}"
ON_POPULATION = 14755211    #Source: https://www.fin.gov.on.ca/en/economy/demographics/quarterly/

BAR_LENGTH = 10
PROGRESS_BAR = ['⬛️', '🔳', '⬜️']

BASE_PATH = '/root/projects/vacbot'
STATUS_PATH = BASE_PATH + '/on_vax_tracker_last_date.ini'

TWITTER_CONSUMER_KEY    = "REPLACE_WITH_YOUR_TWITTER_CONSUMER_KEY"
TWITTER_CONSUMER_SECRET = "REPLACE_WITH_YOUR_TWITTER_CONSUMER_SECRET"
TWITTER_ACCESS_KEY      = "REPLACE_WITH_YOUR_TWITTER_ACCESS_KEY"
TWITTER_ACCESS_SECRET   = "REPLACE_WITH_YOUR_TWITTER_ACCESS_SECRET"
TWEET_TEMPLATE = '''On {report_date}, #Ontario reported:

% population vaccinated with at least 1 dose:
{first_dose_bar} {first_dose_percentage}%
12+ {first_dose_eligible}%
18+ {first_dose_adult}%

% population fully vaccinated:
{full_dose_bar} {full_dose_percentage}%
12+ {full_dose_eligible}%
18+ {full_dose_adult}%

Total doses administered: {total_dose}
#OntarioVaccine @VaxHuntersON'''

twitter_auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
twitter_auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(twitter_auth)

def bar_str(percentage):
    full = int(numpy.floor(percentage/100*BAR_LENGTH))
    half = 1 if (percentage/100*BAR_LENGTH - full) >= 0.3 else 0
    empty = BAR_LENGTH - full - half
    return PROGRESS_BAR[0] * full + PROGRESS_BAR[1] * half + PROGRESS_BAR[2] * empty

def update_vac_progress(last_date, debug = True):
    check_date = last_date + timedelta(days=1)
    vax_response = requests.get(VAX_URL_PREFIX + check_date.strftime("%Y-%m-%d") + VAX_URL_POSTFIX)
    vax_response_obj = json.loads(vax_response.text)
    
    while (len(vax_response_obj["result"]["records"]) > 0):
        vax_data = {}
        for record in vax_response_obj["result"]["records"]:
            vax_data[record["Agegroup"]] = record
        population_12to17   = int(vax_data["12-17yrs"]["Total population"])
        population_adult    = int(vax_data["Adults_18plus"]["Total population"])
        atleast1dose_12to17 = int(vax_data["12-17yrs"]["At least one dose_cumulative"])
        atleast1dose_adult  = int(vax_data["Adults_18plus"]["At least one dose_cumulative"])
        two_dose_12to17     = int(vax_data["12-17yrs"]["Second_dose_cumulative"])
        two_dose_adult      = int(vax_data["Adults_18plus"]["Second_dose_cumulative"])

        total_dose = atleast1dose_12to17 + two_dose_12to17 + atleast1dose_adult + two_dose_adult + int(vax_data["Undisclosed_or_missing"]["At least one dose_cumulative"]) + int(vax_data["Undisclosed_or_missing"]["Second_dose_cumulative"])

        atleast1dose_adult_percent = round(atleast1dose_adult * 100.0 / population_adult, 2)
        two_dose_adult_percent = round(two_dose_adult * 100.0 / population_adult, 2)
        atleast1dose_eligible_percent = round((atleast1dose_adult+atleast1dose_12to17) * 100.0 / (population_adult+population_12to17), 2)
        two_dose_eligible_percent = round((two_dose_adult+two_dose_12to17) * 100.0 / (population_adult+population_12to17), 2)
        atleast1dose_population_percent = round((atleast1dose_adult+atleast1dose_12to17) * 100.0 / ON_POPULATION, 2)
        two_dose_population_percent = round((two_dose_adult+two_dose_12to17) * 100.0 / ON_POPULATION, 2)

        first_dose_bar = bar_str(atleast1dose_population_percent)
        full_dose_bar = bar_str(two_dose_population_percent)

        tweet_text = TWEET_TEMPLATE.format( first_dose_bar = first_dose_bar, 
                                            first_dose_percentage = atleast1dose_population_percent,
                                            first_dose_adult = atleast1dose_adult_percent,
                                            first_dose_eligible = atleast1dose_eligible_percent,
                                            full_dose_bar = full_dose_bar,
                                            full_dose_percentage = two_dose_population_percent,
                                            full_dose_adult = two_dose_adult_percent,
                                            full_dose_eligible = two_dose_eligible_percent,
                                            report_date = check_date.strftime("%Y-%m-%d"),
                                            total_dose = f'{total_dose:,}' ) #,
                                            #previous_day_dose = f'{latest_vax["previous_day_doses_administered"]:,}')

        if debug:
            print(tweet_text)
        else:
            twitter_api.update_status(tweet_text)

        print("[" + str(datetime.now()) + "] [INFO] Availability tweeted for " + check_date.strftime("%Y-%m-%d"))

        with open(STATUS_PATH, 'w') as status_file:
            status_file.write(check_date.strftime("%Y-%m-%d"))

        check_date += timedelta(days=1)
        vax_response = requests.get(VAX_URL_PREFIX + check_date.strftime("%Y-%m-%d") + VAX_URL_POSTFIX)
        vax_response_obj = json.loads(vax_response.text)

def main():
    try:
        with open(STATUS_PATH, 'r') as status_file:
            last_date = datetime.strptime(status_file.read(), "%Y-%m-%d")
        update_vac_progress(last_date, debug=False)
    except Exception as ex:
        print("[" + str(datetime.now()) + "] [ERROR] Unknown error:\n" + str(ex))

if __name__ == "__main__":
    main()
