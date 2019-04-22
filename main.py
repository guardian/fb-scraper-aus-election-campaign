import scraper
import utilities
import uploadImages
import uploadJson
import ocrImages

# run it 

scraper.runScraper()

# handle all the files

utilities.getImages()
uploadImages.runUpload()
ocrImages.ocrImages()

# print update of new ads

utilities.getNewAds()

# update json of results

uploadJson.uploadJson()