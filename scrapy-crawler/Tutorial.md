# 用Scrapy爬取網頁版PTT


## 如何爬蟲

- 在Scrapy安裝完成後，首先要創建專案
```
$ scrapy startproject ptt
```
- Scrapy會自動產生一個名為ptt的專案資料夾
- 到<root_dir>/ptt/settings.py中設定連線延遲:
```python
DOWNLOAD_DELAY = 1.0
```
- 接著到/ptt/items.py中定義一些想要抓取的項目，如貼文、推文、作者等:
```python
class PostItem(scrapy.Item):
    title = scrapy.Field() 		# 貼文標題
    author = scrapy.Field() 	# 貼文作者
    date = scrapy.Field() 		# 貼文日期
    content = scrapy.Field() 	# 貼文內容
    ip = scrapy.Field()			# 作者IP位址
    comments = scrapy.Field() 	# 回文內容
    score = scrapy.Field() 		# 貼文分數(獲得推文+1分; 獲得噓文-1分)
    url = scrapy.Field() 		# 貼文網址
```
- 接著就可以編輯/ptt/spiders/ptt.py實際撰寫爬蟲程式了<br/>首先測試能否連上ptt(此處以八卦版為例)
```python
import scrapy

class PTTSpider(scrapy.Spider):
    name = 'ptt'
    allowed_domains = ['ptt.cc']
    start_urls = ('https://www.ptt.cc/bbs/Gossiping/index.html', )

    def parse(self, response):
        filename = response.url.split('/')[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
```
- 完成編輯後，在根目錄(有 scrapy.cfg 的目錄)下執行：
```
scrapy crawl ptt
```
- 完成後應該會發現存下了一個網頁，內容為是否已滿18歲的確認頁面，代表成功連上ptt。但為了能夠成功抓取八卦版文章，我們必須讓爬蟲程式自動回答這個18歲確認問題
- 利用 div.over18-notice 存在與否來偵測是否進入年齡詢問的頁面
```python
import logging

from scrapy.http import FormRequest

class PTTSpider(scrapy.Spider):
    # ...
    _retries = 0
    MAX_RETRY = 1

    def parse(self, response):
        if len(response.xpath('//div[@class="over18-notice"]')) > 0:
            if self._retries < PTTSpider.MAX_RETRY:
                self._retries += 1
                logging.warning('retry {} times...'.format(self._retries))
                yield FormRequest.from_response(response,
                                                formdata={'yes': 'yes'},
                                                callback=self.parse)
            else:
                logging.warning('Error occurs.')

        else:
          # ...
```
- 上述程式碼利用 FormRequest 在遇到詢問頁面時自動送出表單，用 callback 在表單送出後重新回到原本的爬蟲函式，繼續處理。以 MAX_RETRY 限制表單傳送的次數。
- 另外這裡使用了 XPath 來指定網頁物件的位置
XPath的相關教學請參考[XPath Tutorial](http://www.w3schools.com/xml/xpath_intro.asp)
- 再來就是實際爬文的程式了:
```python
class PTTSpider(scrapy.Spider):
    # ...

    _pages = 0
    MAX_PAGES = 2

    def parse(self, response):
        if len(response.xpath('//div[@class="over18-notice"]')) > 0:
            # ...
        else:
            self._pages += 1
            for href in response.css('.r-ent > div.title > a::attr(href)'):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse_post)

            if self._pages < PTTSpider.MAX_PAGES:
                next_page = response.xpath(
                    '//div[@id="action-bar-container"]//a[contains(text(), "上頁")]/@href')
                if next_page:
                    url = response.urljoin(next_page[0].extract())
                    logging.warning('follow {}'.format(url))
                    yield scrapy.Request(url, self.parse)
                else:
                    logging.warning('no next page')
            else:
                logging.warning('max pages reached')
```
- 這裡使用 CSS Selector，以css('.r-ent > div.title > a::attr(href)') 來抓出每個文章的網址連結。用 response.urljoin 將相對路徑轉成絕對路徑，再把路徑丟給 parse_post 做進一步處理。一樣用 XPath 找出上一頁的網址連結，達到自動翻頁。用 MAX_PAGES 控制最多翻幾頁

## 完整的爬蟲程式
- 最後根據前面定義的items.py，撰寫完整的爬蟲程式(/ptt/spiders/ptt.py):
```python
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
```
- 在Terminal執行以下指令開始爬蟲，並將資料儲存成一個JSON檔案
```
$ scrapy crawl ptt -o gossiping.json
```

## 下一步: 如何使用這個JSON檔案 ?
- [JSON - Introduction](http://www.w3schools.com/js/js_json_intro.asp)
- [json - JSON encoder and decoder](https://docs.python.org/2/library/json.html)