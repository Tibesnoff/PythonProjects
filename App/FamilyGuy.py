# import required modules
from operator import truediv
from bs4 import BeautifulSoup
import requests
import random

def episodeData(name, season, ep):
    return (f"Name: {name} \n S{season[7:-10]}E{ep}")

def hasChild(dif):
    if len(dif.find_all(["a"])) == 0:
            return dif.string
    return dif.find(["a"]).string


def getFamilyGuyEpisodes():
    page = requests.get("https://en.wikipedia.org/wiki/List_of_Family_Guy_episodes")

    soup = BeautifulSoup(page.content, 'html.parser')
    list(soup.children)

    episodes = list(filter(lambda x: x.find(class_="summary")!=None, soup.find_all(class_="vevent", style="text-align:center;background:inherit")))

    episodelist = [
        episodeData(
             str(hasChild(i.find(class_="summary"))),
             i.find_previous(["h3"]).find(class_="mw-headline").string, 
             i.find(["td"]).string
        )for i in episodes
    ]

    return episodelist[random.randrange(len(episodelist))]

print(f"Random Episode is:\n {getFamilyGuyEpisodes()}")
