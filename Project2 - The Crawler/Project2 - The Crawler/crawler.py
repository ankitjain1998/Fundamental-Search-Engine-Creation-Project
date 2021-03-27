#Comp Sci 121/Informatics 141
#Project 2 - The Crawler

#Team Members: Ankit Jain, Om Mungra, Insiya Gunja

import logging
import re
import os
from urllib.parse import urlparse
from urllib.parse import urljoin
from corpus import Corpus
from lxml import etree
from bs4 import BeautifulSoup
from collections import defaultdict
from io import StringIO

# Global Variables
logger = logging.getLogger(__name__)
dynamic_link_url = ''
num_of_dynamic_links = 0
domain = 'uci.edu'
subdomain_dict = defaultdict(int)
valid_set = set()
traps_set = set()
max_outlinks_url = ''
max_outlinks_num = 0
previous_num = 0

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """
    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        global domain
        global subdomain_dict
        global valid_set
        global max_outlinks_url
        global max_outlinks_num
        global previous_num
        
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))

            #To track maximum number of outlinks from a certain URL
            if max_outlinks_num < len(self.frontier) - previous_num:
                max_outlinks_num = len(self.frontier) - previous_num
                max_outlinks_url = url
            previous_num = len(self.frontier)
            
            url_data = self.fetch_url(url)
            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        self.frontier.add_url(next_link)

                        #To obtain links of valid downloaded/fetched links
                        valid_set.add('Fetched URL:\t{}\n'.format(next_link))

                        #To obtain subdomains and their frequencies
                        url_subdomain_index = next_link.index(domain)
                        subdomain = next_link[:(url_subdomain_index)]
                        if 'https' in subdomain:
                            subdomain = subdomain.strip('https://')
                        elif 'http' in subdomain:
                            subdomain = subdomain.strip('http://')
                        subdomain_dict[subdomain] += 1
                    else:
                        #To obtain the links of traps
                        traps_set.add('Trap:\t{}\n'.format(next_link))
                        
        #File Creation for Subdomain Tracking                
        subdomain_count_file = open("Subdomain Count.txt", "w")
        subdomain_count_file.write("Subdomain: \tCount\n")
        for subdomain in dict(subdomain_dict).keys():
            string_to_add = '{}\t{}\n'.format(subdomain[:-1], dict(subdomain_dict)[subdomain])
            subdomain_count_file.write(string_to_add)            
        subdomain_count_file.close()

        #File Creation for Subdomain Creation
        traps_file = open("Traps.txt", "w")
        traps_file.write("Trap: \tUrl\n")
        for trap in traps_set:
            traps_file.write(trap)
        traps_file.close()

        #File Creation for Fetched/Downloaded URLs
        fetched_file = open("Fetched URLs.txt", "w")
        fetched_file.write("Fetched: \tUrl\n")
        for fetched in valid_set:
            fetched_file.write(fetched)
        fetched_file.close()

        #File Creation for Maximum Outlinks Tracker
        max_file = open("Max Outlinks.txt", "w")
        max_file.write('URL with maximum outlinks: {}\n'.format(max_outlinks_url))
        max_file.write('Number of outlinks: {}'.format(max_outlinks_num))
        max_file.close()
        

    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """
        url_data = {
            "url": url,
            "content": None,
            "size": 0
        }
        corp_file_name = self.corpus.get_file_name(url) #Using Corpus method to get file_name associated with URL
        content = b'' #To initialize binary content
        for data in open(corp_file_name, mode = 'rb'):
            content += data #To iterate through the data by opening the file
        if corp_file_name != None: #Updating the dictionary with newly obtained content and size of file
            url_data["content"] = content 
            url_data["size"] = os.path.getsize(corp_file_name)            
        return url_data

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        
        """
        try:
            outputLinks = []
            etree_parser = etree.parse(StringIO(url_data['content'].decode('utf-8')), etree.HTMLParser()) #Parsing through the content of the file and then decoded 
            for data in etree_parser.xpath("//@href"): #Getting data with 'href' so as to obtain the links
                to_append = data
                if bool(urlparse(data).netloc) == False: #To check if link is in absolute or relative form
                    to_append = urljoin(url_data["url"], data) #To convert relative form to absolute form 
                outputLinks.append(to_append)
        except:
            pass #To let errors pass
        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
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

