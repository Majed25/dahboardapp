# Football Dashboard App

This is a dashboard application made with [Dash](https://dash.plotly.com/).

## Overview

The app collects and displays football data, providing insights and valuable information on various metrics. It is designed to practice multiple ETL (Extract, Transform, Load) processes using Python and RESTful APIs, and prepare the data for further analysis using machine learning models.

## Data Sources

The data for this dashboard is obtained from:

- [FBref.com](https://fbref.com/)
- [Transfermarkt.com](https://www.transfermarkt.com/)

### Scraping Data API

The data is scraped from the above sources using the [ScrapingDataAPI](https://github.com/Majed25/scrapingapi).

## Webhook Integration

The dashboard refreshes automatically with new data, triggered by a webhook linked to the [football-data.org API](https://www.football-data.org/). The webhook checks for new matches and updates the dashboard accordingly.

- Webhook repository: [footballdashboard_webhook](https://github.com/Majed25/footballdashboard_webhook)

## Project Objective

The main objectives of this project are:

- To practice multiple ETL processes using Python.
- To implement and work with RESTful APIs.
- To prepare and process data for deeper insights using machine learning models.

## Installation

To run this application locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Majed25/footballdashboard.git
   cd footballdashboard
