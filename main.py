import scrapy
import time
import random
import csv

#Running this script will scrape top news from apnews and store in csv (will take a while to do this)

#import the CrawlerProcess for following links
from scrapy.crawler import CrawlerProcess


# link to current 'top news': https://apnews.com/hub/ap-top-news
# links are in an "a" tag where a class contains "Component 
# heading" and the href is then the link of the article
# Example: <a class="Component-headline-0-2-91" data-key="card-headline" href="/article/2024-republicans-subway-chokehold-death-be39b29eef4529bf996c13ec5bcd22ef"><h2 class="Component-heading-0-2-92 Component-headingMobile-0-2-93 -cardHeading undefined">2024 Republican hopefuls rush to defend Marine who put NYC subway rider in fatal chokehold</h2></a>

top_news = "https://apnews.com/hub/ap-top-news"
#holder lists for packaging later 
news_story_links = []
news_titles = []
news_story_body = []

class NewsScraper(scrapy.Spider):
  name = "news_scraper"

  def start_requests(self):
    yield scrapy.Request(url = top_news, callback = self.parse1)

  #first parsing method to gather the links
  def parse1(self, response):
    top_news_links = response.css('a[class*=Component-headline]::attr(href)').extract()    
    #print(top_news_links) 
# -> this above code stores the links in 
# the format of '/article/tiktok-ban-montana-lawsuit-72be560de89fb87e3c677c8e0cfd9fec' for example.
# so the parent domain portion would need to be added
#"https://apnews.com" + the link string stored from above.
    for url in top_news_links:
      time.sleep(random.randint(8,35)) #random time between requests to hopefully avoid labeling as a bot
      # appending to a list to work with later
      news_story_links.append("https://apnews.com"+url)
      yield response.follow(url = ("https://apnews.com"+url), callback = self.parse2) #keep an eye on this, not sure if can do
      
        
  # Second parsing method to process the next level in 
  def parse2(self, response):
    article_title = response.css('h1::text').extract()
    time.sleep(random.randint(5,20)) #random time between
    news_titles.append(article_title) #storing title to work with
    news_body = response.css('body p::text').extract()
    time.sleep(random.randint(5,20)) #random time between
    news_story_body.append(news_body)
 
      

#run the spider:
process = CrawlerProcess()
process.crawl(NewsScraper)
process.start()


#zipping together the stored lists of link,title,body
zipped_news = zip(news_story_links,news_titles,news_story_body)

#store in a gathered data in csv:
with open('stored_articles.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Link', 'Title', 'Body']) # write header row
    writer.writerows(zipped_news) # write data rows