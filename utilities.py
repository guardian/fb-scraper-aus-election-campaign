# bunch of different functions
import requests
import lxml.html
import scraperwiki
import simplejson as json
import time
from lxml.html.clean import Cleaner
import arrow
import mmh3

def getImages(today, test):

	queryString = "* from ads where dateScraped='{today}'".format(today=today)
	queryResult = scraperwiki.sqlite.select(queryString)
	
	images = []

	for row in queryResult:
		if row['av_img_url'] != "":
			images.append({"image_url":row['av_img_url'], "image_id":row['av_img_id']})
		if row['image_url'] != "":
			images.append({"image_url":row['image_url'], "image_id":row['image_id']})
		if row['vid_image_url']	!= "":
			images.append({"image_url":row['vid_image_url'], "image_id":row['vid_image_id']})

	# Make unique
	
	images_unique = list({v['image_id']:v for v in images}.values())		

	for row in images_unique:
		print("Getting", row['image_url'])
		if not test:
			r = requests.get(row['image_url'])
			with open('imgs/{image_id}'.format(image_id=row['image_id']), 'wb') as f:
				f.write(r.content)

	print("Done saving images")		

def cleanHtml(row):

	cleaner = Cleaner()
	cleaner.javascript = True
	cleaner.style = True 

	snippet = lxml.html.fromstring(row['html'])

	if row['image_id'] != "":
		print("Image post")
		
		images = snippet.cssselect("._7jys")

		# Remove all but first image for gallery posts, add text saying we removed them

		if len(images) > 1:
			origNumber = len(images) - 1
			
			imageStr = "images"
			
			if origNumber == 1:
				imageStr = "image"

			tagString = "<div class='imageCount'>This post originally contained {origNumber} more {imageStr}</div>".format(origNumber=origNumber, imageStr=imageStr)

			for x in range(1, len(images)):
				el = images[x].drop_tree()

			images[0].addnext(lxml.html.fromstring(tagString))
	
		# Remove js and css
			
		cleaned = cleaner.clean_html(snippet)

		# replace main and avatar img src with guardian cdn eg https://interactive.guim.co.uk/2019/04/fb-ad-images/57617685_385077462333660_5324670939118436352_n.jpg

		cleaned.cssselect("._7jys")[0].attrib['src'] = "https://interactive.guim.co.uk/2019/04/fb-ad-images/" + row['image_id']
		cleaned.cssselect("._7pg4")[0].attrib['src'] = "https://interactive.guim.co.uk/2019/04/fb-ad-images/" + row['av_img_id']

		return(lxml.html.tostring(cleaned))

	elif row['vid_image_id'] != "" or row['vid_file_id'] != "":
		print("Video post")
		snippet = lxml.html.fromstring(row['html'])
		videos = snippet.cssselect("._1oak video")
		print(len(videos))
		if len(videos) > 1:
			origNumber = len(videos) - 1
			print("Removing videos")
			videoStr = "videos"
			
			if origNumber == 1:
				videoStr = "video"

			tagString = "<div class='imageCount'>This post originally contained {origNumber} more {videoStr}</div>".format(origNumber=origNumber, videoStr=videoStr)

			for x in range(1, len(videos)):
				el = videos[x].drop_tree()

			videos[0].addnext(lxml.html.fromstring(tagString))
			print("Cleaned")

		cleaned = cleaner.clean_html(snippet)

		if "poster" in snippet.cssselect("._1oad video")[0].attrib:
			cleaned.cssselect("._1oad video")[0].attrib['poster'] = "https://interactive.guim.co.uk/2019/04/fb-ad-images/" + row['vid_image_id']
		cleaned.cssselect("._1oad video")[0].attrib['src'] = ""
		cleaned.cssselect("._7pg4")[0].attrib['src'] = "https://interactive.guim.co.uk/2019/04/fb-ad-images/" + row['av_img_id']

		return(lxml.html.tostring(cleaned))

	else:
		snippet = lxml.html.fromstring(row['html'])
		cleaned = cleaner.clean_html(snippet)
		return(lxml.html.tostring(cleaned))


def getNewAds(today, test):
	
	queryString = "* from ads where dateScraped='{today}'".format(today=today)
	print(queryString)
	queryResult = scraperwiki.sqlite.select(queryString)

	if queryResult:
		for row in queryResult:
			print("================================================================")
			print("New ad from {page_title}".format(page_title=row['page_title']))
			print(row['ad_text'])
			print(row['page_url'])
	else:
		print("No new ads")

#################################################
# Internal functions for modifying the database #
#################################################

def cleanExistingHtml():

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	for row in queryResult:
		row['clean_html'] = cleanHtml(row)
		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")

def modifyVidid():

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	for row in queryResult:
		if row['vid_file_id'] == None:
			row['vid_file_id'] = ""
			time.sleep(0.1)
			scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id"], data=row, table_name="ads")

def updateImageCol():
	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)
	for row in queryResult:
		row['images_uploaded'] = True
		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")	

def updatePartyCol():
	pageJson = requests.get('https://interactive.guim.co.uk/docsdata/1VvyKimrkoQl1CuCMwVgk9zd46Sk72ogyQ50j40EBElw.json').json()['sheets']

	queryString = "* from ads where type='party'"
	queryResult = scraperwiki.sqlite.select(queryString)

	partyLookup = {}

	for row in pageJson['parties']:
		partyLookup[row['page_title']] = row['party']

	print(partyLookup)

	for row in queryResult:
		print(row['page_title'])
		print(partyLookup[row['page_title']])
		row['party'] = partyLookup[row['page_title']]
		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")

def generateImgUrls():

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	for row in queryResult:
		if row['image_url'] != "":
			row['image_id'] = row['image_url'].split("/")[6].split("?")[0]
			print(row['image_id'])
		else:
			row['image_id'] = ""

		if row['vid_image_url']	!= "":
			row['vid_image_id'] = row['vid_image_url'].split("/")[5].split("?")[0]
		else:
			row['vid_image_id'] = ""
			print(row['vid_image_id'])

		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")

def generateAvUrls():

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	for row in queryResult:
		snippet = lxml.html.fromstring(row['html'])
		row['av_img_url'] = snippet.cssselect("._7pg4")[0].attrib['src']
		row['av_img_id'] = row['av_img_url'].split("/")[5].split("?")[0]
		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")

def makeUniqueIDs():

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	# allId = []

	for row in queryResult:
		text = row['page_id'] + row['ad_text'] + row['image_id'] + row['vid_image_id']
		row['unique_id'] = mmh3.hash(text, signed=False)
		# allId.append(row['unique_id'])
		print(row['unique_id'])

		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id","vid_file_id"], data=row, table_name="ads")	

	# print("all", len(allId))
	# print("unique", len(set(allId)))				