# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 15:17:56 2020

Reference: https://www.youtube.com/watch?v=3fcKKZMFbyA&ab_channel=RedEyedCoderClub
"""

# Packages
from time import sleep
import requests
import re # For expression
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  
from matplotlib.dates import DateFormatter # For formatting the xticks and yticks
from datetime import datetime # For getting current time as file name
import pytz # For switiching the timezone of data from UTC to HKT

# Read Website function
def get_website(url):
    resp=requests.get(url)
    if resp.status_code==200:
        print('[HTTP requested successfully]')
    else:
        print('Something wrong happened, the HTTP Status Code is: ',resp.status_code)
    return(BeautifulSoup(resp.text,'lxml'))

# (Part 1.2) General Report - Logged-in player statistics
def statistics_login(stat_url):
   
    # Readin the user data
    df1=pd.read_json(stat_url)
    [data]=df1["data"].to_list()
    df2=pd.DataFrame(data, columns=["Time","Number of Users"])
    
    # Get rid of the extra zero of the UNIX time
    df2["Time"]=df2["Time"]/1000
    df2["Time"]=df2["Time"].astype(np.int64)
    
    # Conver UNIX time to readable date time format
    df2['Time'] = pd.to_datetime(df2['Time'],unit='s')
    df2["Time"]=df2["Time"].dt.tz_localize('utc').dt.tz_convert('Asia/Hong_Kong')
    
    # Plot the main graph
    fig = plt.figure(figsize=(8.0, 5.0))
    ax = plt.subplot()
    ax.plot_date(df2['Time'], df2['Number of Users'], '.r-')
    ax.xaxis.set_major_formatter(DateFormatter('%D %H:%M'))
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))
    plt.xticks(rotation=45)
    plt.title('Number of users logged into Steam at Time')
    plt.xlabel('Date & Time')
    plt.ylabel('Number of users logged into Steam')
    plt.grid(True)
    
    # For current time as file name
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y")
    
    plt.savefig('stat_login('+current_time+').png',bbox_inches='tight')
    plt.show()
    print ("Log-in statistic graph generated successfully.")

# (Part 1.1) General Report - Current gaming statistics
def statistics_game(stat_url):
    
    # Variables
    playernum=[]
    gamelist=[]
    
    # Read the website & Append to dataframe
    url="https://store.steampowered.com/stats/"
    soup = get_website(url)

    # Retrieve the line of player count
    rows = soup.find_all('tr', {'class': "player_count_row"})
    for row in rows:
        # Obtain the player count
        playernum.append(int(row.findAll("td")[0].text[1:-1].replace(',', '')))
        # Obtain the game playing
        gamelist.append(row.findAll("td")[3].text[1:-1])
    data={"Number of current players":playernum,"Name of game":gamelist}
    df1=pd.DataFrame(data)
    
    # Plot the main graph
    fig = plt.figure(figsize=(8.0, 5.0))
    ax = plt.subplot()
    ax.bar(df1["Name of game"][:10],df1["Number of current players"][:10])
    plt.xticks(rotation=90)
    plt.title('Top 10 games by current players')
    plt.xlabel('Name of game')
    plt.ylabel('Number of current players')
    plt.grid(True)
    
    # For current time as file name
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y")
    
    # Save the plot figure
    plt.savefig('stat_game('+current_time+').png',bbox_inches='tight')
    plt.show()
    print ("Game statistic graph generated successfully.")
    
def game_search(search_name):
    
    # Variables
    gameid=[]
    title=[]
    released=[]
    reviews=[]
    gametype=[]
    
    url = "https://store.steampowered.com/search/results/?query&start=0&count=50&dynamic_data=&term="+search_name+"&infinite=1"
    soup=get_website(url)
    games=soup.find_all("a")
    
    # Get all gameids
    for game in games:
        if game!= None:
            gameid.append(game.get("data-ds-appid"))
    # Get rid of nonetype data to prevent error
    gameid=[x[2:-2] for x in gameid if x is not None]
    
    print("Loading ... Please Wait")
    
    # Loop through the game ids collected
    for id in gameid:
        
        url = f"https://store.steampowered.com/apphoverpublic/{id}"
        resp = requests.get(url)

        soup=BeautifulSoup(resp.text,'lxml')
    
        # Get the title of the game
        try:
            title.append(soup.find("h4", class_="hover_title").text.strip())
        except:
            title.append("")
        
        # Get the releasing date of the game
        try:
            released.append(soup.find("div", class_="hover_release").span.text.strip())
        except:
            released.append("")
        
        # Get the reviews of the game
        try:
            reviews.append(soup.find("div", class_="hover_review_summary").span.text.strip())
        except:
            reviews.append("")
        
        # Get the type/genre of the game
        try:
            gametype.append(soup.find("div", class_="app_tag").text)
        except:
            gametype.append("") 

    # Combine lists into dictionary
    dic={"Name of game":title,"Release date":released,"Review":reviews,"Genre":gametype}
    
    # Create dataframe with dictionary created
    df_game=pd.DataFrame(dic)
    
    # Output
    df_game.to_csv('GameSearch_('+search_name+').csv',encoding='utf_8_sig')
    print ('Search CSV file generated successfully')

# Main function to control the different parts of the project
def main():
    
    # (Part 1.1) General Report - Current gaming statistics
    # Link for Current gaming statistics
    stat_game_url="https://store.steampowered.com/stats/"
    statistics_game(stat_game_url)
    
    # (Part 1.2) General Report - Logged-in player statistics
    # Link for Logged-in player statistics
    stat_login_url="https://store.steampowered.com/stats/userdata.json"
    statistics_login(stat_login_url)

    print ("\nDo you want to search for games? \n")
    Choice = input ("Y Yes\nN No \n")
    if Choice == "Y":
        SearchName = input ("Please input keyword to search for game: (e.g. football)\n")
        game_search(SearchName)
    print ("Goodbye! Thanks for using!")
    

if __name__ == "__main__":
    main()
    