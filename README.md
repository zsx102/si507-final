# Project code
- https://github.com/zsx102/si507-final

# Data sources

- The web page I scrape: https://www.latlong.net/category/national-parks-236-42.html
- The api I use: https://api.yelp.com/v3/businesses/search 
- I use BeautifulSoup to scrape the web page and save the data in table "Parks" (using cache)
- The way I use caching is the same as the project2.
![open_cache](/snapshot/open_cache.png)
![save_cache](/snapshot/save_cache.png)
![make_request](/snapshot/make_request.png)

# Database
- The database has been upload to github and there are two tables in the sqlite database
  - The first table "Parks" stored the information of parks from the web page I scraped. It has 4 fields: Id, ParkName, Latitude and Longitude.
  ![Parks](/snapshot/parks.png)
  - The second table "Businesses" stored the response of the yelp api request. It has 7 fields: Id, Name, ParkId, Rating, AvgPrice, Distance and Link.
  ![Businesses](/snapshot/businesses.png)
  - And the connecton of these two tables are the ParkId.
  ![ForeignKey](/snapshot/ForeignKey.png)

- Screenshots:
  ![screenshots1](/snapshot/screenshots1.png)
  ![screenshots2](/snapshot/screenshots2.png)

# Interaction / Presentation

- Give users a web page to select which park they want to search. (using flask)

- After user decided which park to search, the web page will present that particular park's nearby businesses, and the user will be given several options to show the data. (using plotly)
  - sorted by distance
  - sorted by average price
  - sorted by rating


