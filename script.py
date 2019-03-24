#import packages as requested
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re, ssl, os, sys, queue, json
 
items = 10;
page_content = "";
pageMainText = "";
pageTitle = "";
visited = [];
savedURLs = [];
savedTitles = [];
input = [];
relatedTerms=[];

#SSL Environment, w/e that is
def SSL():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

def getPageContent(url):
    try:
        htmlResponse = urlopen(url).read();
        page_content = htmlResponse.decode('utf-8');
        return page_content
    except Exception as e:
        return None

def clean_title(title):
    invalid_characters = ['<','>',':','\"','/','\\','?','*'];
    for c in invalid_characters:
        title=title.replace(c,'');
    return title;

def get_urls(soup):
    links = soup.find_all('a');
    urls = [];
    for link in links:
        urls.append(link.get('href'));
    return urls;

def is_url_valid(url):
    if url is None:
        return False;
    if re.search('#', url):
        return False;
    match=re.search('^/wiki/',url);
    if match:
        return True;
    else:
        return False;

def reformatUrl(url):
    match = re.search('^/wiki/',url);
    if match:
        return "https://en.wikipedia.org"+url;
    else:
        return url;

def save():
    f = open("./Pages/crawled_urls.txt","w");
    i = 0;
    content="";
    for url in savedURLs:
        page_content = getPageContent(url);
        soup = BeautifulSoup(page_content,'html.parser');
        content = soup.get_text().lower();
        f1 = open("./Pages/"+clean_title(str(i+1)+": "+savedTitles[i]+".html"),"w"); 
        f.write(str(i+1)+": "+savedTitles[i]+": "+content.replace("\n","")+"\n");
        f1.write(content);
        i+=1;
        f1.close();
    f.close();

def saveUrls():
    f = open("./Pages/Urls.txt","w");
    for url in savedURLs:
        f.write(url+"\n");
    f.close();
        
def extractUrls(soup):
    links = soup.find_all('a')
    urls=[]
    for link in links:
        urls.append(link.get('href'));
    return urls;

def FocusedCrawler(input):
    q = queue.Queue();    
    pageCount = 0;
    for url in input:
        q.put(url);
        visited.append(url);
    while (not q.empty()):
        url = q.get()
        print("Checking: "+url);
        page_content = getPageContent(url);
        #print("Sample:"+page_content[500:600]);
        if page_content is None:
            continue;
        soup = BeautifulSoup(page_content,'html.parser');
        pageMainText = soup.get_text().lower();
        #print(pageMainText);
        termCounter = 0;
        for term in relatedTerms:
            if (re.findall(term,pageMainText)):
                termCounter = termCounter+1;
                if termCounter >= 2:
                    pageCount=pageCount+1
                    pageTitle = clean_title(soup.title.string) 
                    print('{} {}'.format(pageCount,pageTitle));
                    savedURLs.append(url);
                    savedTitles.append(pageTitle);
                    break
            if (pageCount >= items):
                saveUrls();
                print("Saving...");
                save();
                print("Done!");
                exit();
            outGoingUrls = extractUrls(soup);       
            for outURL in outGoingUrls:
                if is_url_valid(outURL) and reformatUrl(outURL) not in visited:
                    q.put(reformatUrl(outURL));
                    visited.append(reformatUrl(outURL));     

with open('data.json') as f:
    data = json.load(f);

    input = data['seeds'];
    relatedTerms = data['tags'];
    items = data['items'];        

    SSL();
    FocusedCrawler(input);
