import scraper
import utilities
import uploadImages
import uploadJson
import ocrImages
import arrow
import argparse

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser()
parser.add_argument("test", default=False, nargs='?', type=str2bool, help="Toggle testing mode on or off")

test = parser.parse_args().test

today = arrow.now('Australia/Sydney').strftime('%Y-%m-%d')

if test == True:
	print("Starting run in test mode for", today)

else:
	print("Starting run for", today)

# run it 

scraper.runScraper(today,test)

# handle all the files

utilities.getImages(today,test)

uploadImages.runUpload(test)

ocrImages.ocrImages(today,test)

# print update of new ads

utilities.getNewAds(today, test)

# update json of results

uploadJson.uploadJson(test)