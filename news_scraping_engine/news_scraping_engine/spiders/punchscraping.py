import scrapy


class ScrapingEngineSpider(scrapy.Spider):
    name = 'scraping_engine'
    allowed_domains = ['punchng.com']
    start_urls = ['https://punchng.com/']

    first_news = 0 # This will let me keep track of the first NEWS, so as to maintain the newline character.
    
    def __init__(self):
      self.all_paragraph = []  #  To store each paragraph of the NEWS
      
    def parse(self, response):
        """
            This method contains all the link in the Punch website.
        """
        section = response.xpath("//*/section[@class='col-md-12 col-lg-6 latest-news-wraper']")
        links = section.css("div.row > ul li a::attr(href)").extract_first() # xpath("./div[@class='row']/ul//li//a/@href").extract()
        for link in links:
            yield response.follow(url=link, callback=self.link)
    
    def link(self, response):
        """
        This method is for processing the NEWS for user digest.
        """
        title = response.css("h1.post_title::text").extract_first() # Title of the  page
        content = response.css("div.entry-content") # All the content of the punch
        page_sum = content.xpath(".//*[@style='text-align: justify;']")  # All paragraphs with unknown format
        if page_sum == []:
          page_sum = content.xpath(".//p")  # All paragraphs
        
        # Some paragraph contains link which will make the news pretty bad
        # So I have to take the text for the link only
        # And then, join them with the paragraph back
        for pg in page_sum:
            parag = " ".join(pg.xpath('.//text()').extract())
            self.all_paragraph.append(parag)
        news = "\n".join(self.all_paragraph)  # Separating paragraphs with newline character
        self.all_paragraph = [] # Set free
        yield {
                   'title': title,
                   'news': news,
                   'url': response.url
                }
