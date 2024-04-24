import lxml
import re
import pandas as pd

from bs4 import BeautifulSoup
from requests import get

class IMDBScraper:
    """A class for scraping data from IMDb and saving it as a CSV file."""
    
    def __init__(self, url):
        """Initializes the IMDBScraper with the given URL."""
        self.url = url
        self.page = get(url)
        self.soup = BeautifulSoup(self.page.content, 'lxml')

    def get_movie_data(self):
        """Extracts movie data from the IMDb page and returns it as a DataFrame."""
        movie_data = []
        movie_frame = self.soup.find_all("div", class_="lister-item mode-advanced")
        
        # Iterate through each movie frame
        for movie in movie_frame:
            # Extract title
            title = movie.find("h3", class_="lister-item-header").find("a").text
            
            # Extract release date and clean it
            date = movie.find("span", class_="lister-item-year").text
            date = re.sub(r"[()]", "", date)
            
            # Extract runtime, genre, rating, score, and description
            runtime = movie.find("span", class_="runtime")
            runtime = runtime.text[:-4] if runtime else None
            
            genre = movie.find("span", class_="genre")
            genre = genre.text.strip().split(",") if genre else []
            
            rating = movie.find("strong")
            rating = rating.text if rating else None
            
            score = movie.find("span", class_="metascore")
            score = score.text.strip() if score else None
            
            description = movie.find_all("p", class_="text-muted")[-1].text.strip()
            
            # Extract director and stars
            cast = movie.find("p", class_="")
            director, stars = None, None
            if cast:
                casts = cast.text.strip().split('|')
                casts = [c.strip() for c in casts]
                if len(casts) > 0:
                    director = casts[0].replace("Director:", "").strip()
                if len(casts) > 1:
                    stars = casts[1].replace("Stars:", "").strip().split(", ")
            
            # Extract votes and gross earnings
            numbers = movie.find_all("span", attrs={"name": "nv"})
            votes, gross = None, None
            if len(numbers) == 2:
                votes, gross = numbers[0].text, numbers[1].text
            elif len(numbers) == 1:
                votes = numbers[0].text
            
            # Append extracted data to movie_data list
            movie_data.append([title, date, runtime, genre, rating, score, description, director, stars, votes, gross])
        
        # Create a DataFrame from movie_data
        columns = ['Title', 'Release Date', 'Runtime', 'Genre', 'Rating', 'Score', 'Description', 'Director', 'Stars', 'Votes', 'Gross']
        df = pd.DataFrame(movie_data, columns=columns)
        
        return df

    def save_to_csv(self, df, filename='imdb_data.csv'):
        """Saves the DataFrame to a CSV file."""
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

# Usage example
url = "https://www.imdb.com/search/title?count=100&title_type=feature,tv_series&ref_=nv_wl_img_2"
scraper = IMDBScraper(url)
df = scraper.get_movie_data()
scraper.save_to_csv(df, 'imdb_data.csv')
