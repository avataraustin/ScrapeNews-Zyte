import scrapy
import time
import random
import csv
import os
import scrapy_zyte_api

'''
This version was adjusted until it yielded proper data, may need further adjustment to store properly in csv and also possible that news site will change tags rendering selector code obsolete until reupdated. 
'''

# ZYTE_API_KEY = os.environ['ZYTE_API_KEY']



#import the CrawlerProcess for following links
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


def scrape_top_news():
  '''
  Runs a script to scrape top news stories from stored link
  and store them in a csv file. Contains built in timers to slow 
  down the scraping process (may take a while to fully execute)

  Args = None

  result stored in "stored_articles.csv"
  '''
  
  top_news = "https://apnews.com/hub/ap-top-news"
  #holder lists for packaging later 
  
  news_story_links = []
  news_titles = []
  news_story_body = []
  
  class NewsScraper(scrapy.Spider):
    name = "news_scraper"
  ###test
    def start_requests(self):
      yield scrapy.Request(
        url = top_news,
        meta={
          "zyte_api_automap": True,
        },
        callback = self.parse1)
  
    #first parsing method to gather the links
    def parse1(self, response):
      ##### NEED TO ADJUST SELECTORS BELOW TO PROPERLY CHOOSE ON WEBSITE
      top_news_links = response.css('a[href^="https://apnews.com/article"]::attr(href)').getall()
     
      #scrape only the first 5 top news links
      for story in top_news_links[0:5]: #was called url
        
        # appending to a list to work with later
        news_story_links.append(story)
        yield response.follow(url = story, callback = self.parse2)
          
    # Second parsing method to process the next level in 
    def parse2(self, response):
      article_title = response.css('h1::text').extract()
      #time.sleep(random.randint(5,20)) #random time between
      news_titles.append(article_title) #storing title to work with
      news_body = response.css('body p::text').extract()
      #time.sleep(random.randint(5,20)) #random time between
      news_story_body.append(news_body)
   
  custom_settings = {
    'ZYTE_API_KEY': os.environ['ZYTE_API_KEY'],
    'DOWNLOAD_HANDLERS': {
      "http": "scrapy_zyte_api.ScrapyZyteAPIDownloadHandler",
      "https": "scrapy_zyte_api.ScrapyZyteAPIDownloadHandler",
    },
    'DOWNLOADER_MIDDLEWARES': {
      "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
    },
    'REQUEST_FINGERPRINTER_CLASS':  "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",
    'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    #'ZYTE_API_TRANSPARENT_MODE': True,
    'DOWNLOAD_DELAY': 5.5
  }      


  settings = Settings(custom_settings)
  #run the spider:
  process = CrawlerProcess(settings)
  process.crawl(NewsScraper)
  process.start()
  
  #print values for debugging
  print(news_story_links)
  print(news_titles)
  print(news_story_body)

  
  #zipping together the stored lists of link,title,body
  zipped_news = zip(news_story_links, news_titles, news_story_body)
  
  #store in a gathered data in csv:
  with open('stored_articles.csv', 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(['Link', 'Title', 'Body']) # write header row
      writer.writerows(zipped_news) # write data rows

if __name__ == "__main__":
  scrape_top_news()