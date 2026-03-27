import requests
from bs4 import BeautifulSoup

def google_scholar_searcher(query) -> list:
    url = "https://scholar.google.com/scholar"
    params = {"q": query}
    
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    
    titles = []
    title_tags = soup.find_all("h3", class_="gs_rt")
    
    for tag in title_tags:
        a_tag = tag.find("a")
        if a_tag:
            titles.append(a_tag.text)
    
    return titles
