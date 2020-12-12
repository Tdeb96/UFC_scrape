import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

plt.rcParams['animation.ffmpeg_path'] ='E:\\Media\\ffmpeg\\bin\\ffmpeg.exe'


#import statistics
yearly = pd.read_csv('./Data/Yearly_stats.csv')

#Define colours and link them to type of fight
colours_dict = {'KO/TKO':"red", 'Submission':"white", 'Decision': "darkgrey",'Other':"grey"}

#introduce the figure
fig, ax = plt.subplots()

#Define the updating function in each frame
def update(year, data, colours_dict):

    #sort and clean data
    data_year = data[data["Year"]==year].sort_values(by = "percent", ascending = False)
    data_legend = data_year["new"] + data_year["percent"].apply(lambda x: " " + str(np.round(x * 100, 1)) + "%")
    #extract the correct colours
    colours = data_year["new"].map(colours_dict)
    #Clear the canvas
    ax.clear()
    #center the image
    ax.axis('equal')
    #Retrieve the percentages
    percentages = data_year["percent"]*100
    #year as string
    str_year = "Year: " +str(year)
    #Create piechart
    ax.pie(percentages, colors=colours, shadow = True, startangle=140, wedgeprops={"edgecolor":"k",'linewidth': 3, 'antialiased': True})
    #set title
    ax.set_title("Match outcome over time (1993-2020) ", loc = "center")
    # draw circle (to make it a donut
    centre_circle = plt.Circle((0, 0), 0.50, fc='white', linewidth=3, color = "black")
    fig.gca().add_artist(centre_circle)
    #Add total fights to center of the circle
    sum_str = 'Total fights = ' + str(sum(data[data["Year"]==year]["occurances"]))
    ax.text(0., 0., sum_str, horizontalalignment='center', verticalalignment='center', fontsize = 12)
    #Add year to the plot
    ax.text(1.5, 0, str_year, horizontalalignment='center', verticalalignment='center', fontsize = 15)
    #Add legend to the plot
    plt.legend(labels=data_legend, bbox_to_anchor=(1,0.95))
    #change margins of the plot
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.7)
ani = animation.FuncAnimation(fig, update, frames=yearly["Year"].unique(), repeat=True, fargs = [yearly, colours_dict], interval = 1500)

writer = animation.FFMpegWriter(fps=1)

#Save animation
ani.save('./Data/Fight_endings_over_time.mp4', writer = writer)
plt.show()

