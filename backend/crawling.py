from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typeguard import typechecked
import requests

class SubPageData(BaseModel):
    text_lines: List[str]
    sub_page_uri: str

class SiteData(BaseModel):
    sub_pages_data: List[SubPageData]
    site_uri: str

class SiteDataArray(BaseModel):
    array: List[SiteData]


@typechecked
def get_site_data(site_uri: str,site_base_uri:str ,query_keywords: List[str], nr_uris_to_crawl: int = 10) -> SiteData:
    
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

    data: List[SubPageData] = []
    uris_crawled = set()
    uris_to_crawl = [site_uri]
    while nr_uris_to_crawl > 0 and len(uris_to_crawl) > 0:
        current_sub_page = uris_to_crawl.pop(0)
        uris_crawled.add(current_sub_page)
        nr_uris_to_crawl -= 1
        # print(f'Crawling {current_site}')
        try:
            data.append(get_relevant_text(current_sub_page))
            relevant_links = get_relevant_links(current_sub_page)
            for link in relevant_links:
                if link not in uris_crawled:
                    uris_to_crawl.append(link)
        except Exception as e:
            print(e)

    return SiteData(sub_pages_data=data,site_uri=site_base_uri)