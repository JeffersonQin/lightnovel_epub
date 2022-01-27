from __future__ import annotations
import time
import sys
import traceback
import os
import re
from bs4 import BeautifulSoup

from utils import downloader
from utils import echo


DOCUMENT_DOWNLOAD_HEADERS = {
    'accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Content-Type': 'text/html; charset=unicode',
    'accept-encoding':
    'gzip, deflate, br',
    'accept-language':
    'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control':
    'no-cache',
    'pragma':
    'no-cache',
    'sec-ch-ua':
    '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
    'sec-ch-ua-mobile':
    '?0',
    'sec-fetch-dest':
    'document',
    'sec-fetch-mode':
    'navigate',
    'sec-fetch-site':
    'same-origin',
    'sec-fetch-user':
    '?1',
    'upgrade-insecure-requests':
    '1',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'
}

IMAGE_DOWNLOAD_HEADERS = {
    'Accept':
    'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Encoding':
    'gzip, deflate',
    'Accept-Language':
    'zh-CN,zh;q=0.9,en;q=0.8',
    'Host':
    'pic.wenku8.com',
    'Proxy-Connection':
    'keep-alive',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}

DECODE = 'gbk'
ENCODE = 'utf-8'

class BookInfo:
	def __init__(self, aid, cid, title, content=None, href=None) -> None:
		self.aid: str = aid
		self.cid: str = cid
		self.title: str = title
		self.content: str = content
		self.href: str = href


def obtain_article_content(url):
	'''
	download web content
	:param url: url to download
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)

	res = downloader.download_webpage(url, DOCUMENT_DOWNLOAD_HEADERS, DECODE)
	# parse
	try:
		soup = BeautifulSoup(res, 'lxml')
		article = soup.find('article', id='article-main-contents')
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PARSING FAILED')

	echo.pop_subroutine()
	return str(article)


def download_images(content, dump_path):
	"""
	download images from content
	:param content: html content
	:param dump_path: path to dump updated html
	:return:
	"""
	echo.push_subroutine(sys._getframe().f_code.co_name)

	echo.clog(f'Start Parsing Images')

	# parse images
	try:
		soup = BeautifulSoup(content, 'lxml')
		images = soup.find_all('img')
	except Exception as e:
		echo.cerr(f'Error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PARSING FAILED')
	# download images
	try:
		i = 0
		for tag in images:
			i += 1
			echo.clog(f'Processing images: ({i} / {len(images)})')
			# parse
			link = str(tag.attrs['src'])
			if link.startswith('http') or link.startswith('//'):
				file_name = link.split('?')[0].split('/')[-1]
				file_dir = os.path.join(DUMP_PATH, file_name)
				# download
				downloader.download_file(link, file_dir, IMAGE_DOWNLOAD_HEADERS)
				# replace src
				tag.attrs['src'] = os.path.abspath(file_dir)
				# update html
				with open(dump_path, 'w', encoding=ENCODE) as f:
					f.write(str(soup))
		return str(soup)
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('DOWNLOAD FAILED')
	finally:
		echo.pop_subroutine()

def process_article_page(url, dump_path, cvt=None):
    '''
        Process the article page.
        :param url: url to process
        :param dump_path: path to dump html
        :return: string of html content
        '''
    echo.push_subroutine(sys._getframe().f_code.co_name)

    try:
        flag = True
        # obtain html
        if dump_path is not None:
            if os.path.exists(dump_path):
                with open(dump_path, 'r', encoding=ENCODE) as f:
                    content = f.read()
                flag = False
        if flag:
            content = obtain_article_content(url)
            if dump_path is None:
                dump_path = os.path.join(DUMP_PATH, f'./{time.time_ns()}.html')
            with open(dump_path, 'w', encoding=ENCODE) as f:
                f.write(content)
            echo.clog(f'Dumped HTML to {dump_path}')
        # download images
        content = download_images(content, dump_path)

        return content
    except Exception as e:
        echo.cerr(f'error: {repr(e)}')
        traceback.print_exc()
        echo.cexit('PROCESS PAGE FAILED')
    finally:
        echo.pop_subroutine()

def getBookStructure(content: str) -> dict[str, list[BookInfo]]:
	soup = BeautifulSoup(content, 'lxml')
	table = soup.find('table')
	units = table.find_all('td')
	books = {}
	curBook = None
	for unit in units:
		# print(unit.prettify())
		cl = unit.get('class')[0]
		if cl == 'vcss':
			curBook = unit.text
			books[curBook] = []
		elif cl == 'ccss':
			atag = unit.find('a')
			if atag is None:
				continue
			aid = re.search(r'var article_id = "(\S+)"', content)[1]
			cid = re.search(r'var chapter_id = "(\S+)"', content)[1]
			curChapter = BookInfo(aid,
                         cid,
                         href=atag.attrs['href'],
                         title=atag.text)
			if curBook not in books:
				echo.cexit(f'No current book specified: {curChapter}')
			books[curBook].append(curChapter)
	return books


def getContent(content: str) -> BookInfo:
	aid = re.search(r'var article_id = "(\S+)"', content)[1]
	cid = re.search(r'var chapter_id = "(\S+)"', content)[1]
	soup = BeautifulSoup(content, 'lxml')
	title = soup.find('div', id='title').text
	content = soup.find('div', id='contentmain').prettify()
	return BookInfo(aid, cid, title, content)


def get_contents(url, dump_path):
	'''
		Get contents from url.
		:param url: url to process
		:param dump_path: path to dump things
		'''
	global DUMP_PATH
	DUMP_PATH = dump_path

	echo.push_subroutine(sys._getframe().f_code.co_name)

	try:
		assert ('novel' in url) and ('index.htm' in url), 'not wenku8 novel toc page'
		relative = url.replace('index.htm', '')
		content = downloader.download_webpage(url, DOCUMENT_DOWNLOAD_HEADERS, DECODE)
		structure = getBookStructure(content)

		# series
		contents = []
		book_index = 0
		for book in structure.keys():
			echo.clog(f'Processing book {book} {book_index} / {len(structure.keys())}')
			book_index += 1
			ch_index = 0
			for chapter in structure[book]:
				addr = relative + '/' + chapter.href
				chWeb = downloader.download_webpage(addr, DOCUMENT_DOWNLOAD_HEADERS, DECODE)
				chContent = getContent(chWeb)
				ch_index += 1
				echo.clog(f'Processing chapter {ch_index} / {len(structure[book])}')
				a_title = chContent.title
				aid = chContent.cid
				echo.clog(f'Title: {a_title}')
				echo.clog(f'Article ID: {aid}')
				a_dump_path = os.path.join(dump_path, f'{aid}.html')
				with open(a_dump_path, 'w', encoding=ENCODE) as f:
					echo.clog(f'Save content to {a_dump_path}')
					f.write(chContent.content)
				# to call download images
				img_content = process_article_page(None, a_dump_path)
				contents.append({'title': a_title, 'content': img_content})

		return contents
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('GET CONTENTS FAILED')
	finally:
		echo.pop_subroutine()


def get_cover(cover_link, dump_path):
	'''
	Get cover from link.
	:param cover_link: link to cover
	:param dump_path: path to dump cover
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)
	try:
		cover_name = self.cover_link.split('?')[0].split('/')[-1]
		cover_dir = os.path.join(dump_path, cover_name)
		downloader.download_file(self.cover_link, cover_dir, IMAGE_DOWNLOAD_HEADERS)
		return cover_dir
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('GET COVER FAILED')
	finally:
		echo.pop_subroutine()
