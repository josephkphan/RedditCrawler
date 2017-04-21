# RedditCrawler

## Requirements
 - Anaconda Python
 
## Setup
 - Install scrappy "conda install -c conda-forge scrapy"
 - set up folder: "scrapy startproject <YOUR PROJECT NAME>"
 
## Run Code
  - Inside the folder created by the scrappy start project, run "scrappy crawl --nolog <SPIDER NAME>"
      - nolog so you don't see debug info


## Mongo help commands
  - show dbs
  - use <database name>
  - db.getCollectionNames()
  - db.<collection_name>.find()
  - db.<collection_name>.drop()
  - db.<collection_name>.count()