from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import time
from datetime import date
import numpy as np
from selenium import webdriver

#Define output list
events = []

#Event URL's
url_UFC = "https://www.ufc.com/events"
url_page_number = "?page="
url_past_events = "#events-list-past"


#First extract an overview of all UFC events
page_number = 0
while(True):
    print("extracting page: ", page_number)

    #UFC url
    url = url_UFC+url_page_number+str(page_number)+url_past_events

    #Connect to the website
    try:
        page = urllib.request.urlopen(url)
    except:
        trynumber = 1
        while trynumber < 11:  # If error occurs, wait for 5 seconds then try again
            time.sleep(5)
            try:
                page = urllib.request.urlopen(url)
            except:
                print("An error occured, trying again, try:", trynumber)
                trynumber += 1
        break

    # Get HTML representation of the webpage
    soup = BeautifulSoup(page, 'html.parser')

    #Get main event fight + website link
    event_list = soup.find_all('h3', attrs = {'class': 'c-card-event--result__headline'})

    # Break if the page contains no events, i.e. if you scraped all events
    if len(event_list) == 0:
        print("Fin.")
        break

    for event in event_list:
        event_tag = event.find('a', href = True) #Get the tag with the reference
        href = event_tag['href']
        text = event_tag.getText()
        events.append([text, href])
        print("Saving event ",text) #Nice for output, turn this off for speed
    page_number +=1

events = pd.DataFrame(events, columns= ["Mainevent", "Event_URL"]) #Turn into pandas df
events.to_pickle("./Data/Events.pkl") #save as pickle
events = pd.read_pickle("./Data/Events.pkl") #Load events file to speed up the code

#Now we extract all fights per event
url_UFC = "https://www.ufc.com" #Base event url

event_number = 0
fights = []

# Connect to the website using selenium
driver = webdriver.Chrome("./Data/chromedriver")

for event in events["Event_URL"].iteritems():
    print("Extracting information about UFC event:", events["Mainevent"][event_number])
    url_event = url_UFC+str(event[1]) #Event url

    #Navigate to event page
    try:
        driver.get(url_event)
    except:
        time.sleep(15)
        driver.get(url_event)
    time.sleep(10)
    page = driver.page_source

    # Get HTML representation of the webpage
    soup = BeautifulSoup(page, 'html.parser')

    #First we extract data about the event itself
    try:
        event_name = soup.find('div', attrs = {'class': 'field field--name-node-title field--type-ds field--label-hidden field__item'}).getText().strip()
    except: #Sometimes the page does not load correctly and it cannot find a field name, in that case we wait 30 seconds before trying again
        time.sleep(30)
        driver.get(url_event)
        time.sleep(10)
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        event_name = soup.find('div', attrs = {'class': 'field field--name-node-title field--type-ds field--label-hidden field__item'}).getText().strip()

    event_datetime = soup.find('div', attrs = {'class': 'c-hero__headline-suffix tz-change-inner'}).getText().strip()

    try:
        event_location = soup.find('div', attrs = {'class': 'field field--name-venue field--type-entity-reference field--label-hidden field__item'}).getText().strip()
    except:
        event_location = "Location unknown" #If no location, insert "event_location"

    #Save these characteristics to add to each fight
    base = [event_name, event_datetime, event_location]

    #Locate and loop over all the fights
    full_card = soup.find_all('div', attrs={'class':'c-listing-fight'})

    #Test if the card is in the future, if the card is in the future, skip the card
    try:
        future_test = soup.find('div', attrs={'class': 'c-listing-fight__result-text round'}).getText()
    except:
        event_number+=1
        continue

    if len(future_test) == 0:
        event_number+=1
        continue

    for bout in full_card:
        performance_bonus = bout.find('div', attrs={'class':'c-listing-fight__awards'}).getText().strip()
        if len(performance_bonus) ==0: #if no performance bonus, change to "No bonus"
            performance_bonus = "No bonus"
        weight_class = bout.find('div', attrs={'class':'c-listing-fight__class'}).getText().strip()
        if len(weight_class) == 0: #If no weightclass, change to "No weightclass"
            weight_class = "No weightclass"
        fighter_names = bout.find_all('div', attrs={'class': 'c-listing-fight__detail-corner-name'})
        red_name = fighter_names[0].getText().strip() #first name is blue corner
        blue_name = fighter_names[1].getText().strip()
        odds = bout.find_all('span', attrs={'class': 'c-listing-fight__odds-amount'})
        red_odds = odds[0].getText().strip()
        blue_odds = odds[1].getText().strip()
        if len(odds) == 0:  # if no odds, change to nan
            blue_odds = np.nan
            red_odds = np.nan
        round_length = bout.find('div', attrs={'class': 'c-listing-fight__result-text round'}).getText().strip()
        fight_time = bout.find('div', attrs={'class': 'c-listing-fight__result-text time'}).getText().strip()
        finish_method = bout.find('div', attrs={'class': 'c-listing-fight__result-text method'}).getText().strip()
        #Get the winner of the bout
        red_corner_details = bout.find('div', attrs={'class': 'c-listing-fight__corner--red'})
        blue_corner_details = bout.find('div', attrs={'class': 'c-listing-fight__corner--blue'})
        if red_corner_details.find('div', attrs={'class': 'c-listing-fight__outcome--Win'}) != None:
            winner = "Red"
            winner_name = red_name
        elif blue_corner_details.find('div', attrs={'class': 'c-listing-fight__outcome--Win'}) != None:
            winner = "Blue"
            winner_name = blue_name
        else:
            winner = "Draw"
            winner_name = np.nan
        #copy base characteristics and append all other characteristics
        bout_characteristics = base.copy()
        bout_characteristics.extend([performance_bonus, weight_class, blue_name, red_name, winner, winner_name, blue_odds,
                                     red_odds, round_length, fight_time, finish_method])
        fights.append(bout_characteristics)

    if events["Mainevent"][event_number] == "The Beginning": #This is the last true ufc event, the remaining events are cancelled events
        break
    event_number+=1

fights = pd.DataFrame(fights, columns= ["Name", "DateTime", "Location", "Bonus", "Weight_class", "Blue_name", "Red_name"
                                        , "Winner", "Winner_name", "Blue_odds", "Red_odds", "Number_rounds",
                                        "Fight_time", "Finish_method"])  #Turn into pandas df

#Save the resulting dataset
today = date.today()
save_name = "./Data/"+today.strftime("%Y%m%d")+"fights"+".pkl"
print("Finishing the scrape, saving the file")
fights.to_pickle(save_name)

