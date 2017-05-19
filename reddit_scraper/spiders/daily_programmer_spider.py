# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re

from pymongo import MongoClient


class PymongoClient():
    def __init__(self):
        client = MongoClient()
        client = MongoClient('mongodb://localhost:27017/')
        db = client['reddit_database']

        self.question_collection = db['daily_programmer']
        self.content_index_table_collection = db['content_index_table']
        self.title_index_table_collection = db['title_index_table']

    def get_question_collection(self):
        return self.question_collection
        
    def get_content_index_table_collection(self):
        return self.content_index_table_collection
    
    def get_title_index_table_collection(self):
        return self.title_index_table_collection
    
    def get_question_collection_count(self):
        return self.question_collection.count()


# This spider will grab all the questions on daily programmer and add them to a databse
class ProgrammerSpider(CrawlSpider):
    name = "dailyprogrammer"  # Spider Name - must be unique per spider
    allowed_domains = ["www.reddit.com"]  # Domain - set the scope of the crawler
    start_urls = ['https://www.reddit.com/r/dailyprogrammer/']
    # Start URLS is where the crawler will start and perform the rules
    # If there is more than 1 start URL, it will go in order
    rules = [
        # Rule #1
        Rule(LinkExtractor(
            allow=['/r/dailyprogrammer/comments/']),  # will look for links with thie format
            callback='parse_problem',  # calls this method whenever it gets a response from that url^
            follow=False),  # This will Go into the found website! but will not go any deeper
        # Rule #2
        Rule(LinkExtractor(
            allow=['/r/dailyprogrammer/\?count=\d*&after=\w*']),
            # \d is some number of digits, \w alpha characters and underscores
            # ^ Finds the pagination of the website
            callback='pagination',  # calls this method whenever it gets a response from that url^
            follow=True)  # will infinitely go into "depth" of the website
        # This will go through even pagination button "next page"
    ]




    # Callback method for a found link
    # This will retrieve the information from the specific site from Rule #1
    def parse_problem(self, response):
        print("\n--------------------------------------------------------------------------------\n")
        # print(response.url)

        # Another Way ToExtract out the URL (from the title of the page itself)
        # for link in response.xpath(
        #         "//div[@id='siteTable']//div[@class='entry unvoted']/p[@class='title']/a/@href").extract():
        #     path = "https://www.reddit.com" + str(link)
        #     print(str(path))

        if re.search("challenge_" , str(response.url)) and PymongoClient().get_question_collection().find_one({"url": str(response.url)}) is None:
            # Extract Out the Question Content
            for data in response.xpath(
                    "//div[@id='siteTable']//div[@class='entry unvoted']//div[@class='md']").extract():

               if data is not None or data != "":
                    print str(response.url)
                    #############################################################
                    # Get Web View String
                    web_view_string = str(data)
                    print "Successfully Got Web View String"
                    try:
                        web_view_string= web_view_string.replace('\n','')
                        web_view_string= re.sub('<h1>[Credit|Finally](.*)</div>','</div>',web_view_string)
                    except Exception, e:
                        print "Error: ", e
                    #############################################################
                    # Get Description String
                    description = re.findall('<p>(.*?)</p>', web_view_string)
                    try:
                        description = description[0]+description[1] + description[2]
                    except:
                        description = description[0]
                    print "Successfully Got Problem Description"
                    
                    ##############################################################
                    # Get Link ID
                    try:
                        post_id = PymongoClient().get_question_collection_count()
                    except:
                        post_id = 0
                    if post_id is None:
                        post_id = 0
                    print "Successfully Got ID"
                    
                    #############################################################
                    # Get Difficulty, Title, and Update Title Index Table
                    split = str(response.url).split('_')
                    difficulty = split[3]
                    title = ''
                    for i in range(4, len(split) ):
                        split[i] = re.sub(r'\W+', '', split[i])
                        title = title + ' ' + split[i]
                    title = title[1:]    
                    print difficulty
                    print title

                    try:
                        title_index_table = PymongoClient().get_title_index_table_collection().find()[0]
                        print 'Opened Title Index Table'
                    except:
                        title_index_table = {}
                        title_index_table['id']= 'title_index_table'
                        print "Failed to Open Title Index Table: Created New"
                    split = title.lower().split(' ')
                    string_set = set(split)
                    string_set.discard('id')
                    print string_set
                    try:
                        for word in string_set:
                            if word in title_index_table:
                                title_index_table[str(word)] = title_index_table[str(word)] + ',' + str(post_id)
                            else:
                                title_index_table[str(word)] = str(post_id)
                    except Exception, e:
                        print 'Error:',e
                    try:
                        PymongoClient().get_title_index_table_collection().delete_many({'id':'title_index_table' })
                        print 'Deleted Title Index Table'
                    except:
                        print 'No Title Index Table to Delete'
                    PymongoClient().get_title_index_table_collection().insert_one(title_index_table)   
                    print 'Sucessfully Updated Title Index Table'
                    
                    ############################################################
                    # Update Content Index Table
                    try:
                        content_index_table = PymongoClient().get_content_index_table_collection().find()[0]
                        print 'Opened Content Index Table'
                    except:
                        content_index_table = {}
                        content_index_table['id']= 'content_index_table'
                        print "Failed to Open Content Index Table: Created New"
                    split = description.lower().split(' ')
                    for i in range (0, len(split)):
                        split[i] = re.sub(r'\W+', '', split[i])
                    string_set = set(split)
                    string_set.discard('id')
                    # index_table = PymongoClient().get_index_table_collection
                    for word in string_set:
                        if len(word) > 15 or any(str.isdigit(c) for c in word):
                            continue
                        if word in content_index_table:
                            content_index_table[str(word)] = content_index_table[str(word)] + ',' + str(post_id)
                        else:
                            content_index_table[str(word)] = str(post_id)
                    try:
                        PymongoClient().get_content_index_table_collection().delete_many({'id':'content_index_table' })
                        print 'Deleted Content Index Table'
                    except:
                        print 'No Content Index Table to Delete'
                    PymongoClient().get_content_index_table_collection().insert_one(content_index_table)   
                    print 'Sucessfully Updated Content Index Table'
                                 
                    ############################################################
                    # Creating Post 
                    post = {
                        "id" : post_id,
                        "url": str(response.url),
                        "difficulty": difficulty,
                        "title": title,
                        "webview": web_view_string
                    }
                    print(post)                    
                    PymongoClient().get_question_collection().insert_one(post)
                    # Note:
                    # @____ (i.e. @href or @title) will look for that specific Attribute inside the a HTML block.
                    # // means look anywhere within the scope
                    # / means look one level down

    def clean_string(self, string):
        return re.sub('<[^<]+?>', '', string)   # will remove all html tags

    def custom_remove_html_tags(self, string):
        string = re.sub('<code>', '', string)
        string = re.sub('</code>', '', string)
        string = re.sub('<p>', '', string)
        string = re.sub('</p>', '', string)
        string = re.sub('<strong>', '', string)
        string = re.sub('</strong>', '', string)
        string = re.sub('<div class="md">', '', string)
        string = re.sub('</div>', '', string)
        string = re.sub('<pre>', '', string)
        string = re.sub('</pre>', '', string)
        string = re.sub('<h1>', '', string)
        string = re.sub('</h1>', '', string)
        string = re.sub('<h2>', '', string)
        string = re.sub('</h2>', '', string)
        string = re.sub('<h3>', '', string)
        string = re.sub('</h3>', '', string)
        string = re.sub('<ul>', '', string)
        string = re.sub('</ul>', '', string)
        string = re.sub('<li>', '', string)
        string = re.sub('</li>', '', string)
        string = re.sub('<em>', '', string)
        string = re.sub('</em>', '', string)
        string = re.sub('<ol>', '', string)
        string = re.sub('</ol>', '', string)
        string = re.sub('<br>', '', string)
        string = re.sub('<blockquote>', '', string)
        string = re.sub('</blockquote>', '', string)

        # NOTE <sup> = to the power up
        # NOTE <Table> = a table

        return string

    # Callback method for a pagination link
    def pagination(self, response):

        print("------------------------next-------------------------")
