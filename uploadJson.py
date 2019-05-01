# adds the results to s3 

import boto3
import os
import io
import scraperwiki
import time
import simplejson as json
import gzip
import pandas as pd

def uploadJson(test):
	AWS_KEY = os.environ['AWS_KEY_ID']
	AWS_SECRET = os.environ['AWS_SECRET_KEY']

	queryString = "* from ads"
	queryResult = scraperwiki.sqlite.select(queryString)

	pd.DataFrame(queryResult).to_csv('fb-data.csv.gz',compression='gzip')

	remove = ["html", "verified", "image_url", "vid_image_url", "image_id", "vid_image_id", "images_uploaded", "av_img_url", "av_img_id","start_date"]

	for result in queryResult:
		for s in remove:
			del result[s]

	results = json.dumps(queryResult, indent=4)

	with open('fb-data.json','w') as fileOut:
			fileOut.write(results)
			
	if not test:		
		print("Uploading JSON to S3")
		bucket = 'gdn-cdn'
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		)
		s3 = session.resource('s3')
		key = "2019/04/fb-ad-data/fd-data.json"
		object = s3.Object(bucket, key)
		object.put(Body=results, CacheControl="max-age=300", ACL='public-read')
		print("Done")

		print("Uploading CSV to S3")
		key2 = "2019/04/fb-ad-data/fb-data.csv.gz"
		s3.meta.client.upload_file('fb-data.csv.gz', bucket, key2, ExtraArgs={"CacheControl":"max-age=300", 'ACL':'public-read'})
		print("Done")		