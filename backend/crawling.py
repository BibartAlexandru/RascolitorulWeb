from typing import List
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typeguard import typechecked
from functional import seq
import requests

class SubPageData(BaseModel):
    text_lines: List[str]
    sub_page_uri: str

class SiteData(BaseModel):
    sub_pages_data: List[SubPageData]
    site_uri: str

class SiteDataArray(BaseModel):
    array: List[SiteData]
    initial_search_string: str

@typechecked
def base_url(url: str) -> str:
    split = urlsplit(url)
    return split.scheme + "://" + split.netloc

@typechecked
def get_site_data(sub_page_uri: str, site_uri:str ,query_keywords: List[str], max_uris_left: int = 10) -> List[SiteData]:
    """
    Returns a list of SiteData. Each SiteData for a different site, in case there are urls to another site. Otherwise, 
    an array with 1 SiteData object.
    """

    @typechecked
    def get_relevant_text(sub_page_uri: str) -> SubPageData:
        res = requests.get(sub_page_uri)
        if res.status_code != 200:
            raise Exception(f"Get request to {sub_page_uri} returned status code {res.status_code}")
        parser = BeautifulSoup(res.content,'html.parser')
        elements = parser.find_all('p') + parser.find_all('h1') + \
                parser.find_all('h2') + parser.find_all('h3') +\
                parser.find_all('h4') + parser.find_all('h5') + parser.find_all('h6')
        relevant_text = [element.get_text() for element in elements if any(q in element.get_text().lower() for q in query_keywords)]
        return SubPageData(text_lines=relevant_text,sub_page_uri=sub_page_uri)
    
    @typechecked
    def get_relevant_links(site_uri: str) -> List[str]:
        res = requests.get(site_uri)
        if res.status_code != 200:
            raise Exception(f"Get request to {site_uri} returned status code {res.status_code}")
        parser = BeautifulSoup(res.content,'html.parser')
        # sa nu inceapa linku cu # ca atunci e doar un element de pe aceasi pagina
        # relevante is daca au in ele un keyword. eventual putem schimba asta
        links = [a['href'] for a in parser.find_all('a',href = True) if a['href'][0] != '#']

        # poate linku e /cart/product in loc de https://emag.ro/cart/product, urljoin lipeste urlu de baza cu ala relativ daca e relativ
        relevant_links = [urljoin(site_uri,l) for l in links if any(keyword in l for keyword in query_keywords)]
        return relevant_links

    sub_pages_data: List[SubPageData] = []
    uris_crawled = set()
    uris_to_crawl = [sub_page_uri]
    while max_uris_left > 0 and len(uris_to_crawl) > 0:
        print(len(uris_to_crawl))
        current_sub_page = uris_to_crawl.pop(0)
        uris_crawled.add(current_sub_page)
        max_uris_left -= 1
        # print(f'Crawling {current_site}')
        try:
            sub_pages_data.append(get_relevant_text(current_sub_page))
            relevant_links = get_relevant_links(current_sub_page)
            for link in relevant_links:
                if link not in uris_crawled:
                    uris_to_crawl.append(link)
        except Exception as e:
            print(e)
    
    # Gasesc base_urlurile siteurilor vizitate 

    sub_pages = seq(sub_pages_data).map(lambda obj : obj.sub_page_uri).to_list()
    site_uris = set()
    for sub_page in sub_pages:
        if base_url(sub_page) not in site_uris:
            site_uris.add(base_url(sub_page))
    
    for site_uri in site_uris:
        print(site_uri)

    site_datas = [
        SiteData(sub_pages_data=[sp for sp in sub_pages_data if base_url(sp.sub_page_uri) == site],site_uri=site)
        for site in site_uris
    ]

    return site_datas