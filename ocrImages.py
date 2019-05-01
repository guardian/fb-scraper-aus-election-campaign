import scraperwiki
from PIL import Image
import cv2
import os
import pytesseract
import arrow
import time

def readImage(fileName):
	print("Converting {fileName} to greyscale".format(fileName=fileName))
	filePath = "imgs/" + fileName
	image = cv2.imread(filePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	ext = fileName.split(".")[1]
	tempFile = "temp." + ext
	cv2.imwrite(tempFile, gray)
	text = pytesseract.image_to_string(Image.open(tempFile))
	os.remove(tempFile)
	print(text)
	return text

def ocrImages(today, test):
	
	queryString = "* from ads where dateScraped='{today}'".format(today=today)
	queryResult = scraperwiki.sqlite.select(queryString)

	for row in queryResult:
		row['imageText'] = ""

		if row['image_id'] != "":
				print(row['image_id'], row['page_title'])
				try:
					row['imageText'] = readImage(row['image_id'])
				except Exception as e:
					row['imageText'] = ""
					print("error")
					print(e)

		if row['vid_image_id'] != "":
				print(row['image_id'], row['page_title'])
				try:
					row['imageText'] = readImage(row['vid_image_id'])
				except Exception as e:
					row['imageText'] = ""
					print("Error")
					print(e)	
		
		time.sleep(0.1)
		if not test:		
			scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")
			
