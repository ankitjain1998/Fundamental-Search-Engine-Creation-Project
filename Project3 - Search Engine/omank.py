#PROJECT 3: COMPLETE SEARCH ENGINE

#NAME: ANKIT JAIN, OM RAMNIK MUNGRA
#ID: 96065117, 72248203

#INDEXER AND SEARCH RETRIVAL MODULE
#IMPORTED MODULES
import json
import pymongo
import sys
import re
import os
from collections import defaultdict
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
#nltk.download('stopwords')
from mongoengine import *
import math
from urllib.parse import urlparse

#GLOBAL VARIABLES
RAW_FOLDER_NAME = "WEBPAGES_RAW"
dynamic_link_url = ''
num_of_dynamic_links = 0

#JSON FILE HANDLING
file_name = '{}/{}'.format(RAW_FOLDER_NAME,"bookkeeping.json")
file = open(file_name, "r")
json_data = json.load(file)
file.close()

class TokenDictionary:
    '''
    Class is initialized by a string to be tokenized
    '''
    def __init__(self, text_string:str):
        self.text = text_string.lower()
        self.result = None 

    def get_token_dictionary(self):
        '''
        Token dictionary is obtained by mean iterating through
        the words matching the regex function and words which 
        are not stop words[obtained from nltk library] and then 
        added to a default dictionary which records the frequencies
        of the occurences of the words
        '''
        try:
            self.result = defaultdict(int)
            non_tokens = list(stopwords.words('english'))
            non_tokens.extend(["\n", "\t", " ", ""])
            compiler = re.compile(r'\W+|_')
            u_line = compiler.sub(' ', self.text)
            for word in u_line.split():
                if word not in non_tokens:
                    self.result[word.lower()] += 1
            return dict(self.result)
        except:
            return dict()

class URLSoup:
    '''
    Class is used to store the BeautifulSoup object
    and title of the url separately to be used and 
    is initialized by the path and url
    '''
    def __init__(self, path, url):
        self.url = url
        self.path = path
        
    def get_soup(self):
        #To get the soup object
        return BeautifulSoup(open('WEBPAGES_RAW/{}'.format(path)).read(), 'html.parser')
    
    def get_title(self):
        #To get the URL title to be used
        try:
            url_soup = self.get_soup()
            return url_soup.title.get_text()
        except AttributeError:
            result = ''
            return result

class URLData(Document):
    #Extension of Document class offered by mongoengine
    #Used to store data available in the urls 
    document_id = StringField()
    url = StringField()
    title = StringField()
    token_dictionary = MapField(IntField())
    num_of_tokens = IntField()
	
def save_data(path,web_url,webpage_title,frequencies):
    #Function is used to save new or updated data based on
    #the entries of path, url, title and frequencies entered
    if (URLData.objects(document_id = path).count() == 0):
        #In case document is new
        data_object = URLData(document_id = path, url = web_url, title = webpage_title, token_dictionary = frequencies, num_of_tokens = len(frequencies.keys()))
    else:
        #In case document is already existing and needs to be updated
        data_object = URLData.objects(document_id = path).first()
        for key in frequencies.keys():
            data_object.token_dictionary[key] += frequencies[key]
    data_object.save()

class WeightedDictionary:
    #EXTRA CREDIT
    #Class is used to weight different elements of the url data
    #based on whether it is occuring in title, header or body
    #Title is weighed highest, then header and then finally body
    def __init__(self):
        self.weights = {'title_weight':9, 'header_weight':6, 
                        'body_weight':3}
        self.token_weights = defaultdict(int)
        self.body_tokens = dict()
        self.title_tokens = dict()
        self.header_tokens = dict()
    
    def get_title_tokens(self, soup):
        #To get all tokens in the title
        try:
            title_text = soup.find('title').get_text()
            self.title_tokens = TokenDictionary(title_text).get_token_dictionary()
            if self.title_tokens == None:
                self.title_tokens = dict()
        except AttributeError:
            self.title_tokens = dict()
    
    def get_header_tokens(self, soup):
    #To get all tokens in the header
	#Source: https://stackoverflow.com/questions/45062534/how-to-grab-all-headers-from-a-website-using-beautifulsoup	
        try:
            header_text = ''
            for header in (soup.find_all(re.compile('^h[1-6]$'))):
                header_text += str(header.get_text())
            self.header_tokens = TokenDictionary(header_text).get_token_dictionary()
            if self.header_tokens == None:
                self.header_tokens = dict()
        except AttributeError:
            self.header_tokens = dict()
            
    def get_body_tokens(self, soup):
        #To get all tokens in the body
        try:
            body_text = soup.find('body').get_text()
            self.body_tokens = TokenDictionary(body_text).get_token_dictionary()
            if self.body_tokens == None:
                self.body_tokens = dict()
        except AttributeError:
            self.body_tokens = dict()
	
    def get_token_weights(self, soup, token_dictionary):
        #To assign weights based on where they are occuring
        self.get_title_tokens(soup)
        self.get_header_tokens(soup)
        self.get_body_tokens(soup)
        for key in list(token_dictionary.keys()):
            if key in list(self.body_tokens.keys()) and self.body_tokens != dict():
                self.token_weights[key] += self.weights['body_weight']
            if key in list(self.header_tokens.keys()) and self.header_tokens != dict():
                self.token_weights[key] += self.weights['header_weight']
            if key in list(self.title_tokens.keys()) and self.title_tokens != dict():
                self.token_weights[key] += self.weights['title_weight']
        return dict(self.token_weights)

class SearchData(Document):
    #Extension of Document class offered by mongoengine
    #Used to store data available in the queries 
    search_query = StringField()
    tf_idf_query = MapField(IntField())

def save_query(query,score, document_id):
    #Function is used to save new or updated data based on
    #the query itself, its score and document id
    if (SearchData.objects(search_query = query).count() == 0):
        #For new queries
        query_object = SearchData(search_query = query)
        query_object.tf_idf_query[document_id] = score 
    else:
        #For pre-existing or updating queries
        query_object = SearchData.objects(search_query = query).first()
        query_object.tf_idf_query[document_id] = score
    print("Query Object Name: ", query_object.search_query) 
    query_object.save()
    
def update_search_tf_idf(corpus_size):
    #To get the score for the different query tokens
    #Formula is from lecture slides
    object_num = 0
    search_lists = list(SearchData.objects)
    for object in search_lists:
        object_num += 1
        for key in list(object.tf_idf_query.keys()):
            document_id = key
            frequency = object.tf_idf_query[key]
            tf_idf_score_1 = (1 + math.log(frequency))
            tf_idf_score_2 = (math.log(corpus_size/len(object.tf_idf_query)))
            object.tf_idf_query[key] += (tf_idf_score_1)*(tf_idf_score_2)
        object.save()
    #print(object_num)
    
def locate_query(to_find):
    #To find a query based on the query entered and its score
    try:
        result = SearchData.objects.get(search_query = to_find)
    except MultipleObjectsReturned:
        result = result.first()
    except DoesNotExist:
        return dict()
    return result.tf_idf_query

def url_finder(hits):
    #To get all urls associated with the document ids as per the 
    #list of possible matching hits entered
    urls = []
    for key in hits.keys():
        associated_url = URLData.objects.get(document_id = key)
        urls.append({'url':'https://{}'.format(associated_url.url), 'title':associated_url.title})
    return urls

def processing(search_query_dict):
    #Processes the search query dictionary
    #entered by the user which is the tokenized
    #dictionary of the search query and weighted as well
    if len(search_query_dict) > 1:
        score_dictionary = defaultdict(int)
        for query in search_query_dict.keys():
            try:
                for id in SearchData.objects.get(search_query = query).tf_idf_query.keys():
                    incrementer = score_dictionary[id] 
                    score_dictionary[id] += incrementer
            except DoesNotExist:
                return None
        result = score_dictionary
    else:
        if len(search_query_dict) == 0:
            raise EmptyQueryError
        else:
            for query in search_query_dict.keys():
                result = locate_query(query) #To get score
    result = dict(sorted(result.items(), key = lambda x: x[1], reverse = True)) #To sort on the basis of the score
    return url_finder(result)

def is_valid(url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method

        From Project #2
        """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if len(parsed.geturl()) > 100: #Accounting for arbitrary length of invalid url which is 100 characters
            return False
        try:
            if re.match(r"^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$", parsed.path.lower()) == None:
                #SOURCE: https://support.archive-it.org/hc/en-us/articles/208332963-Modify-your-crawl-scope-with-a-Regular-Expression
                #Checking for Repeating directories 
                checker = ".ics.uci.edu" in parsed.hostname \
                       and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                        + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                        + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                        + "|thmx|mso|arff|rtf|jar|csv" \
                                        + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())
                global dynamic_link_url
                global num_of_dynamic_links
                url_split = url.split('?') #To split the url on basis of presence of queries
                if checker == False:
                    return False
                if url_split[0] != dynamic_link_url: #To check for dynamic links as traps
                    dynamic_link_url = url_split[0] #Updating dynamic links
                    num_of_dynamic_links = 0 
                else:
                    if parsed.query != '': #Checking presence of queries in parsed url
                        num_of_dynamic_links += 1 #Iterating number of dynamic links if queries exist
                        if num_of_dynamic_links >= 20: #Overload of dynamic links signifies URL is a trap 
                            checker = False
                    else:
                        num_of_dynamic_links = 0 #Resetting number of dynamic links back to null   
                if 'calendar' in url and '?' in url: #Checking presence of queries for calender based links which are often deemed as traps
                    checker = False
                return checker #Checker returned based on whether it is True or False after checking for traps
            else:
                return False #Returning False in case of repeated directories which are often traps
        except TypeError:
            print("TypeError for ", parsed)
            return False

def get_results(query):
    '''
    To get results based on the token dictionary 
    of the search query and then print them in the approrpriate 
    format
    '''
    query_token_object = TokenDictionary(search_query)
    result = processing(query_token_object.get_token_dictionary())
    print("\nSearch Results:")
    rank = 0
    return_string = ''
    print("\nNumber of Results: {}".format(len(result)))
    for result_key in result[:20]:
        rank += 1
        return_string += 'Link {}: {}\n'.format(rank,result_key['url'])
    return return_string

class EmptyQueryError(Exception):
    '''To raise error when query is empty'''
    pass

if __name__ == "__main__":
    connect('load_everything10', host = 'localhost', port = 27017)
    
    #To upload the corpus data of the valid urls onto a database [MongoDB]
    #for path,path_url in json_data.items():
    #    url_added = 'https://{}'.format(path_url)
    #    if is_valid(str(url_added)) == True:
    #        soup_object = URLSoup(path,path_url)
    #        frequencies = TokenDictionary(soup_object.get_soup().get_text()).get_token_dictionary()
    #        save_data(path,path_url,soup_object.get_title(),frequencies)

    #To create the collection of queries from the different datas of url obtained
    # for item in URLData.objects:
    #     urls += 1
    #     print(urls)
    #     soup_object = BeautifulSoup(open('{}/{}'.format(RAW_FOLDER_NAME, item.document_id)).read(), 'html.parser')
    #     weighted_dict = WeightedDictionary().get_token_weights(soup_object, item.token_dictionary)
    #     for query in weighted_dict.keys():
    #         query_score = weighted_dict[query]
    #         save_query(query, query_score,item.document_id)
	
    # update_search_tf_idf(URLData.objects.count()) #To update tf_idf scores of all indexes

    search_query = input("Enter Query: ") #To get user input
    print(get_results(search_query)) #To get the results



