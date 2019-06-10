# Scraper for political ads on Facebook ad library

This is a series of modules that does the following:

1) Scrapes Facebook ads using Selenium
2) Gets the main image from the ad
2) Runs the images through OCR 
3) Copies images to S3
4) Exports the data locally and to S3
5) Sends and email with a link to a summary of new ads

It is being run from a json feed generated by a google doc with a big list of Facebook pages that have made political posts or promoted a political post

The exported data is available [here](https://interactive.guim.co.uk/2019/04/fb-ad-data/fb-data.csv.gz). 

Things to keep in mind for data analysis:

All the party pages have been tracked since April 11, the start of the campaign. However, not all other pages have been tracked over the entire campaign. New pages are added daily. Some pages publish a mix of political and non-political ad content.

It is not possible to look at ad volume with this data, as it tracks whatever Facebook's ad library considers to be a unique ad. For example a page could run only one unique ad, but pay for millions of impressions, or a page could run hundreds of different ads with only a small amount of impressions each. 
