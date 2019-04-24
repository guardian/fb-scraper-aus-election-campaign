import scraperwiki
import smtplib
from email.mime.text import MIMEText

import os
import arrow

def sendNotifications(today, test):
	
	EMAIL_ALERT_PASSWORD = os.environ['EMAIL_ALERT_PASSWORD']

	fromaddr = "alerts@nickevershed.com"
	recipients = ["nick.evershed@theguardian.com"]
	 
	queryString = "* from ads where dateScraped='{today}'".format(today=today)
	
	lastSent = scraperwiki.sqlite.get_var('lastSent')

	print(lastSent)
	
	queryResult = scraperwiki.sqlite.select(queryString)

	tempQueries = []

	if lastSent:
		lastSentList = lastSent.split()
		for row in queryResult:
			if str(row['unique_id']) not in lastSentList:
				tempQueries.append(row)
	else:
		tempQueries = queryResult			

	newSent = []

	if tempQueries:

		adNumber = len(tempQueries)

		subject = "{adNumber} new facebook ads".format(adNumber=adNumber)

		body = ""
		
		for row in tempQueries:
			body += "<p></p>"
			body += "================================================================<br>"
			body += "<h4>New ad from {page_title}</h4>".format(page_title=row['page_title'])
			body += ("<p>" + row['ad_text']  + "</p>")
			
			if row['image_id'] != "": 
				body += ("<br><a href='{imageUrl}'>image link</a>".format(imageUrl="https://interactive.guim.co.uk/2019/04/fb-ad-images/" + row['image_id']))
			elif row['vid_image_id'] != "":
				body += ("<br><a href='{imageUrl}'>image link</a>".format(imageUrl="https://interactive.guim.co.uk/2019/04/fb-ad-images/" + row['vid_image_id']))	
			
			body += ("<br><a href='{pageUrl}'>page link</a>".format(pageUrl=row['page_url']))
			newSent.append(str(row['unique_id']))
	else:
		subject = "No new facebook ads"
		body = "No new ads, sorry m8"

	msg = MIMEText(body, 'html')

	msg['Subject'] = subject
	msg['From'] = fromaddr
	msg['To'] = ", ".join(recipients)	
	server = smtplib.SMTP_SSL('mail.nickevershed.com', 465)
	server.login(fromaddr, EMAIL_ALERT_PASSWORD)
	text = msg.as_string()
	print(text)
	server.sendmail(fromaddr, recipients, text)
	server.quit()

	scraperwiki.sqlite.save_var('lastSent', ",".join(newSent))	

	print("Email sent")

sendNotifications(arrow.now('Australia/Sydney').strftime('%Y-%m-%d'), True)	