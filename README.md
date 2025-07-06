# App Scraper

## Table of Contents

- [Project Overview](#project-overview)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
  - [Running the Scraper](#running-the-scraper)
  - [Exporting Data](#exporting-data)
- [Code Structure](#code-structure)


## Project Overview 

This project is a web scraper designed to extract app data and user comments from an app marketplace, specifically targeting apps related to mental health exercises. The scraper fetches app metadata, user comments, and related information, then saves the data into a Django-based backend. Additionally, it provides functionality to export the scraped data into well-structured Excel files for reporting or analysis.

##  Setup and Installation

Follow these steps to set up and run the project using Docker.

---

Ensure [Docker](https://www.docker.com/products/docker-desktop/) is installed on your machine.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hanane-yh/bazar_scraper.git
   cd bazar_scraper
   
2. **Build and start the containers**:
   ```bash
   docker-compose up --build

## Usage
### Running the Scraper
To run the scraper and start collecting app data and comments:

```bash
   docker exec -it scraper_app python manage.py scrape_apps
```
This command will:

- Fetch app URLs from the listing page.

- Scrape app details and comments using Selenium.

- Save the data into the local database.

### Exporting Data
To export the saved data from the database to an Excel file, run:
```bash
   docker exec -it scraper_app python manage.py export_data
```

This will generate an Excel file containing the scraped apps and comments, ready for analysis or sharing.


## Code Structure

This project is organized into several modules to separate concerns and improve maintainability:

- **scrapers.py**  
  Contains functions to scrape app details, comments, and other data from the target website using Selenium.

- **savers.py**  
  Handles saving the scraped data (apps, users, comments) into the database models.

- **scripts.py**  
  Main entry point to run the scraping pipeline. It fetches app URLs, extracts data, and saves it using the above modules.

- **exporters.py**  
  This module handles exporting the scraped data (apps, users, and comments) from the database into a structured Excel file.

- **utils.py**  
  Contains utility functions.
