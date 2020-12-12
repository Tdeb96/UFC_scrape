import pandas as pd
import numpy as np
from datetime import date
from flashgeotext.geotext import GeoText

#Set names for athletes and fights doc
athletes_name = './Data/20201207Athletes.pkl'
fights_name = './Data/20201207fights.pkl'

#First we load the athletes dataset
athletes = pd.read_pickle(athletes_name)

#Start with the athlete dataset, we work from left to right

#drop Athlete_URL
athletes = athletes.drop(columns = "Athlete_URL")

#Extract city and country from Hometown variable

def customsplit(df): #Create a small custom sort function for our case
    split = df.split(',')
    if split == ['']:
        city = np.nan
        country = np.nan
    elif len(split) == 1:
        city = np.nan
        country = split[0]
    else:
        city = split[0]
        country = split[1]
    return [city, country]

athletes[["City","Nation"]] = athletes.apply(lambda x: customsplit(x['Hometown']), axis=1, result_type='expand')
athletes = athletes.drop(columns = "Hometown") #drop Hometown
athletes = athletes.drop(columns = "Trains at") #drop Trains at column for lack of variation / information

#Convert body measurements to metric system
#Fill body measurements with nans
athletes[["Age","Height","Weight","Reach","Leg reach"]] = athletes[["Age","Height","Weight","Reach","Leg reach"]].replace(r'^\s*$', np.nan, regex=True)

athletes["Age"] = athletes["Age"].astype(float)
athletes["Height"] = athletes["Height"].astype(float)*2.54
athletes["Weight"] = athletes["Weight"].astype(float)*0.45359237
athletes["Reach"] = athletes["Reach"].astype(float)*2.54
athletes["Leg reach"] = athletes["Leg reach"].astype(float)*2.54

#Convert octagon debut to datetime object
athletes["Octagon Debut"] = pd.to_datetime(athletes['Octagon Debut'], format='%b. %d, %Y')

#Convert the headline to valuable information
athletes[["Division","record"]] = athletes["headline"].str.split("• ", expand = True)
athletes = athletes.drop(columns = "headline") #drop headline

#Create variable with ranking if athlete is in the top 15 in the division
athletes["Top15_ranking"] = athletes["Division"].str.extract('(\d+)')
athletes['Division'] = athletes['Division'].str.replace('\d+', '').str.replace('#', '')

#Expand the record into wins losses and draws
athletes["record"] = athletes["record"].str.split("(", expand = True)[0].str.replace(" ","")
athletes[["Wins", "Losses", "draws",]] = athletes["record"].str.split("-", expand = True)
athletes = athletes.drop(columns = "record")

#simple cleaning
athletes['Striking accuracy'] = athletes['Striking accuracy'].str.replace("%", '')
athletes['Grappling accuracy'] = athletes['Grappling accuracy'].str.replace("%", '')
athletes['Sig. Str. Defense'] = athletes['Sig. Str. Defense'].str.replace("%", '').str.replace(" ", '')
athletes['Takedown Defense'] = athletes['Takedown Defense'].str.replace("%", '').str.replace(" ", '')

#Get rid of percentages in multiple statistics
del_perc = ['Sig_str_by_position_Standing', 'Sig_str_by_position_Clinch',
       'Sig_str_by_position_Ground', 'Win_by_way_KO/TKO', 'Win_by_way_DEC',
       'Win_by_way_SUB']
for i in del_perc:
    athletes[i] = athletes[i].str.split("(", expand = True)[0].str.replace(" ","")

#Turn columns containing numeric values to float and fill with nan
numeric_cols = ['Age', 'Height', 'Weight', 'Reach',
       'Leg reach', 'Striking accuracy', 'Grappling accuracy',
       'Sig. Strikes Landed', 'Sig. Strikes Attempted', 'Takedowns Landed',
       'Takedowns Attempted', 'Sig. Str. Landed', 'Sig. Str. Absorbed',
       'Takedown avg', 'Submission avg', 'Sig. Str. Defense',
       'Takedown Defense', 'Knockdown Ratio',
       'Sig_str_by_position_Standing', 'Sig_str_by_position_Clinch',
       'Sig_str_by_position_Ground', 'Win_by_way_KO/TKO', 'Win_by_way_DEC',
       'Win_by_way_SUB', 'Sig_strikes_head', 'Sig_strikes_body',
       'Sig_strikes_leg', 'Top15_ranking', 'Wins', 'Losses', 'draws']
for i in numeric_cols:
    athletes[i] = pd.to_numeric(athletes[i])

#Turn average fight time to timedelta
athletes.loc[athletes["Average fight time"] != '', "Average fight time"] \
    = ['00:' + x for x in athletes.loc[athletes["Average fight time"] != '', "Average fight time"]]
athletes["Average fight time"] = pd.to_timedelta(athletes["Average fight time"], errors = 'coerce')

#Fill remaining empty objects with None
athletes = athletes.replace('',np.nan)

#Unify and change column names
new_col_names = ['Name', 'Status', 'Age', 'Height', 'Weight', 'Octagon_debut', 'Reach',
                 'Leg_reach', 'Striking_accuracy', 'Grappling_accuracy',
                 'Sig_strikes_landed', 'Sig_strikes_attempted', 'Takedowns_landed',
                 'Takedowns_attempted', 'Sig_str_landed_per_min', 'Sig_str_absorbed_per_min',
                 'Takedown_avg_15min', 'Submission_avg_15min', 'Sig_str_defense_perc',
                 'Takedown_defense_perc', 'Knockdown_ratio', 'Average_fight_time',
                 'Sig_str_standing', 'Sig_str_clinch',
                 'Sig_str_ground', 'Win_by_way_KO_TKO', 'Win_by_way_DEC',
                 'Win_by_way_SUB', 'Sig_strikes_head', 'Sig_strikes_body',
                 'Sig_strikes_leg', 'Fighting_style', 'City', 'Nation', 'Division',
                 'Top15_ranking', 'Wins', 'Losses', 'Draws']
athletes.columns = new_col_names

#Now we clean the list with fights
fights = pd.read_pickle(fights_name)

events = pd.read_pickle('./Data/Events.pkl')

#Turn odds to float
fights[['Blue_odds', "Red_odds"]] = fights[['Blue_odds', "Red_odds"]].replace("+","")

#Replace only "-" for np.nan
odds = ['Blue_odds', "Red_odds"]
for i in odds:
    fights.loc[fights[i] == "-", i] = np.nan #turn no odds to nan
    fights.loc[fights[i] == "--", i] = np.nan #same for this one
    fights[i] = fights[i].str.replace("EVEN", '100') #turn even odds to +100
    fights[i] = pd.to_numeric(fights[i])

#turn fight time to timedelta
fights.loc[fights["Fight_time"] != '', "Fight_time"] \
    = ['00:' + x for x in fights.loc[fights["Fight_time"] != '', "Fight_time"]]
fights["Fight_time"] = pd.to_timedelta(fights["Fight_time"], errors = 'coerce')

#We now clean the datetime, but we need to add the year

#Only extract the month and the day
fights[["Month", "Day"]] = fights["DateTime"].str.split(" ", expand = True).iloc[:, [1,2]]

#Now we need to get creative, we know that they have had consecutive events since 1993 and there has never been a year
# without an event, thus:
fights["Year"] = ""
month_prev = 12
year = 2020
year_iteration = 0
month = {'Jan':1, 'Feb':2 , 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
for i in fights["Month"]:
    if month[i] > month_prev:
        year -= 1
    month_prev = month[i]
    fights.loc[year_iteration, "Year"] = year
    year_iteration += 1

#Make Date a datetime object
fights["Date"] = pd.to_datetime(fights["Year"].astype(str)+"-"+fights["Month"]+"-"+fights["Day"], format = "%Y-%b-%d")

#Make day a numeric
fights["Day"] = pd.to_numeric(fights["Day"])

#Drop DateTime column
fights = fights.drop(columns = "DateTime")

#Extract Country and city from Location
geotext = GeoText(use_demo_data=True) #Prepare geotext

def countrycity(df):
    places = geotext.extract(input_text = df)
    if len(list(places["countries"].keys())) == 0:
        country = "Unknown"
    else:
        country = list(places["countries"].keys())[0]
    if len(list(places["cities"].keys())) == 0:
        city = "Unknown"
    else:
        city = list(places["cities"].keys())[0]
    return [country, city]

fights[["Country","City"]] = fights.apply(lambda x: countrycity(x['Location']), axis=1, result_type='expand')

#Drop the Location column
fights = fights.drop(columns = "Location")

#Drop "bout" from division
fights["Weight_class"] = fights["Weight_class"].str.replace(" Bout", "")

#Now prepare the keys for use in of the fights
athletes["Fighter_ID"] = np.arange(len(athletes["Division"]))
fights["Fight_ID"] = np.arange(len(fights["Weight_class"]))

#add fighter key as a foreign key to the fights dataset
fighter_keys = athletes[["Name", "Fighter_ID"]]
fights = fights.merge(right = fighter_keys, how = "left", left_on = "Blue_name", right_on = "Name")
fights = fights.drop(columns = "Name_y").rename(columns = {"Fighter_ID": "Fighter_ID_blue"})
fights = fights.merge(right = fighter_keys, how = "left", left_on = "Red_name", right_on = "Name")
fights = fights.drop(columns = "Name").rename(columns = {"Fighter_ID": "Fighter_ID_red"})

#Add keys to the fights
fights["Fight_ID"] = np.arange(len(fights["Weight_class"]))

#Move the columns containing the indices to the front
cols_fights = list(fights)
cols_fights.insert(0, cols_fights.pop(cols_fights.index('Fighter_ID_red')))
cols_fights.insert(0, cols_fights.pop(cols_fights.index('Fighter_ID_blue')))
cols_fights.insert(0, cols_fights.pop(cols_fights.index('Fight_ID')))
fights = fights.loc[:, cols_fights]

cols_athletes = list(athletes)
cols_athletes.insert(0, cols_athletes.pop(cols_athletes.index('Fighter_ID')))
athletes = athletes.ix[:, cols_athletes]

#Save cleaned datasets as csv
today = date.today()
save_name_athletes = "./Data/"+today.strftime("%Y%m%d")+"athletes"+".csv"
save_name_fights = "./Data/"+today.strftime("%Y%m%d")+"fights"+".csv"

athletes.to_csv(save_name_athletes, index = False)
fights.to_csv(save_name_fights, index = False)