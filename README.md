# Use Scrapy To Crawl PTT Data 


## 目標
PTT，全名批踢踢實業坊，為台灣影響力數一數二的網路社群，擁有超過2萬個分類看板，註冊帳號高達150萬，是台灣原創網路文化的誕生地。<br/>

由於貼文為數不寡，以八卦版為例，每個月大約有6~7萬篇貼文被發表，再加上每篇貼文底下的回覆，所累積的文字資料量可以說是相當可觀，也因此PTT成為許多人作文字探勘會選擇的研究目標。<br/>

就八卦版而言，鄉民討論的主題可以說是毫無限制，也顯得八卦版內容較沒有一個顯著的方向，但也因為這個特性，我們也可以很容易找出某些主題、輿論在什麼樣的情況下，或者是什麼時間點，具有較高的討論熱度。<br/>

但既然要作資料分析，「如何爬取資料，並且決定以什麼樣的形式儲存」就顯得相當基本且重要，本教學目的為提供用Python Scrapy爬取PTT資料的方法。使用Scrapy來爬取PTT的貼文資訊，優點是簡單、快速，但Scrapy的爬取範圍侷限於網頁版PTT，若想連線至BBS版PTT爬取更多網頁版沒有的資料，則可以使用Python的Telnetlib來撰寫爬蟲。本則教學內容僅包含Scrapy的部分，敬請見諒。<br/>


## 使用技術
- [Python](https://www.python.org)
- [Scrapy](https://scrapy.org)
- [Telnetlib](https://docs.python.org/2/library/telnetlib.html)


## 在開始之前
#### 安裝Python
- 這個部分請參照Python官網的說明
- [連結點此](https://www.python.org/downloads/)

#### 設置Python虛擬環境
- 在此我們使用 Python 開發好幫手 – virtualenv
- 可以讓使用 Python 的開發者方便快速的建立各自獨立的虛擬環境。在獨立的虛擬環境中開發 Python 程式，可以降低各個環境中的套件數量，也降低了不同版本套件間衝突的可能。
- 使用者可以透過 Python 的 easy_install 工具安裝
```
$ easy_install virtualenv
```
- 或直接以 Ubuntu 的 apt-get 安裝
```
$ apt-get install python-virtualenv
```
- 安裝完成後，只需要輸入以下命令，就能建立名為 .env 的虛擬環境
```
$ virtualenv .env
```
- 接著透過以下命令啟動虛擬環境
```
$ source .env/bin/activate
```
- 啟動之後可以發現 shell 的提示字元前出現了虛擬環境的名稱，讓我們方便確認現在正使用哪個虛擬環境
- 如果在系統中安裝有多個版本的 Python （例如 2.7 及 3.2 版），就可以透過 --python 參數去指定建立的虛擬環境要使用哪個版本(以下教學仍採用Python 2.7版本)
```
$ virtualenv .env3 --python=python3.2
```

#### 在虛擬環境中安裝Scrapy
- 在Terminal中輸入以下指令進行安裝
```
$ pip install Scrapy
```

## 下一步
#### 使用Scrapy爬蟲
- [點我看教學](https://github.com/ChienChengLin/Use-Scrapy-To-Crawl-PTT-Data/blob/master/scrapy-crawler/Tutorial.md)
