# gets page ID and title from a facebook page URL 

import requests
import lxml.html
import scraperwiki
import simplejson as json

pages = requests.get('https://interactive.guim.co.uk/docsdata/1VvyKimrkoQl1CuCMwVgk9zd46Sk72ogyQ50j40EBElw.json').json()['sheets']

def checkText(text):
	if 'require":[["CurrentPage","init",[],' in text:
		return True
	else:
		return False	

for page in pages['various']:
	data = {}
	print("Getting", page['page_url'])
	r = requests.get(page['page_url'])
	if checkText(r.text):
		pageInfo = r.text.split('require":[["CurrentPage","init",[],')[1].split('],["PagesNuxFrameworkHelper')[0]
		print(pageInfo)
		pageInfoJson = json.loads(pageInfo.replace("\\",""))
		print(pageInfoJson[0]['pageName'])

		data['page_title'] = pageInfoJson[0]['pageName']
		data['page_id'] = pageInfoJson[0]['pageID']
		data['page_url'] = page['page_url']
		data['type'] = page['type']
		data['tags'] = page['tags']
		data['anonymous'] = page['anonymous']
		data['verified'] = page['verified']

		scraperwiki.sqlite.save(unique_keys=["page_url"], data=data, table_name="data")
	else:
		print("Page no longer exists")	

for page in pages['parties']:
	data = {}
	print("Getting", page['page_url'])
	r = requests.get(page['page_url'])
	if checkText(r.text):
		pageInfo = r.text.split('require":[["CurrentPage","init",[],')[1].split('],["PagesNuxFrameworkHelper')[0]
		print(pageInfo)
		pageInfoJson = json.loads(pageInfo.replace("\\",""))
		print(pageInfoJson[0]['pageName'])

		data['page_title'] = pageInfoJson[0]['pageName']
		data['page_id'] = pageInfoJson[0]['pageID']
		data['page_url'] = page['page_url']
		data['type'] = page['type']
		data['verified'] = page['verified']
		scraperwiki.sqlite.save(unique_keys=["page_url"], data=data, table_name="data")
	else:
		print("Page no longer exists")

for page in pages['politicians']:
	data = {}
	print("Getting", page['page_url'])
	r = requests.get(page['page_url'])
	if checkText(r.text):
		pageInfo = r.text.split('require":[["CurrentPage","init",[],')[1].split('],["PagesNuxFrameworkHelper')[0]
		print(pageInfo)
		pageInfoJson = json.loads(pageInfo.replace("\\",""))
		print(pageInfoJson[0]['pageName'])

		data['page_title'] = pageInfoJson[0]['pageName']
		data['page_id'] = pageInfoJson[0]['pageID']
		data['page_url'] = page['page_url']
		data['name'] = page['name']
		data['party'] = page['party']
		data['verified'] = page['verified']
		data['house'] = page['house']
		data['type'] = page['type']
		scraperwiki.sqlite.save(unique_keys=["page_url"], data=data, table_name="data")
	else:
		print("Page no longer exists")

queryString = "* from data"
queryResult = scraperwiki.sqlite.select(queryString)
queryJson = json.dumps(queryResult, indent=4)

with open('facebookPages.json','w') as fileOut:
	fileOut.write(queryJson)	

