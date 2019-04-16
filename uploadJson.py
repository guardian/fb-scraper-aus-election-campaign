# adds the results to s3 

import boto3
import os
import io
import scraperwiki
import time
import simplejson as json

def uploadJson():
	AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
	AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	remove = ["html", "verified", "image_url", "vid_image_url", "image_id", "vid_image_id", "images_uploaded", "av_img_url", "av_img_id",]

	for result in queryResult:
		for s in remove:
			del result[s]

	results = json.dumps(queryResult)

	with open('fb-ads.json','w') as fileOut:
			fileOut.write(results)

	print("Connecting to S3")
	bucket = 'gdn-cdn'
	session = boto3.Session(
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
	)
	s3 = session.resource('s3')
	key = "2019/04/fb-ad-data/fd-ads.json"
	object = s3.Object(bucket, key)
	object.put(Body=results, CacheControl="max-age=300", ACL='public-read')
	print("Uploaded json")