import subprocess as sub
import sys, time, csv

try:
    import scrapy
except ModuleNotFoundError:
    install = sub.run([sys.executable, "-m", "pip", 'install', "scrapy"], stderr=sub.PIPE, stdout=sub.PIPE) # Process for installing scrapy library
    if install.returncode == 0:
        print('scrapy installed successfull!\n')
        time.sleep(2)  # Sleep for 2 seconds before going on with the scraping
    else:
        print('Unsuccessful installation!,\nHint: Check your internet.')
        sys.exit(1)
        
from scrapy import Request, Selector, Spider
from scrapy.crawler import CrawlerProcess
from pathlib import Path


def create_remove_f_news():
    """
      This method is going to delete old NEWS if it exists,
      else it will create a new NEWS.
    """
    path = Path('Top 15 news.csv')
    if path.exists():
        path.unlink()
    else:
        path.touch()


class PunchScraper(Spider):
    name = "Punch_scraper"
    
    # This are the process for saving CSV
    def __init__(self):
        self.file_name = Path('Top 15 news.csv')
        with open(self.file_name, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['NEWS Title', 'URL', 'Content'])
        
    def start_requests(self):
        urls = ["https://punchng.com/"]
        for url in urls:
            yield Request(url, callback=self.link_follow)

    def link_follow(self, response):
        """
            This method contains all the link in the Punch website.
        """
        section = response.xpath("//*/section[@class='col-md-12 col-lg-6 latest-news-wraper']")
        links = section.css("div.row > ul li a::attr(href)").extract_first() # xpath("./div[@class='row']/ul//li//a/@href").extract()       
        for link in links:      
            yield response.follow(url=link, callback=self.parse)        

    def parse(self, response):
        """
        This method is for processing the NEWS for user digest.
        """
        title = response.css("h1.post_title::text").extract_first() # Title of the  page
        content = response.css("div.entry-content") # All the content of the punch
        page_sum = content.xpath(".//*[@style='text-align: justify;']")  # All paragraphs with unknown format
        if not page_sum:
            page_sum = content.xpath(".//p")  # All paragraphs
        
        # Some paragraph contains link which will make the news pretty bad
        # So I have to take the text for the link only
        # And then, join them with the paragraph back
        all_paragraph = []  # To store each paragraph of the NEWS
        for pg in page_sum:
            parag = " ".join(pg.xpath('.//text()').extract())
            all_paragraph.append(parag)        
        news = "\n".join(all_paragraph)  # Separating paragraphs with newline character
        with open(self.file_name, 'a') as content:
            file = csv.DictWriter(content, fieldnames=['NEWS Title', 'URL', 'Content'])
            file.writerow({'NEWS Title': title, 'URL': response.url, 'Content': news})
                             
                     
if __name__ == '__main__':
    create_remove_f_news()
    process = CrawlerProcess()
    process.crawl(PunchScraper)
    process.start()  # Crawling process start here
