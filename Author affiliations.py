# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 11:22:05 2018

@author: WillsO
"""

import re
import pandas as pd
from bs4 import BeautifulSoup
import requests

class PubMedObject(object):
    soup = None
    url = None

    # pmid is a PubMed ID
    # url is the url of the PubMed web page
    # search_term is the string used in the search box on the PubMed website
    def __init__(self, pmid=None, url='', search_term=''):
        if pmid:
            pmid = pmid.strip()
            url = "http://www.ncbi.nlm.nih.gov/pubmed/%s" % pmid
        if search_term:
            url = "http://www.ncbi.nlm.nih.gov/pubmed/?term=%s" % search_term
        page = requests.get(url).text
        self.soup = BeautifulSoup(page, "html.parser")

        # set the url to be the fixed one with the PubMedID instead of the search_term
        if search_term:
            try:
                url = "http://www.ncbi.nlm.nih.gov/pubmed/%s" % self.soup.find("dl",class_="rprtid").find("dd").text
            except AttributeError as e:  # NoneType has no find method
                print("Error on search_term=%s" % search_term)
        self.url = url

    def get_title(self):
        return self.soup.find(class_="abstract").find("h1").text

    #auths is the string that has the list of authors to return
    def get_authors(self):
        result = []
        author_list = [a.text for a in self.soup.find(class_="auths").findAll("a")]
        for author in author_list:
            lname, remainder = author.rsplit(' ', 1)
            #add periods after each letter in the first name
            fname = ".".join(remainder) + "."
            result.append(lname + ', ' + fname)

        return ', '.join(result)
    
    
    def get_institution(self):
        """Identifies instituional affiliations for list of PMIDs"""
        result = []
        try:
            author_institution = [a.text for a in self.soup.find(class_="ui-ncbi-toggler-slave").findAll("dd")]
            l, result = [], []
            for institution in author_institution:
                x = institution.lower().split(',')
                l.append(x)
            for list in l:
                #print(list)
                s = 0
                #Identifies institution name in pubmed author acknowledgement
                for elem in list:
                    if 'university' in elem:
                        if s >= 1:
                            result = result[:-1]
                            result.append(elem)
                            s+=1
                            break
                        else:
                            result.append(elem)
                            s+=1
                            break
                    elif 'institute' in elem:
                        if s >=1:
                            continue
                        else:
                            result.append(elem)
                            s+=1
                    elif 'center' in elem:
                        if s>=1:
                            continue
                        else:
                            result.append(elem)
                            s+=1    
                if s == 0:
                    result.append(list[1])
                        
        except AttributeError:
            result.append("Institutions not available")

        return result


    def get_citation(self):
        return self.soup.find(class_="cit").text

    def get_external_url(self):
        url = None
        doi_string = self.soup.find(text=re.compile("doi:"))
        if doi_string:
            doi = doi_string.split("doi:")[-1].strip().split(" ")[0][:-1]
            if doi:
                url = "https://doi.org/%s" % doi
        else:
            doi_string = self.soup.find(class_="portlet")
            if doi_string:
                doi_string = doi_string.find("a")['href']
                if doi_string:
                    return doi_string

        return url or self.url
    
def load_file(filename):
    pmid_file = open(filename, 'r')
    result = []
    for line in pmid_file:
        result.append(line.strip())
    pmid_file.close()
    return result

def write_to_excel(d):
     df = pd.DataFrame.from_dict(d, orient = 'index')
     df.to_csv('mycsvfile.csv')


def scrape_authors(filename):
    pmidList = load_file(filename)
    institutions = {}
    #l = []
    for pmid in pmidList:

        x = PubMedObject(pmid)
        institutions[pmid] = x.get_institution()
    write_to_excel(institutions)
    return print(institutions)

#Amend pmids.txt to file name with list of PMIDs 
scrape_authors('pmids.txt')

