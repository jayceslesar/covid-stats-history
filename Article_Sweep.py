import json
import re
import requests
from difflib import SequenceMatcher
import pandas as pd
import urllib3
from pathlib import Path
from datetime import date
import datetime
import lxml.html


def lowerize(words:list) -> list:
    lowered = [w.lower() for w in words]
    return lowered


# used to tell how similar to strings are
def similar(a:str, b:str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# searches the title words and keywords list provided to ween out titles
def find_relevant_titles(title:str, keywords:list, bad_keywords:list) -> bool:
    title = title.lower()
    title_split = title.split()
    keywords = lowerize(keywords)
    bad_keywords = lowerize(bad_keywords)
    title_split = lowerize(title_split)
    for w in good_keywords:
        if w in title:
            return True
    for w in bad_keywords:
        if w in title:
            return False
    return True
    # n = len(keywords)
    # title_n = len(title.split())


# class to organize data and run everything
class Article_Sweep:
    # initializer
    def __init__(self, keywords:list, bad_keywords:list, auto_params:list, manual_params:list):
        # date formatting to get the right URL
        today = date.today()
        d2 = today.strftime("%B %d %Y").split()
        if d2[1][0] == '0':
            day = d2[1][1:]
        else:
            day = d2[1]
        self.DATE = day + d2[0] + d2[2]
        yesterday = date.today() - datetime.timedelta(days=1)
        d2 = yesterday.strftime("%B %d %Y").split()
        if d2[1][0] == '0':
            day = d2[1][1:]
        self.DATE_YESTERDAY = day + d2[0] + d2[2]
        # self.CDC_LINK = 'https://www.cdc.gov/library/researchguides/2019novelcoronavirus/researcharticles.html'
        # self.CDC_PAPERS = 'https://www.cdc.gov'
        self.JSON_PAPERS = 'https://connect.medrxiv.org/relate/collection_json.php?grp=181'
        self.pubmed = None # TODO::this
        # others -> ?
        self.KEYPHRASES = keywords
        self.BAD_KEYWORDS = bad_keywords
        

        
        # parses the rxiv pre-release database
        def get_rxiv(self):
            self.words = ""
            # flag as known preprints
            # pings and gets the json object of daily info
            data = requests.get(self.JSON_PAPERS).json()
            # search each title
            for paper_data in data["rels"]:
                curr_title = paper_data["rel_title"]
                curr_match = {}
                # run the relevant function (function returns True or False)
                if find_relevant_titles(curr_title, self.KEYPHRASES, self.BAD_KEYWORDS):
                    try:
                        # if it is in english (python cant tell the difference between the two)
                        print(curr_title)
                        self.words += curr_title + ' '
                        # if it can print -> pull data
                        curr_match["title"] = curr_title
                        curr_match["link"] = paper_data["rel_link"]
                        curr_match["date"] = None
                    except:
                        continue
                    # break
                    
                    # self.todays_matches.append(curr_match)

        def get_pubmed(self):
            # TODO::this week add
            pass

        # actualy run both functions
        get_rxiv(self) # TODO::get all auto variables -> clean up bad words
