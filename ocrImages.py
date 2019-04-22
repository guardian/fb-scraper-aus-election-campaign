import scraperwiki
from PIL import Image
import cv2
import os
import pytesseract

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

def ocrImages():

	today = datetime.strftime(datetime.now(), '%Y-%m-%d')
	queryString = "* from ads where dateScraped='{today}'".format(today=today)
	queryResult = scraperwiki.sqlite.select(queryString)

	for row in queryResult:
		row['imageText'] = ""

		if row['image_id'] != "":
				print(row['image_id'], row['page_title'])
				row['imageText'] = readImage(row['image_id'])
			
		if row['vid_image_id'] != "":
				print(row['image_id'], row['page_title'])
				row['imageText'] = readImage(row['vid_image_id'])
		
		time.sleep(0.1)		
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id"], data=row, table_name="ads")
		
	
