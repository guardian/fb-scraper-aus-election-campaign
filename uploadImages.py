# mirrors the images on s3

import boto3
import os
import io
from concurrent.futures import ThreadPoolExecutor
import scraperwiki
import time

def runUpload():
	AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
	AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

	queryString = "* from ads where images_uploaded IS NULL"
	queryResult = scraperwiki.sqlite.select(queryString)

	images = set()

	for row in queryResult:
		if row['av_img_id'] != "":
			images.add(row['av_img_id'])
		if row['image_id'] != "":
			images.add(row['image_id'])
		if row['vid_image_id'] != "":
			images.add(row['vid_image_id'])

	images_list = list(images)

	print("uploading", len(images_list), "files")
	# test = ['57617685_385077462333660_5324670939118436352_n.jpg','57673908_1212642335578164_9122860954495746048_n.jpg']

	def upload(fileName):

		print("Connecting to S3")
		bucket = 'gdn-cdn'
		session = boto3.Session(
	    aws_access_key_id=AWS_KEY,
	    aws_secret_access_key=AWS_SECRET,
		)
		filePath = "imgs/" + fileName
		s3 = session.resource('s3')
		key = "2019/04/fb-ad-images/" + fileName
		s3.meta.client.upload_file(filePath, bucket, key, ExtraArgs={"CacheControl":"max-age=300", 'ACL':'public-read'})
		print("Uploaded ", filePath)

	pool = ThreadPoolExecutor(max_workers=10)

	for filename in images_list:
		pool.submit(upload,filename)

	for row in queryResult:
		print("Updating database")
		row['images_uploaded'] = 1
		time.sleep(0.1)
		scraperwiki.sqlite.save(unique_keys=["page_id","ad_text","image_url","vid_image_url"], data=row, table_name="ads")	
