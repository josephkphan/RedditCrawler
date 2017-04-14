# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re


class AnimeSpider(CrawlSpider):  # CrawlSpider let's you go into links on the page; Spider is 1 specific link
    name = "anime"  # Spider Name - must be unique per spider
    allowed_domains = ["www.reddit.com", "www.youtube.com", "streamable.com"]  # Domain - set the scope of the crawler
    start_urls = ['https://www.reddit.com/r/anime/']
    # Start URLS is where the crawler will start and perform the rules
    # If there is more than 1 start URL, it will go in order
    rules = [  # Sublink URL patterns
        # Rule #1 (individual sublinks)
        Rule(LinkExtractor(
            allow=['https://www.youtube.com/']),  # will look for links with this format
            callback='parse_youtube',  # calls this method whenever it gets a response from that url^
            follow=False),  # This will Go into the found website! but will not go any deeper

        Rule(LinkExtractor(
            allow=['https://streamable.com/']),
            callback='parse_streamable',
            follow=False),

        # Rule #2 (pages)
        Rule(LinkExtractor(
            allow=['/r/anime/\?count=\d*&after=\w*']),
            # \d is some number of digits, \w alpha characters and underscores
            # ^ Finds the pagination of the website
            callback='pagination',  # calls this method whenever it gets a response from that url^
            follow=True)  # will infinitely go into "depth" of the website
        # This will go through even pagentation button "next page"
    ]

    # Callback method for a found link
    # This will retreive the information from the specific site from Rule #1
    def parse_youtube(self, response):
        print("\n\n\n--------------------------------------------------------------------------------\n\n\n")
        for data in response.xpath("//div[@id='watch-headline-title']/h1/span/@title").extract():
            print(data)
        print(response.url)

    # Rule2 parse
    def parse_streamable(self, response):
        print("\n\n\n--------------------------------------------------------------------------------\n\n\n")
        for data in response.xpath("//div[@id='video-footer']/h1[@id]").extract():
            string = str(data)
            string = re.sub('\<h1 id="title">', '', string)
            string = re.sub('\</h1>', '', string)
            print(string)
        print(response.url)

    # Callback method for a pagination link
    def pagination(self, response):
        print("------------------------next-------------------------")

        # Only parse the first 2 pages
        if "50" in str(response):
            quit()
