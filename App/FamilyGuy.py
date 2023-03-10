# import required modules
from bs4 import BeautifulSoup
import requests
import random

def episodeData(name, season, ep):
    return "Name: " + name + "\n S" + season[7:-10] + "E" +ep

def hasChild(dif):
    if len(dif.find_all(["a"])) == 0:
        return dif.string
    return dif.find(["a"]).string

def getFamilyGuyEpisodes():
    page = requests.get("https://en.wikipedia.org/wiki/List_of_Family_Guy_episodes")

    soup = BeautifulSoup(page.content, 'html.parser')

    list(soup.children)

    episodes = soup.find_all(class_="vevent", style="text-align:center;background:inherit")

    episodelist = []

    for i in episodes:
        name = i.find(
            class_="summary")  # (lambda x: i.find(class_="summary").contents[0] if str(i.find(class_="summary").contents[0].string) else str(i.find(class_="summary")))
        name = hasChild(name)
        season = i.find_previous(["h3"]).find(class_="mw-headline").string
        episode = i.find(["td"]).string
        epdata = episodeData(str(name), season, episode)
        episodelist.append(epdata)
        #print(epdata)
    return episodelist[random.randrange(len(episodelist))]



print("Random Episode is:\n " + getFamilyGuyEpisodes() )
