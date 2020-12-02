import subprocess as sub
import sys

try:
    import scrapy
except ModuleNotFoundError:
    install = sub.run([sys.executable, "-m", "pip", 'install', "scrapy"], capture_output=True)
    if install.returncode == 0:
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
        links = section.css("div.row > ul li a::attr(href)").extract_first() # xpath("./div[@class='row']/ul//li//a/@href").extract()
        for link in links:
            yield response.follow(url=link, callback=self.parse)

    def parse(self, response):
        title = response.css("h1.post_title::text").extract_first() # Title of the  page
        content = response.css("div.entry-content") # All the content of the punch
        page_sum = content.xpath(".//p")  # All paragraphs
        for pg in page_sum:
            parag = " ".join(pg.xpath('.//text()').extract())
            summary[title].append(parag)
        key = list(summary.keys()) # All title
        for i in key:
            summary[i] = "\n".join(summary[i])  # Separating paragraphs with newline character
        first = 0
        with open(f'Top 15 news.txt', 'a+') as doc:
            title_format = f'{title}\n' if first == 0 else "\n\n"+title+'\n'
            doc.writelines(title_format)
            doc.writelines(summary[title])
            first = 1


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(PunchScraper)
    process.start()
