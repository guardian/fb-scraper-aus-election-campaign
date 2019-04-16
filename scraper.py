import requests
import lxml.html
import scraperwiki
from datetime import datetime
from datetime import timedelta
import simplejson as json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import pickle
from selenium.webdriver import DesiredCapabilities
import random
import updates
import utilities

# pagesFile = open('facebookPages.json')
# pages = json.load(pagesFile)

# pagesFile = open('majorParties.json')
# pages = json.load(pagesFile)

def runScraper():
	pageJson = requests.get('https://interactive.guim.co.uk/docsdata/1VvyKimrkoQl1CuCMwVgk9zd46Sk72ogyQ50j40EBElw.json').json()['sheets']

	pages = []

	for row in pageJson['various']:
		row['name'] = ""
		row['party'] = ""
		row['house'] = ""
		pages.append(row)

	for row in pageJson['parties']:
		row['tags'] = ""
		row['anonymous'] = ""
		row['house'] = ""
		row['party'] = ""
		pages.append(row)

	for row in pageJson['politicians']:
		row['tags'] = ""
		row['anonymous'] = ""
		pages.append(row)

	options = Options()
	options.headless = True
	upto = 0

	driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)

	dateScraped = datetime.strftime(datetime.now(), '%Y-%m-%d')


	for x in range(upto,len(pages)):

		page = pages[x]

		print("up to", x)
		# https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=AU&q=Liberal%20Party%20of%20Australia&view_all_page_id=13561467463
		url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=AU&q={name}&view_all_page_id={id}".format(name=page['page_title'],id=page['page_id'])
		print("getting", url)	
		driver.get(url)
		# check if results
		def scrollAndWait():
			print("Scroll and wait")
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(3)

		scrollAndWait()	

		if "There are no ads that match your search criteria." not in driver.page_source:
			
			dom = lxml.html.fromstring(driver.page_source)
			# print(driver.page_source)
			try:
				ad_number = dom.cssselect('._7gn2 div')[0].text.replace("~","").replace(" results","").replace(" result","")
			except:
				print(driver.page_source)
				
			ad_number = int(ad_number)
			print(ad_number, "ads")
			runTimes = round(ad_number/15)

			for _ in range(runTimes):
				scrollAndWait()				

			dom = lxml.html.fromstring(driver.page_source)
			ad_elements = dom.cssselect('._7owt')
			# # print(ad)

			for ad_element in ad_elements:
				data = {}
				data['html'] = lxml.html.tostring(ad_element)
				# print(data['html'])

				maintext = ad_element.cssselect("._7jyr ._4ik6")
			
				if len(maintext) > 0:
					data['ad_text'] = maintext[0].text_content()
				else:
					data['ad_text'] = ""

				data['start_date'] = ad_element.cssselect("._7jwu")[0].text_content()
				# print(data['ad_text'])
				data['page_title'] = page['page_title']
				data['page_id'] = page['page_id']
				data['page_url'] = page['page_url']
				data['type'] = page['type']
				data['tags'] = page['tags']
				data['anonymous'] = page['anonymous']
				data['verified'] = page['verified']
				data['name'] = page['name']
				data['party'] = page['party']
				data['house'] = page['house']
				data['dateScraped'] = dateScraped

				data['image_url'] = ""
				data['image_id'] = ""

				images = ad_element.cssselect("._7jys")

				if len(images) > 0:
					data['image_url'] = images[0].attrib['src']
					data['image_id'] = images[0].attrib['src'].split("/")[6].split("?")[0]

				data['vid_image_url'] = ""
				data['vid_image_id'] = ""

				vid_images = ad_element.cssselect("._1oak video")

				if len(vid_images) > 0:
					data['vid_image_url'] = vid_images[0].attrib['poster']
					data['vid_image_id'] = vid_images[0].attrib['poster'].split("/")[5].split("?")[0]

				data['av_img_url'] = ""
				data['av_img_id'] = ""	

				av_images = ad_element.cssselect("._7pg4")

				if len(av_images) > 0:	
					data['av_img_url'] = av_images[0].attrib['src']
					data['av_img_id'] = data['av_img_url'].split("/")[5].split("?")[0]

				data['clean_html'] = utilities.cleanHtml(data)	

				# check if it has been scraped before

				queryString = "* from ads where page_id='{page_id}' and ad_text='{ad_text}' and image_id='{image_id}' and vid_image_id='{vid_image_id}'".format(page_id=data['page_id'], ad_text=data['ad_text'].replace("'", "''"), image_id=data['image_id'], vid_image_id=data['vid_image_id'])
				queryResult = scraperwiki.sqlite.select(queryString)
				
				# if it hasn't been scraped before, save the values in the main table

				if not queryResult:
					print("new ad")
					scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_id","vid_image_id"], data=data, table_name="ads")
				else:
					print("No updates")
					# print(queryResult[0]['ad_text'])
					# print(data['ad_text'])

		else:
			print("No ads found")			

	driver.close()