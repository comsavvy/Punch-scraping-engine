import subprocess as sub, sys

try:
    import scrapy
except ModuleNotFoundError:
    install = sub.run([sys.executable, "-m", "pip", 'install', "scrapy"], capture_output=True)
    if install.stderr == b'':
        print('scrapy installed successfull')
    else:
        print('Check your internet!')
        sys.exit(1)
        
from scrapy import Request, Selector, Spider
from scrapy.crawler import CrawlerProcess
from collections import defaultdict

summary = defaultdict(list) # To store the title and the content

class PunchScraper(Spider):
    name = "Punch_scraper"
    
    
    def start_requests(self):
        urls = ["https://punchng.com/"]
        
        for url in urls:
            yield Request(url, callback=self.link_follow)
            
            
    def link_follow(self, response):
        section = response.xpath("//*/section[@class='col-md-12 col-lg-6 latest-news-wraper']")
        links = section.css("div.row > ul li a::attr(href)").extract() # xpath("./ul//li/a/@href").extract()
        for link in links:
            yield response.follow(url = link, callback=self.parse)
        
            
    def parse(self, response):
        title = response.css("h1.post_title::text").extract_first() # Title of the  page
        content = response.css("div.entry-content") # All the content of the punch
        page_sum = content.xpath(".//p") # All paragraph
        for pg in page_sum:
            parag = " ".join(pg.xpath('.//text()').extract())
            summary[title].append(parag)
        key = list(summary.keys()) # All title
        for i in key:
            summary[i] = "\n".join(summary[i]) # Separating the paragraph with newline character
        if summary[title] != '':
            with open(f'Top 15 news.txt', 'w+') as doc:
                doc.writelines("\n"+title+'\n')
                doc.writelines(summary[title])
            
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(PunchScraper)
    process.start()