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
        self.collection = db['daily_programmer']

    def get_collection(self):
        return self.collection


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
        print("\n\n\n--------------------------------------------------------------------------------\n\n\n")
        # print(response.url)

        # Another Way ToExtract out the URL (from the title of the page itself)
        # for link in response.xpath(
        #         "//div[@id='siteTable']//div[@class='entry unvoted']/p[@class='title']/a/@href").extract():
        #     path = "https://www.reddit.com" + str(link)
        #     print(str(path))

        if PymongoClient().get_collection().find_one({"url": str(response.url)}) is None:
            # Extract Out the Question Content
            for data in response.xpath(
                    "//div[@id='siteTable']//div[@class='entry unvoted']//div[@class='md']").extract():

               if data is not None or data == "":
                    # string = re.sub('<[^<]+?>', '', str(data))   # will remove all html tags
                    string = self.remove_html_tags(str(data))

                    post = {
                        "url": str(response.url),
                        "problem": str(data)
                    }
                    print(post)
                    PymongoClient().get_collection().insert_one(post)
                    # Note:
                    # @____ (i.e. @href or @title) will look for that specific Attribute inside the a HTML block.
                    # // means look anywhere within the scope
                    # / means look one level down

    def remove_html_tags(self, string):
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
