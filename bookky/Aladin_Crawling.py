import os
import  requests
from tkinter import EXCEPTION
from bs4 import BeautifulSoup
from socket import *
import urllib3
from time import sleep
from selenium import webdriver


def get_bookid():

    f = open(os.getcwd()+'\\bookky\\Book_Data.json', 'w', encoding='utf-8')

    f.write("[\n")

                            
    # All book -> 1 ~ 526 page

    for page in range(1,526):
        print(page,"작업중..\n")
        url = "https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=25&ViewType=Detail&PublishMonth=147&SortOrder=5&page=" + str(page) + "&Stockstatus=2&PublishDay=84&CustReviewRankStart=0&CustReviewCountStart=0&PriceFilterMax=-1&CID=351&SearchOption="
               
        request = requests.get(url, verify=False)
        List = BeautifulSoup(request.content, "html.parser")
        data_div = List.select('div.ss_book_box')

        Len = len(data_div)
        c=0

        for index in data_div:
            c = c+1
            get_bookdetail(str(index.get('itemid')),f)
            f.write(",\n")

    
    f.write("]")
    f.close()
        
def get_bookdetail(Bid,f):


    print(Bid)
    f.write("   {\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(executable_path=os.getcwd()+'\\bookky\\chromedriver.exe', chrome_options=options)
    url = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId="+str(Bid)

    driver.get(url)  

    for i in range(1,20):
        driver.execute_script("window.scrollTo(0, "+str(i*1000)+")")
        sleep(0.1)
    
    req = driver.page_source
    data = BeautifulSoup(req, "html.parser")



    book_title = data.select('a.Ere_bo_title')
    if len(book_title) != 0:
        f.write('       "TITLE" : "' + book_title[0].get_text().strip() + '",\n') 
    else:
        f.write('       "TITLE" : null,\n')
    
    book_subtitle = data.select('a.Ere_sub1_title')
    if len(book_subtitle) != 0:
        f.write('       "SUBTITLE" : "' + book_subtitle[0].get_text().strip() + '",\n')
    else:
        f.write('       "SUBTITLE" : null,\n')

    book_author = data.select('meta[property="og:author"]')
    if len(book_author) != 0:
        f.write('       "AUTHOR" : "' + book_author[0].get('content').strip() + '",\n')
    else:
        f.write('       "AUTHOR" : null,\n')
    
    book_ISBN = data.select('meta[property="books:isbn"]') 
    if len(book_ISBN) != 0:
        f.write('       "ISBN" : "' + book_ISBN[0].get('content').strip() + '",\n')
    else:
        f.write('       "ISBN" : null,\n')

    book_publisher = data.find_all('a','Ere_sub2_title')
    if len(book_publisher) != 0:
        f.write('       "PUBLISHER" : "' + book_publisher[-1].get_text().strip() + '",\n')
    else:
        f.write('       "PUBLISHER" : null,\n')


    book_price = data.find_all("div","Ritem")
    if len(book_price) != 0:
        f.write('       "PRICE" : "' + book_price[0].get_text().strip() + '",\n')
    else:
        f.write('       "PRICE" : null,\n')

    book_page = data.select('div.conts_info_list1 > ul > li')
    if len(book_page) != 0:
        f.write('       "PAGE" : "' + book_page[0].get_text().strip() + '",\n')
    else:
        f.write('       "PAGE" : null,\n')

    book_thumbnail = data.select('meta[property="og:image"]')
    if len(book_thumbnail) != 0:
        f.write('       "thumbnail" : "' + book_thumbnail[0].get('content').strip() + '",\n')
    else:
        f.write('       "thumbnail" : null,\n')
  

    book_index = data.find("div", id="div_TOC_All")
    if not book_index:
        book_index = data.find("div", id="div_TOC_Short")
        if not book_index:
            f.write('       "BOOK_INDEX" : null,\n')
        else:
            f.write('       "BOOK_INDEX" : "' + book_index.get_text().strip().replace('\n',"^^") + '",\n')
            
    else:
        f.write('       "BOOK_INDEX" : "' + book_index.get_text().strip().replace('\n',"^^") + '",\n')


    book_introduction = data.select('div.Ere_prod_mconts_box')
    f.write('       "BOOK_INTRODUCTION" : "')
    
    flag=1

    for i in book_introduction:
        location = str(i).find('LL">책소개')
        if location != -1:
            introduction = i.find('div','Ere_prod_mconts_R').get_text().strip().replace('\n',"^^")
            f.write(introduction.strip() + '",\n')
            flag=0
            break

    if flag == 1:
        f.write('null,\n')
       

    book_date = data.select('meta[itemprop="datePublished"]')
    if len(book_date) != 0:
        f.write('       "PUBLISH_DATE" : "' + book_date[0].get('content').strip() + '",\n')
    else:
        f.write('       "PUBLISH_DATE" : null,\n')


    book_rating = data.find('a','Ere_sub_pink Ere_fs16 Ere_str').get_text()
    if len(book_rating) != 0:
        f.write('       "RATING" : "' + book_rating.strip() + '",\n')
    else:
        f.write('       "RATING" : null,\n')

    f.write('       "Allah_BID" : "' + Bid + '"')

    f.write("   }")


    driver.quit()

  


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    get_bookid()

