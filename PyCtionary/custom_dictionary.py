#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    File name: custome_dictionary.py
    Author: Salah Hamza
    Date created: --/08/2017
    Date last modified: 01/02/2018
    Python Version: 2.7
'''



from bs4 import BeautifulSoup
import requests, enchant, re, wikipedia
from difflib import SequenceMatcher



def _get_soup_object(url,parser="lxml"):
    """ returns instance of class BeautifulSoup (soup object)"""
    return BeautifulSoup(requests.get(url).text,parser)

class Custom_dictionary(object):
    def __init__(self,word_dict=enchant.Dict("en_US")):
        self.Dict = word_dict

    def suggested_terms(self,term):
        """ function returns a list of suggested words (uses PyEnchant)"""
        return self.Dict.suggest(term)
    
    
    def meaning(self,term, disable_errors=False):
        if len(term.split()) > 1:
            message = "A Term must be only a single word."
            return message
        else:
            try:
                if self.Dict.check(term)==False:
                    sugg_terms = self.get_top_sugg(self.Dict.suggest(term))
                    if sugg_terms:
                        return sugg_terms
                    else:
                        return "Nothing was found."
                html = _get_soup_object(
                        "http://wordnetweb.princeton.edu/perl/webwn?s={0}".format(term))
                types = html.findAll("h3")
                length = len(types)
                lists = html.findAll("ul")
                out = {}
                for a in types:
                    reg = str(lists[types.index(a)])
                    meanings = []
                    for x in re.findall(r'\((.*?)\)', reg):
                        if 'often followed by' in x:
                            pass
                        elif (len(x) > 5 or ' ' in str(x)):
                            meanings.append(x)
                    name = a.text
                    out[name] = meanings
                return out
            except Exception as e:
                if disable_errors == False:
                    #err = "Error: The Following Error occured: {}".format(e)
                    message = "Nothing was found."
                    return message

    
    
    def suggest_subject(self,term):
        """
            returns:
                - checks if one of the words is misspelled then returns a suggested turm
        """
        return " ".join([self.Dict.suggest(word)[0] for word in term.split()])




    def get_page(self,term):
        """
            returns:
                - returns page object of term
        """
        return wikipedia.page(term)



    def wikipedia_summary(self,term):
        """
            returns:
                - page object of term if page exists in wikipedia
                - suggestions if page does not exists in wikipedia
                - None if neither
        """
        suggs = wikipedia.search(term.capitalize())
        if suggs:
            if term.lower() in [s.lower() for s in suggs]:
                try:
                    return self.get_page(term.capitalize())
                except wikipedia.exceptions.DisambiguationError:
                    err = "Ambiguous flag::  {} may refer to many subject.".format(term)
                    if term.capitalize() in suggs:
                        suggs.pop(suggs.index(term.capitalize()))
                    return (err,suggs)
            else:
                return suggs[:5]
        else:
            return None


    @staticmethod
    def synonym(term, formatted=False):
        try:
            data = _get_soup_object("http://www.thesaurus.com/browse/{0}".format(term))
            terms = data.select("div#filters-0")[0].findAll("li")
            if len(terms) > 5:
                terms = terms[:5:]
            li = []
            for t in terms:
                li.append(t.select("span.text")[0].getText())
            if formatted:
                return {term: li}
            return li
        except:
            return ["No synonyms."]

    @staticmethod
    def antonym(word, formatted=False):
        data = _get_soup_object("http://www.thesaurus.com/browse/{0}".format(word))
        try:
            terms = data.select("section.antonyms")[0].findAll("li")
            if len(terms) > 5:
                terms = terms[:5:]
            li = []
            for t in terms:
                li.append(t.select("span.text")[0].getText())
            if formatted:
                return {word: li}
            return li
        except:
            try:
                terms = data.find("section",class_="container-info antonyms")
                term = terms.find_all("li")
                li = []
                for tag in term:
                    li.append(tag.getText())
                return li
            except:
                return ["No antonyms"]





    @staticmethod
    def get_top_sugg(suggestions):
        l = []
        for word in suggestions:
            if " " not in word:
                l.append(word)
        return l

    #these two methods are not used for now but they might be included
    #later for better search results
    @staticmethod
    def match_ratio(term,sugg_term):
        t = SequenceMatcher(lambda x: x==" ",term,sugg_term)
        return t.ratio()

    @staticmethod
    def best_match(term,sugg_terms):
        match_dict = dict((match_ratio(term,sugg_term),sugg_term) for
                sugg_term in sugg_terms)
        return match_dict[max(match_dict)]
        

