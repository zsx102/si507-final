# How to supply API keys
- Create a yelp app. (link: https://www.yelp.com/fusion)
- Create **secrets.py** to store the api-key. The format is like:
  ```python
  API_KEY = 'your api-key'
  ```

# Required Package

- time
- sqlite3
- flask
- decimal
- requests
- bs4

# Create database

```SQL
CREATE TABLE "Colleges" (
	"Id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Name"	TEXT NOT NULL,
	"City"	TEXT NOT NULL,
	"State"	TEXT NOT NULL,
	"Latitude"	TEXT NOT NULL,
	"Longitude"	TEXT NOT NULL
);

CREATE TABLE "Businesses" (
	"Id"	INTEGER NOT NULL,
	"Name"	TEXT,
	"CollegeId"	INTEGER,
	"Rating"	TEXT,
	"AvgPrice"	TEXT,
	"Distance"	REAL,
	"Category"	TEXT,
	FOREIGN KEY("CollegeId") REFERENCES "Colleges"("Id")
);
```

# Interaction

- First, select a college you want to search, then, select a way to present the results, decide to use plot or not.
- See the documentation for detail information.

