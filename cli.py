from lightnovel import LightNovel
import click
import time
import sys
import traceback
import os
import requests
import opencc
from bs4 import BeautifulSoup

from utils import downloader
from utils import echo


DUMP_PATH = './dump'


echo.init_subroutine()


def download_content(url):
	'''
	download web content
	:param url: url to download
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)

	echo.clog(f'start downloading: {url} => memory')
	# download
	try:
		res = requests.get(url=url, headers={
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
			'cache-control': 'no-cache',
			'pragma': 'no-cache',
			'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'document',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-user': '?1',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'
		}).text
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('DOWNLOAD FAILED')
	# parse
	try:
		soup = BeautifulSoup(res, 'lxml')
		article = soup.find('article', id='article-main-contents')
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PARSING FAILED')

	return str(article)
	echo.pop_subroutine()


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
				downloader.download_file(link, file_dir)
				# replace src
				tag.attrs['src'] = os.path.abspath(file_dir)
				# update html
				with open(dump_path, 'w', encoding='utf-8') as f:
					f.write(str(soup))
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('DOWNLOAD FAILED')


@click.group()
def cli():
	pass


@cli.command()
@click.option('--dump-path', type=click.Path(exists=True), default='./dump', help='directory for dumping')
@click.option('--html-dump', type=click.Path(exists=True), default=None, help='html content dump file path')
@click.option('--title', default=None, help='title of light novel')
@click.option('--authors', default=None, help='authors\' names, separated by comma (,)')
@click.option('--identifier', default=None, help='identifier of light novel')
@click.option('--cover-link', default=None, help='cover_link of light novel. cover_link can either be web link or file path. if it is not beginned with "http", it would be recognized as file path. if nothing was given, then it will use the first picture of webpage.')
@click.option('--cvt', default=None, help='OpenCC conversion configuration, used to convert between different Chinese characters. you can choose the value from "s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t". if nothing is provided, no conversion would be performed. for more information, please visit: https://github.com/BYVoid/OpenCC')
@click.option('--path', type=click.Path(exists=True), default='./', help='directory for saving the light novel')
@click.argument('url')
def download(dump_path, 
			html_dump, 
			title: str, 
			authors: str, 
			identifier: str, 
			cover_link: str, 
			cvt: str, 
			path: str, 
			url: str):
	'''
	download the light novel
	:param dump_path: directory for dumping
	:param html_dump: html content dump file path
	:param title: title of light novel
	:param authors: authors' names, separated by comma (,)
	:param identifier: identifier of light novel
	:param cover_link: cover_link of light novel. cover_link can either be web link or file path. if it is not beginned with "http", it would be recognized as file path. if nothing was given, then it will use the first picture of webpage.
	:param cvt: OpenCC conversion configuration, used to convert between different Chinese characters. you can choose the value from "s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t". if nothing is provided, no conversion would be performed. for more information, please visit: https://github.com/BYVoid/OpenCC
	:param path: directory for saving the light novel
	:param url: url of light novel
	:return: None
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)
	global DUMP_PATH
	DUMP_PATH = dump_path

	try:
		# init directory
		if not os.path.exists(dump_path):
			os.mkdir(dump_path)
		# obtain html
		if html_dump is not None:
			with open(html_dump, 'r', encoding='utf-8') as f:
				content = f.read()
		else:
			content = download_content(url)
			html_dump = os.path.join(DUMP_PATH, f'./{time.time_ns()}.html')
			with open(html_dump, 'w', encoding='utf-8') as f:
				f.write(content)
			echo.clog(f'Dumped HTML to {html_dump}')
		# download images
		download_images(content, html_dump)

		if title is None:
			title = input('Input title of light novel: ')
		if authors is None:
			authors = input('(optional) Input authors\' names, separated by comma (,): ')
		if identifier is None:
			identifier = input('(optional) Input identifier of light novel: ')
		if cover_link is None:
			cover_link = input('(optional) Input cover_link of light novel (see --help for further explanation): ')
		novel = LightNovel(url=url, authors=authors.split(','), identifier=identifier, title=title, cover_link=cover_link)
		novel.content = content

		if cvt in ["s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t"]:
			converter = opencc.OpenCC(f'{cvt}.json')
			novel.content = converter.convert(novel.content)
		
		novel.write_epub(path)
	except Exception as e:
		echo.cerr(f'Error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('DOWNLOAD LIGHTNOVEL FAILED')
	finally:
		echo.pop_subroutine()


if __name__ == '__main__':
	cli()
