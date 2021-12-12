from lightnovel import LightNovel
import click
import opencc

from utils import echo

echo.init_subroutine()

@click.group()
def cli():
	pass


@cli.command()
@click.option('--title', default=None, help='title of light novel')
@click.option('--authors', default=None, help='(optional) authors\' names, separated by comma (,)')
@click.option('--identifier', default=None, help='(optional) identifier of light novel')
@click.option('--cover_link', default=None, help='(optional) cover_link of light novel. cover_link can either be web link or file path. if it is not beginned with "http", it would be recognized as file path. if nothing was given, then it will use the first picture of webpage.')
@click.option('--cvt', default=None, help='(optional) OpenCC conversion configuration, used to convert between different Chinese characters. you can choose the value from "s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t". if nothing is provided, no conversion would be performed. for more information, please visit: https://github.com/BYVoid/OpenCC')
@click.argument('url')
@click.argument('path')
def download(title: str, authors: str, identifier: str, cover_link: str, cvt: str, url: str, path: str):
	'''
	download the light novel

	ARGUMENTS:\n
	* URL: url of light novel to download\n
	* PATH: directory to store the light novel\n
	'''
	if title is None:
		title = input('Input title of light novel: ')
	if authors is None:
		authors = input('(optional) Input authors\' names, separated by comma (,): ')
	if identifier is None:
		identifier = input('(optional) Input identifier of light novel: ')
	if cover_link is None:
		cover_link = input('(optional) Input cover_link of light novel (see --help for further explanation): ')
	novel = LightNovel(url=url, authors=authors.split(','), identifier=identifier, title=title, cover_link=cover_link)
	novel.download_content()
	if cvt in ["s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t"]:
		converter = opencc.OpenCC(f'{cvt}.json')
		novel.content = converter.convert(novel.content)
	novel.write_epub(path)


if __name__ == '__main__':
	cli()
