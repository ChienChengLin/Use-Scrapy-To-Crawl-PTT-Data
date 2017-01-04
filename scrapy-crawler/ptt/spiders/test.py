# encoding: utf-8

import logging
from datetime import datetime
import scrapy
from scrapy.http import FormRequest
from ptt.items import PostItem



class PTTSpider(scrapy.Spider):
    name = 'ptt'   
    allowed_domains = ['ptt.cc'] # 網域名稱
    start_urls = ('https://www.ptt.cc/bbs/Gossiping/index.html', ) # 起始網址

    _retries = 0
    MAX_RETRY = 100000 # 18歲問題的最大重試次數

    _pages = 0
    MAX_PAGES = 100 # 最大翻頁次數

    def parse(self, response):  # 這個函式包括18歲問題表單傳送、爬取每一頁的每個標題，並將各文章連結傳給parse_post函式
        if len(response.xpath('//div[@class="over18-notice"]')) > 0:   # 判斷是否進入18歲問題頁面
            if self._retries < PTTSpider.MAX_RETRY:
                self._retries += 1
                logging.warning('retry {} times...'.format(self._retries))
                yield FormRequest.from_response(response,
                                                formdata={'yes': 'yes'},
                                                callback=self.parse)  # 表單送出後，再次呼叫parse函式
            else:
                logging.warning('you cannot pass')

        else:   
            self._pages += 1 
            for href in response.css('.r-ent > div.title > a::attr(href)'): # 抓取每個文章的標題、連結

                url = response.urljoin(href.extract()) # urljoin將相對位址轉為絕對位址
                yield scrapy.Request(url, callback=self.parse_post) # 將每個內文的網址傳送給parse_post，進行內文等相關內容的爬取

            if self._pages < PTTSpider.MAX_PAGES: # 判斷是否等於最大翻頁次數
                lastpage = u'上頁'
                next_page = response.xpath(
                    '//div[@id="action-bar-container"]//a[contains(text(), "%s")]/@href' %(lastpage))
                if next_page:
                    url = response.urljoin(next_page[0].extract())
                    logging.warning('follow {}'.format(url))
                    yield scrapy.Request(url, self.parse)
                else:
                    logging.warning('no next page')
            else:
                logging.warning('max pages reached')

    def parse_post(self, response):  # 這個函式進行內文等相關資訊的爬取
        item = PostItem()
        item['title'] = response.xpath(
            '//meta[@property="og:title"]/@content')[0].extract()
        
        auth = u'作者'
        item['author'] = response.xpath(
            '//div[@class="article-metaline"]/span[text()="%s"]/following-sibling::span[1]/text()'%(auth))[
                0].extract().split(' ')[0]
        
        time = u'時間'
        datetime_str = response.xpath(
            '//div[@class="article-metaline"]/span[text()="%s"]/following-sibling::span[1]/text()'%(time))[
                0].extract()
        item['date'] = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %Y')

        item['content'] = response.xpath('//div[@id="main-content"]/text()')[
            0].extract()

        temp_ip = response.xpath(
            "//span[starts-with(text(),'※ 發信站: 批踢踢實業坊')]/text()".decode('utf8'))[
                0].extract() 
        temp_ip = temp_ip.strip("※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ".decode('utf8'))
        item['ip'] = temp_ip.strip("\n")



        comments = []
        total_score = 0
        for comment in response.xpath('//div[@class="push"]'):
            push_tag = comment.css('span.push-tag::text')[0].extract()
            push_user = comment.css('span.push-userid::text')[0].extract()
            push_content = comment.css('span.push-content::text')[0].extract()

            if u"推" in push_tag:
                score = 1
            elif u"噓" in push_tag:
                score = -1
            else:
                score = 0

            total_score += score

            comments.append({'user': push_user,
                             'content': push_content,
                             'score': score})

        item['comments'] = comments
        item['score'] = total_score
        item['url'] = response.url

        yield item