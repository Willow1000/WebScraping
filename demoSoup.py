import requests
from bs4.element import NavigableString
from bs4 import BeautifulSoup
import pandas as pd

url = "https://xnxx.com/search/hardcore"


def scraper(url): 
    data_array = []
    for i in range(1,113):
        index = i    
        response = requests.get(url=url+f"/{index}")
        soup= BeautifulSoup(response.content)
        videos_div = soup.find("div",class_="mozaique")
        top_section = videos_div.find_all("div",class_="thumb-under")    
        bottom_section = videos_div.find_all("p",class_="metadata")
        for i in range(len(bottom_section)):
            title = top_section[i].find("a").text
            link = "https://xnxx.com"+top_section[i].find("a")['href']
            
           
            if len(bottom_section[i].find("span",class_="right").text.replace('\n','').strip().split(" ")) ==2:
                views,perc  = bottom_section[i].find("span",class_="right").text.replace('\n','').strip().split(" ")
            else:
                views = bottom_section[i].find_all('span')[0].text.replace("\n",'').strip().split(" ")[0]
                perc = None   
            duration = [t.strip() for t in bottom_section[i].contents if isinstance(t, NavigableString) and t.strip()][0]
            video_quality = bottom_section[i].find("span",class_='video-hd').text.replace("-",'').strip()
            data_array.append({
                "id":i,
                "title":title,
                "link":link,
                "duration":duration,
                "quality":video_quality,
                "views":views,
                "ratings":perc
            })
    return data_array
if __name__ == "__main__":
    data_array = scraper(url = url)   
    DataFrame = pd.DataFrame(data_array)
    DataFrame.to_csv("xnxx_hardcore.csv")
   