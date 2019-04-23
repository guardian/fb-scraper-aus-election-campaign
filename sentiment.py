import scraperwiki
from textblob import TextBlob
import csv

queryString = "* from ads"
queryResult = scraperwiki.sqlite.select(queryString)

data = []

for row in queryResult:
	new = {}
	text = ""
	if row['ad_text'] != "":
		text = text + row['ad_text']

	if row['imageText'] != "":
		text = text + row['imageText']

	if text != "":
		text = text.lower().replace("like","").replace("share","")
		new['text'] = text
		sentiment = TextBlob(text).sentiment
		new['sentiment'] = sentiment[0]
		new['subjectivity'] = sentiment[1]
		new['party'] = row['party']
		new['type'] = row['type']
		data.append(new)
		print(text)
		print(sentiment)


with open('sentiment.csv', 'w') as f:
	w = csv.DictWriter(f, ['text','sentiment','subjectivity','party','type'])
	w.writeheader()
	w.writerows(data)