import scraperwiki
import smtplib
from email.mime.text import MIMEText
import os
import arrow
import io
from pybars import Compiler
import boto3

def sendNotifications(today, test):
	
	with io.open("latest.html", 'r', encoding='utf-8') as tempSource:
		compiler = Compiler()
		template = compiler.compile(tempSource.read())

	EMAIL_ALERT_PASSWORD = os.environ['EMAIL_ALERT_PASSWORD']
	AWS_KEY = os.environ['AWS_KEY_ID']
	AWS_SECRET = os.environ['AWS_SECRET_KEY']
	
	fromaddr = "alerts@nickevershed.com"
	recipients = ["nick.evershed@theguardian.com"]
	print("Checking if there are new ads")
	queryString = "* from ads where dateScraped='{today}'".format(today=today)
	
	lastSent = scraperwiki.sqlite.get_var('lastSent')
	
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
		# print(tempQueries)
		adNumber = len(tempQueries)

		subject = "{adNumber} new facebook ads".format(adNumber=adNumber)
		print(subject)

		body = "{adNumber} new facebook ads, see them <a href='https://interactive.guim.co.uk/2019/04/fb-ad-data/latest.html'>here</a>".format(adNumber=adNumber)
		
		output = template(tempQueries)
		print(output)

		for row in tempQueries:
			newSent.append(str(row['unique_id']))

		if not test:		
			print("Uploading HTML to S3")
			bucket = 'gdn-cdn'
			session = boto3.Session(
			aws_access_key_id=AWS_KEY,
			aws_secret_access_key=AWS_SECRET,
			)
			s3 = session.resource('s3')
			key = "2019/04/fb-ad-data/latest.html"
			object = s3.Object(bucket, key)
			object.put(Body=output, CacheControl="max-age=300", ACL='public-read',ContentType='text/html')
			print("Done")

	else:
		subject = "No new facebook ads"
		body = "No new ads, sorry m8"
		print(subject)

	if not test:	
		msg = MIMEText(body, 'html')
		msg['Subject'] = subject
		msg['From'] = fromaddr
		msg['To'] = ", ".join(recipients)	
		server = smtplib.SMTP_SSL('mail.nickevershed.com', 465)
		server.login(fromaddr, EMAIL_ALERT_PASSWORD)
		text = msg.as_string()
		print("Sending email")
		server.sendmail(fromaddr, recipients, text)
		server.quit()
		print("Email sent")
	
		scraperwiki.sqlite.save_var('lastSent', ",".join(newSent))


# sendNotifications(arrow.now('Australia/Sydney').strftime('%Y-%m-%d'), False)	

