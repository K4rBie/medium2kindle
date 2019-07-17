#!/usr/bin/python3
# author: Karol Bieńkowski
# license: GPL v3

from urllib.request import urlopen, Request
import sys, subprocess, os, io
from bs4 import BeautifulSoup
from PIL import Image

hotmail_pass = 'password'
hotmail_adress = 'example@hotmail.com' # which script also assumes is your login, too
kindle_adress = 'example@kindle.com'

def convert ( file_name, author ):
	print("\nFile conversion started...")
	
	subprocess.run(['ebook-convert', file_name+".html", file_name+".mobi", "--no-inline-toc", "--pretty-print", "--output-profile", "kindle", "--mobi-file-type=both", "--enable-heuristics", "--authors", author], stdout=subprocess.DEVNULL)

	print("Conversion successful.")


def send (file_name):
	print("\nSending file to Kindle device...")
	
	calibre_smtp = '--relay smtp.live.com --port 587 --username ' + hotmail_adress + ' --password ' + hotmail_pass + ' --encryption-method TLS ' + hotmail_adress + ' ' + kindle_adress + ' ""'
	subprocess.call(['calibre-smtp', '-a', file_name+".mobi"] + calibre_smtp.split(), stdout=subprocess.DEVNULL)
	
	print("File sent.")


def clean (file_name, n):	
	try:
		for ext in [".html",".mobi"]:	#".html",
			os.remove(file_name+ext)
	except:
		pass
	
	if n == 0:
		return
	
	# you can simplify if you change the way you count imgs
	for i in range(1 , n+1):
		try:
			os.remove('img'+str(i))
		except:
			pass


def draw_line ():
	print('\n' + '_' * 40)


def find_author (page):
	try:
		x = page.find('meta', {'name': 'author'})['content']
	except:
		x = 'unknown'
	
	return x


def find_title (page):
	# TODO: find proper way to get only article title
	title_tag = page.find('meta', {'property': 'twitter:title'})
	
	if title_tag is None:
		#print('\nNo title tag. Trying to extract from article.')
		return page.title_tag.get_text().split('–')[0].split('-')[0]
	else:
		return title_tag['content']
	

def sanitize_images (section, n):
	for image in section.select('img[src]'):
		n += 1
		resource = urlopen(Request(image['src'], None, header))
		#print(image['src'])
		
		if image['src'].split('?')[-1] == 'q=20':
			image.decompose()
			continue
		
		img = Image.open(io.BytesIO(resource.read()))
		width, height = img.size
		
		if width >= 1600 or height >= 1600:
			if width >= height:
				divider = int(width/800)
			else:
				divider = int(height/800)
				
			img = img.resize((int(width/divider), int(height/divider)))
		
		img.save('img'+str(n), 'PNG')
		image['src'] = 'img'+str(n)
			
	return [section, n]


##################################################################

article_links = sys.argv

for article in range(1,len(article_links)):
	url = article_links[article]
	header = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
	
	page_req = Request(url, None, header)
	html = urlopen(page_req).read().decode('utf-8', 'ignore')
	page = BeautifulSoup(html, "lxml")
	
	draw_line()
	
	author = find_author(page)
	title = find_title (page)
	file_name = title

	print("\ntitle: ", file_name, "\nauthor: ", author)
	
	old_design = page.find('div', {'class': 'section-content'}) is not None
	
	if old_design:
		#print ("old design")
		
		for match in page.find_all('div', {'class': 'aspectRatioPlaceholder-fill'}):
			match.decompose()
			
		for match in page.find_all('h1', {'class': 'graf'}):
			match.decompose()
		
		for match in page.find_all('img', {'class': 'graf-dropCapImage'}):
			match.decompose()
		
		page.find('div', {'class': 'uiScale'}).decompose()
		
		sections = page.find_all('div', {'class': 'section-content'})
		
	else:
		#print ("new design")
		try:
			page.find('h1').decompose()
		except:
			pass	
		page.find('svg').parent.parent.parent.parent.decompose()
		
		# you prolly need only the bigger one
		sections = page.find_all('section')[2:4]
	
	g = open(file_name+'.html', 'w')
	g.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"><html lang="en"><head><title>' + title + '</title><meta http-equiv="content-type" content="text/html; charset=utf-8"/></head><body><div>')
	
	n = 0
	article_len = 0 
	for section in sections:
		[section, n] = sanitize_images(section, n)
		article_len += len(section.get_text())
		g.write(section.prettify(formatter="html"))
		
		for image in section.select('img[src]'):
			image.wrap(page.new_tag("div"))
			
		for figure in section.select('figure'):
			figure.replace_with(page.new_tag("div"))

	g.write('</div></body></html>')
	g.close()
	

	if article_len < 1050:
		print("Article is too short, probably partial, not sending.")
		clean (file_name, n)
	else:
		convert ( file_name, author )
		send (file_name)
		clean (file_name, n)
