import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SstgeorgeItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'
base = 'https://www.stgeorge.com.au/about/media/news/{}'
class SstgeorgeSpider(scrapy.Spider):
	name = 'stgeorge'
	now = datetime.datetime.now()
	year = now.year
	start_urls = ['https://www.stgeorge.com.au/about/media/news?searchsource=search-results&kw=news&cat=news-%26-media-releases&rank=1&result-type=natural']

	def parse(self, response):
		post_links = response.xpath('//p//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if self.year > 2014:
			self.year -= 1
			yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="lead top-margin3-xs"]/p//text()').getall()
		if date:
			date = re.findall(r'\d+\s\w+\s\d+', ''.join(date))
		title = response.xpath('//div[@class="lead top-margin3-xs"]/p/b//text()|//div[@class="lead top-margin3-xs"]/p[1]//text()').get()
		if not title:
			title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="body-copy4 parbase section"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SstgeorgeItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
