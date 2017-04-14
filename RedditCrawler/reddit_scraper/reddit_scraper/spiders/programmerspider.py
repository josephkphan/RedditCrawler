# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy


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

        print(response.url)

        # Another Way ToExtract out the URL (from the title of the page itself)
        # for link in response.xpath(
        #         "//div[@id='siteTable']//div[@class='entry unvoted']/p[@class='title']/a/@href").extract():
        #     path = "https://www.reddit.com" + str(link)
        #     print(str(path))

        # Extract Out the Question Content
        for data in response.xpath("//div[@id='siteTable']//div[@class='entry unvoted']//div[@class='md']").extract():
            print(data)
            # Note:
            # @____ (i.e. @href or @title) will look for that specific Attribute inside the a HTML block.
            # // means look anywhere within the scope
            # / means look one level down

    # Callback method for a pagination link
    def pagination(self, response):
        print("------------------------next-------------------------")
