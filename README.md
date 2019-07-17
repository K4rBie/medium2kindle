# medium2kindle
Script for sending Medium.com articles to Your Kindle device. 

It tries to keep images and text formatting, adds basic file tags like article author and title and resizes images to sane values.

It was tested on python 3.7, basic 8th gen Kindle and modern Linux distro, but Kindle seems to be a fussy beast so no warraty given.

## Requirements
- Python3 and packages
  - BeautifulSoup4
  - PIL
- Calibre 
- hotmail e-mail account for sending files from
- Kindle device e-mail - every device gets one, make sure it has hotmail account whitelisted

## Instalation / Usage
- Simply copy medium2kindle.py file to your local folder. Make sure nothing else is there, because script creates and removes some files so it may remove something by mistake.
- insert you e-mail adresses and password in variables in script. I know, not the safest way, use junk mail or sth. 
- make script executable
- find interesting article on medium.com and copy its URL
- the script can take many article links at once:

````./medium2kindle.py your_article_url another_article_url````
