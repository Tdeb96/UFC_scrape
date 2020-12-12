# importing libraries
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import numpy as np
import time
from datetime import date

#define output list
athletes = []

#base url of UFC website
url_base = 'https://www.ufc.com/athletes/all?&search=&page='

#Page number
page_number = 0
#Create a loop to cycle over all the webpages with different athletes
while(True):
    # Website URL
    print("extracting page: ", page_number)
    url = url_base + str(page_number)

    # Connect to the website
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

    # Extract the athletes from the page
    content_lis = soup.find_all('div', attrs={'class': 'c-listing-athlete-flipcard__back'})

    #Break if the page contains no athletes, i.e. if you reached the end of the webpages
    if len(content_lis) == 0:
        print("Fin.")
        break

    #Extract the usefull information from the class
    for div in content_lis:
        name_raw = div.find('span', attrs={'class': 'c-listing-athlete__name'})  # Extract the name class
        name = name_raw.getText().strip()
        a_tag = div.find('a', href=True)  # extract the href part
        href = a_tag['href']  # get the href attribute
        athletes.append([name, href])  # append to array
    #increase the page number
    page_number += 1

#Convert the data into a pandas dataframe
athletes = pd.DataFrame(athletes, columns= ["Name", "Athlete_URL"])

#Store the dataset using pickle
athletes.to_pickle("./Data/Athletes.pkl")

#For each athlete we now extract additional information from their respective pages
url_fighter_base = "https://www.ufc.com" #Base url

athlete_number = 0
for fighter in athletes["Athlete_URL"].iteritems():
    print("Extracting information about UFC fighter:", athletes["Name"][athlete_number])

    # Website URL
    url_fighter = url_fighter_base + str(fighter[1])

    # Connect to the website
    try:
        page = urllib.request.urlopen(url_fighter)
    except:
        trynumber = 1
        while trynumber<11: #If error occurs, wait for 5 seconds then try again
            time.sleep(5)
            try:
                page = urllib.request.urlopen(url_fighter)
            except:
                print("An error occured, trying again, try:",trynumber)
                trynumber += 1
        break

    # Get HTML representation of the webpage
    soup = BeautifulSoup(page, 'html.parser')

    #First we extract Biography of the fighter
    biography_info = soup.find('div', attrs={'class': 'c-bio__content'})

    #extract the titles and the information
    titels = biography_info.find_all('div', attrs={'class': "c-bio__label"})
    information = biography_info.find_all('div', attrs={'class': "c-bio__text"})

    #define empty set for all interesting items
    biography = []

    #Combine all information with the labels
    for i in range(len(titels)):
        label = titels[i].getText().strip()
        value = information[i].getText().strip()
        biography.append([label, value])

    #Extract the headline (containing ranking, division and record)
    headline_raw = soup.find('div', attrs={'class': 'c-hero__headline-suffix tz-change-inner'})
    headline = headline_raw.getText().strip().replace("\n","").replace("  ","")
    biography.append(["headline",headline])

    #striking and grappling accuracy
    accuracy = soup.find_all('text', attrs={'class': "e-chart-circle__percent"})
    if len(accuracy) == 0: #Somethmes no additional statistics are available
        print("No additional statistics available")
    else:
        if len(accuracy) == 1: #sometimes only 1 stat is available, then we have to run a slightly other line of code
            title = soup.find('div', attrs={'class': "c-overlap--stats__title"}).getText().strip()
            biography.append([title, accuracy[0].getText().strip()])
        else:
            biography.append(["Striking accuracy", accuracy[0].getText().strip()])
            biography.append(["Grappling accuracy", accuracy[1].getText().strip()])

        # First set of statistics
        statistics_labels = soup.find_all('dt', attrs={'class': "c-overlap__stats-text"})
        statistics_values = soup.find_all('dd', attrs={'class': "c-overlap__stats-value"})
        for i in range(len(statistics_labels)):
            label = statistics_labels[i].getText().strip()
            value = statistics_values[i].getText().strip()
            biography.append([label, value])

        # Second set of statistics
        statistics_labels = soup.find_all('div', attrs={'class': "c-stat-compare__label"})
        statistics_values = soup.find_all('div', attrs={'class': "c-stat-compare__number"})

        #Sometimes values are missing, then we need to take a closer look into the code
        if len(statistics_values)!=len(statistics_labels):
            #identify two groups of statistics
            group1 = soup.find_all('div', attrs={'class': "c-stat-compare__group-1"})
            group2 = soup.find_all('div', attrs={'class': "c-stat-compare__group-1"})

            #Check if there is a value, if not, skip the statistic
            for stat in group1:
                if len(stat.find('div', attrs = {'class': "c-stat-compare__number"})) != 0:
                    value = stat.find('div', attrs = {'class': "c-stat-compare__number"}).getText().strip()
                    label = stat.find('div', attrs = {'class': "c-stat-compare__label"}).getText().strip()
                    biography.append([label, value])

            for stat in group2:
                if len(stat.find('div', attrs = {'class': "c-stat-compare__number"})) != 0:
                    value = stat.find('div', attrs = {'class': "c-stat-compare__number"}).getText().strip()
                    label = stat.find('div', attrs = {'class': "c-stat-compare__label"}).getText().strip()
                    biography.append([label, value])

        else: #Else, match labels with the stats
            for i in range(len(statistics_labels)):
                label = statistics_labels[i].getText().strip()
                value = statistics_values[i].getText().strip()
                biography.append([label, value])

        # significant strikes per position + win by which way
        sigstrikes_labels = soup.find_all('div', attrs={'class': "c-stat-3bar__label"})
        sigstrikes_values = soup.find_all('div', attrs={'class': "c-stat-3bar__value"})

        for i in range(3):
            label = "Sig_str_by_position_" + sigstrikes_labels[i].getText().strip()
            value = sigstrikes_values[i].getText().strip()
            biography.append([label, value])

        # Win by which way
        for i in range(3, 6):
            label = "Win_by_way_" + sigstrikes_labels[i].getText().strip()
            value = sigstrikes_values[i].getText().strip()
            biography.append([label, value])

        # significant strikes by target
        biography.append(
            ["Sig_strikes_head", soup.find('text', attrs={'id': "e-stat-body_x5F__x5F_head_value"}).getText().strip()])
        biography.append(
            ["Sig_strikes_body", soup.find('text', attrs={'id': "e-stat-body_x5F__x5F_body_value"}).getText().strip()])
        biography.append(
            ["Sig_strikes_leg", soup.find('text', attrs={'id': "e-stat-body_x5F__x5F_leg_value"}).getText().strip()])

    # Add the information to the pandas dataframe
    for item in biography:
        if item[0] not in athletes.columns:  # if column does not exist yet add it to global dataframe
            athletes[item[0]] = ''
        try:
            athletes.at[athlete_number,item[0]] = item[1]
        except:
            athletes[item[0]] = athletes[item[0]].astype(str)
            athletes.at[athlete_number, item[0]] = item[1]

    athlete_number += 1

today = date.today()
save_name = "./Data/"+today.strftime("%Y%m%d")+"Athletes"+".pkl"
athletes.to_pickle(save_name)

