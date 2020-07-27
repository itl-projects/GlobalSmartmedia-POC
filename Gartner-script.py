import requests
from bs4 import BeautifulSoup
from excel import createSheet, appendSheet
import os
from config import track_get_no, track_check, track

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}
url = "https://www.gartner.com/ngw/syspath-bin/gartner/dynamiccontent?requestType=select-by-tags&designType=tiles&nPage=1&pageSize=254&languageCode=en&showLocalizedContent=false&filterCodes=&randomSeed=&tagType=emt:page/content-type&currentPagePath=/en/information-technology/research/research-index&tags=emt%3Apage%2Ftype%2Fresearch%2Cemt%3Apage%2Ftype%2Fspecial-reports&filterTags=emt%3Apage%2Ffunction%2Fit&excludeFilterTags=emt%3Apage%2Fcontent-type%2Fpremium-research%2Cemt%3Apage%2Fcontent-type%2Fpurchase-research"

web_url = 'https://www.gartner.com'
r = requests.get(url, headers=headers)
data = r.json()

data_list = data['data']['docs']
finalDict = {}

count = track_get_no("tracking.json") + 1

for article in data_list:

	if track_check("tracking.json", article['url']):
			# count += 1
			continue

	url = web_url + article['url']
	title = article['title']

	description = article['allFields']['description']
	publish_date = article['date'].split(',')[1]

	finalDict.update({'sr. no.': count, 'title': title, 'description': description, 'company_name': 'Gartner', 'web_url': web_url, 'category': 'Information Technology'})
	finalDict.update({'published_date': publish_date})

	inner_r = requests.get(url, headers=headers)
	inner_soup = BeautifulSoup(inner_r.text, features="html.parser")

	white_paper_link = None

	for anchor in inner_soup.find_all('a'):
			if anchor.get('href') is not None:
				if 'pdf' in anchor.get('href') and 'asset' in anchor.get('href'):
					white_paper_link = anchor.get('href')

	if white_paper_link is None:
		temp_link = article['url'].split('/')[-1]+'.pdf'
		dr = requests.get('https://emtemp.gcom.cloud/ngw/globalassets/en/doc/documents/'+temp_link, headers=headers)
		if dr.status_code == "200" or dr.status_code == 200:
			white_paper_link = 'https://emtemp.gcom.cloud/ngw/globalassets/en/doc/documents/'+temp_link

	if white_paper_link is None:
		continue

	print('Downloading White Paper:', white_paper_link.split('/')[-1])
	try:
		pdf = requests.get(white_paper_link, allow_redirects=True)
	except:
		continue
	if not os.path.exists('white papers'):
		os.mkdir('white papers')
	path = 'white papers/'+str(count)+'_'+white_paper_link.split('/')[-1]
	if '?' in path:
		path = path.split('?')[0]
	with open(path, 'wb') as f:
		f.write(pdf.content)

	sheet_name = 'whitepapers_data.xlsx'
	if not os.path.exists(sheet_name):
		createSheet(sheet_name, finalDict)
		appendSheet(sheet_name, finalDict)
	else:
		appendSheet(sheet_name, finalDict)
	print("Appended to sheet for", title)
	count += 1
	track("tracking.json", article['url'])


