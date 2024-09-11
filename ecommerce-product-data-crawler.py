import re, json, urllib, os, shutil
import pandas as pd
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from scrapy.spiders import SitemapSpider
from datetime import timedelta

### Setup e inizio del crawling ###

if os.path.exists('ProductDataNew.csv'):
    os.rename('ProductDataNew.csv', 'ProductDataOld.csv')
elif os.path.exists('ProductDataOld.csv'):
    pass
else:
    print("ERRORE: Il file .csv contenente i dati storici dei prodotti non è stato trovato.\nPosizionalo nella stessa directory dello script .py e nominalo 'ProductDataNew.csv' prima di eseguire nuovamente lo script.")
    exit()

if os.path.exists('shopProducts.json'):
    os.remove('shopProducts.json')

def get_page(url):
    response = urllib.request.urlopen(urllib.request.Request(url, 
                                                             headers={'User-Agent': 'Mozilla'}))
    soup = BeautifulSoup(response, 
                         'html.parser', 
                         from_encoding=response.info().get_param('charset'))
    
    return soup

def get_sitemaps(robots):
    sitemapList = []
    lines = str(robots).splitlines()

    for line in lines:
        if line.startswith('Sitemap:'):
            split = line.split(':', maxsplit=1)
            if '/en/' in split[1]:
                sitemapList.append(split[1].strip())

    return sitemapList

robots=get_page('https://e-commerce.com/robots.txt')
sitemaps=get_sitemaps(robots)

class ProductsSpider(SitemapSpider):
    name = "products"
    allowed_domains = ["e-commerce.com"]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }
    sitemap_urls = sitemaps

    def parse(self, response):
        data={
            'h1' : response.selector.xpath("//*[@class='page-title']/span/text()").get(),
            'cat1' : 
                None if response.selector.xpath("//*[@class='items']/li[2]/a[@title]/text()").get()==None
                else response.selector.xpath("//*[@class='items']/li[2]/a[@title]/text()").get().strip(),
            'cat2' : 
                None if response.selector.xpath("//*[@class='items']/li[3]/a[@title]/text()").get()==None
                else response.selector.xpath("//*[@class='items']/li[3]/a[@title]/text()").get().strip(),
            'skuMain' : response.selector.xpath("//*[@data-product-sku]").css("::attr(data-product-sku)").get(),
            'skuSubList' : 
                None if (response.selector.xpath("//*[contains(text(),'AEC.CONFIGURABLE_SIMPLES')]/text()").get()==None or re.sub(';AEC.BUNDLE.*', '', re.sub('\/\*\*.*CONFIGURABLE_SIMPLES = ', '', response.selector.xpath("//*[contains(text(),'AEC.CONFIGURABLE_SIMPLES')]/text()").get().strip().replace('\n','').replace('\t','')))=='[]')
                else [d.get('simple_id',None) for d in list(json.loads(re.sub(';AEC.BUNDLE.*', '', re.sub('\/\*\*.*CONFIGURABLE_SIMPLES = ', '', response.selector.xpath("//*[contains(text(),'AEC.CONFIGURABLE_SIMPLES')]/text()").get().strip().replace('\n','').replace('\t','')))).values())],
            # 'variantSubList' :
            #     None if (response.selector.xpath("//*[contains(text(),'AEC.CONFIGURABLE_SIMPLES')]/text()").get()==None or re.sub(';AEC.BUNDLE.*', '', re.sub('\/\*\*.*CONFIGURABLE_SIMPLES = ', '', response.selector.xpath("//*[contains(text(),'AEC.CONFIGURABLE_SIMPLES')]/text()").get().strip().replace('\n','').replace('\t','')))=='[]')
            #     else [d.get('name',None) for d in list(json.loads(re.sub(';AEC.BUNDLE.*', '', re.sub('\/\*\*.*CONFIGURABLE_SIMPLES = ', '', response.selector.xpath("//*[contains(text(),'AEC.CONFIGURABLE_SIMPLES')]/text()").get().strip().replace('\n','').replace('\t','')))).values())],
            #'brand' : 
            #    None if response.selector.xpath("//*[contains(text(),'AEC.Cookie.detail')]/text()").get()==None or json.loads(re.sub('\]\}\,"impressions"\:.*', '', re.sub('window.google_tag_params.ecomm_pagetype.*"products"\:\[', '', response.selector.xpath("//*[contains(text(),'AEC.Cookie.detail')]/text()").get().strip().replace('\n','').replace('\t','')))).get('brand')==''
            #    else json.loads(re.sub('\]\}\,"impressions"\:.*', '', re.sub('window.google_tag_params.ecomm_pagetype.*"products"\:\[', '', response.selector.xpath("//*[contains(text(),'AEC.Cookie.detail')]/text()").get().strip().replace('\n','').replace('\t','')))).get('brand'),
            'url' : response.request.url
        }

        yield data

def run_spider():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "shopProducts.json": {"format": "json"},
        },
    })
    process.crawl(ProductsSpider)
    process.start()

#OPZIONALE: timestamp di inizio crawling
crawlStartTime=datetime.now()

if __name__ == "__main__":
    run_spider()

#OPZIONALE: timestamp di fine crawling, stampa i timestamp di inizio e fine crawling
crawlEndTime=datetime.now()
print("L'ora di inizio del crawling è stata: "+crawlStartTime.strftime("%H:%M:%S"))
print("L'ora di fine del crawling è stata: "+crawlEndTime.strftime("%H:%M:%S"))
crawlStartTime_delta = timedelta(hours=crawlStartTime.hour, minutes=crawlStartTime.minute, days=crawlStartTime.day)
crawlEndTime_delta = timedelta(hours=crawlEndTime.hour, minutes=crawlEndTime.minute, days=crawlEndTime.day)
difference_delta = crawlEndTime_delta - crawlStartTime_delta
print("Il tempo totale trascorso è: "+str(difference_delta))

### Inizia la pulizia dei dati del file JSON ###

df = pd.read_json('shopProducts.json')

df['order']=None # aggiunge colonna per ordinare per sitemap

sitemapOrder=[] # setup per ordinare i dati a seconda della cartella linguistica della sitemap (/it/en/ in cima)
for sitemap in sitemaps:
    sitemapOrder.append(sitemap.replace('https://e-commerce.com/sitemap','').replace('sitemap.xml',''))
    
sitemapOrderNum=[]

for sitemap in range(len(sitemapOrder)):
    sitemapOrderNum.append(sitemap)

sitemapOrderDict=dict(zip(sitemapOrder, sitemapOrderNum))

for sitemap in sitemapOrderDict.keys():
    for index, row in df.iterrows():
        if sitemap in df.at[index,'url']:
            df.at[index,'order']=sitemapOrderDict[sitemap]

df.sort_values(by=['order'],ascending=True, inplace=True) # ordina i dati per cartella linguistica

df.dropna(axis=0, subset=['h1'], inplace=True)

df.drop_duplicates(subset=['skuMain'], keep='first', inplace=True)

for index, row in df.iterrows():
    df.at[index,'h1']=(' '.join(df.at[index,'h1'].splitlines())).replace('  ',' ') # fixa alcuni titoli che vanno a capo
    if row['skuSubList']!=None: # aggiunge il configurabile alla lista di sku
        row['skuSubList'].append(row['skuMain'])
    else:
        df.at[index,'skuSubList']=df.at[index,'skuMain']

df=df.explode(['skuSubList']) # espande i valori di sku creando una riga per ognuno

df.rename(columns={"h1": "item_name", "cat1": "item_cat1", "cat2": "item_cat2", "skuSubList": "item_id"}, inplace=True)

df.drop(['skuMain','url','order'], axis=1, inplace=True)

df=df.replace('"','', regex=True)

df['item_name']=df['item_name'].str.replace(',','.')

df.to_csv('productDataCurrent.csv',index=False)

### Inizia il confronto con i dati del periodo precedente per aggiungere i dati di eventuali prodotti nuovi ###

dfCurr=pd.read_csv('productDataCurrent.csv')

dfPrev=pd.read_csv('ProductDataOld.csv')

dfPrevRowCount=len(dfPrev)

dfMerge=pd.concat([dfPrev, dfCurr])

dfMerge.drop_duplicates(subset=['item_id'], keep='first', inplace=True)

dfMergeRowCount=len(dfMerge)

numAddedProducts=dfMergeRowCount-dfPrevRowCount

dfMerge.to_csv('ProductDataNew.csv',index=False)

if numAddedProducts>0:
    print('Sono stati trovati e aggiunti al file '+str(numAddedProducts)+' nuovi articoli.')
    lastProductsAdded=dfMerge.tail(numAddedProducts)
    print(lastProductsAdded)
    print('Procedere al caricamento su GA4 del file "ProductDataNew.csv".')
else:
    print('Non sono stati trovati nuovi articoli. Non è necessario caricare su GA4 il file "ProductDataNew.csv".')

os.remove('ProductDataOld.csv')

os.remove('productDataCurrent.csv')

if os.path.exists('Storico-Dati-Prodotti/') == False:
    os.mkdir('Storico-Dati-Prodotti')

shutil.copy2('./ProductDataNew.csv', './Storico-Dati-Prodotti')

currentMonth=datetime.now().month

currentYear=datetime.now().year

currentDay=datetime.now().day

os.rename('Storico-Dati-Prodotti/ProductDataNew.csv','Storico-Dati-Prodotti/ProductInfo_'+str(currentYear)+'-'+str(currentMonth)+'-'+str(currentDay)+'.csv')