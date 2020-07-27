import requests
from bs4 import BeautifulSoup
from excel import createSheet, appendSheet
import os
from config import track_check, track


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}

page_no = 1
count = 1
while True:
	url = "https://www.trendmicro.com/vinfo/us/security/research-and-analysis/research/page/"+str(page_no)
	print(url)
	r = requests.get(url, headers=headers)
	if r == 404:
		print(r.status_code)
		break
	soup = BeautifulSoup(r.text, features="html.parser")

	finalDict = {}
	web_url = 'https://www.trendmicro.com'
	for div in soup.find_all('div', {'class': 'enclose'}):
		# Fetching Relevant Data from single page
		h3 = div.find('h3')
		title = h3.text
		link = h3.find('a').get('href')
		if track_check("tracking.json", link):
			count += 1
			continue
		description = div.find('div', {'class': 'blurbEntry'}).text
		finalDict.update({'sr. no.': count, 'title': title, 'description': description, 'company_name': 'Trend Micro', 'web_url': web_url, 'category': 'Information Technology'})

		# Requesting the real inner pages
		try:
			inner_r = requests.get(web_url+link, headers=headers)
		except:
			continue
		inner_soup = BeautifulSoup(inner_r.text, features="html.parser")
		white_paper_link = None

		# Fetching the PDF/WhitePaper Link
		date = inner_soup.find('div', {'id': 'datePub'}).text
		date = date.split(',')[1].strip()
		finalDict.update({'published_date': date})

		for anchor in inner_soup.find_all('a'):
			if anchor.get('href') is not None:
				if 'pdf' in anchor.get('href') and 'asset' in anchor.get('href') or 'white_paper' in anchor.get('href'):
					white_paper_link = anchor.get('href')

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
		track("tracking.json", link)
	page_no += 1

