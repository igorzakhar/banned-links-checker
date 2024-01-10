import asyncio
import logging
import os
import sys

from textwrap import shorten
from urllib.parse import unquote
from urllib.parse import urlparse

import aiofiles
import aiohttp
import feedparser

from bs4 import BeautifulSoup


async def write_file(filename, links):
    async with aiofiles.open(filename, mode='w') as afp:
        return await afp.write('\n'.join(links))


async def read_file(filename):
    if not (os.path.exists(filename)):
        return []
    async with aiofiles.open(filename, mode='r') as afp:
        content = await afp.read()
        return content.split('\n')


async def fetch_article_urls(session, rss_url):
    async with session.get(rss_url) as response:
        resp_body = await response.text()
        feed = feedparser.parse(resp_body)
        article_urls = [
            entry['id']
            for entry in feed.entries
        ]

        return article_urls


async def extract_links(session, article_url):
    async with session.get(article_url) as response:
        resp_body = await response.text()
        soup = BeautifulSoup(resp_body, 'lxml')
        post_content_body = soup.find('div', {'id': 'post-content-body'})

        title = None
        title_tag = soup.find('h1', {'class': 'tm-title'})
        if title_tag:
            title = title_tag.text

        found_links = None
        if post_content_body:
            a_tag = post_content_body.find_all('a')
            found_links = [
                (link['href'], link.get_text(strip=True))
                for link in a_tag if link.has_attr('href')
            ]

        return {
            'url': article_url,
            'title': title,
            'found_links': found_links
        }


async def collect_hyperlinks(session, article_urls):
    tasks = [
        extract_links(session, article_url) for article_url in article_urls
        if not 'companies' in urlparse(article_url).path.split('/')
    ]

    return await asyncio.gather(*tasks)


def detect_links(links, allowed_tld, allowed_domains):
    detected_links = []
    if links:
        for link in links:
            url = urlparse(link[0])
            tld = ''.join(url.netloc.split('.')[-1:])
            domain = '.'.join(url.netloc.split('.')[-2:]).lower()
            if (url.scheme and tld not in allowed_tld
                    and domain not in allowed_domains
                    and url.scheme != 'mailto'):
                detected_links.append(link)

    return detected_links


def print_results(results, tld, allowed_domains):
    for res in results:
        detected_links = detect_links(res['found_links'], tld, allowed_domains)
        if detected_links:
            title = shorten(res["title"], width=70, placeholder="...»")
            print('-' * 40)
            print(f'Link: {res["url"]}\nTitle: {title}\n')
            for link in detected_links:
                url = urlparse(link[0])
                if url.query:
                    print(f'\u25b6 {link[1]} \u2192 {unquote(link[0])}')
                else:
                    print(f'{link[1]} \u2192 {unquote(link[0])}')


async def main():
    logging.getLogger('charset_normalizer').setLevel(logging.WARNING)

    logging.basicConfig(
        format='%(funcName)s \u2192  %(asctime)s %(message)s',
        level=logging.DEBUG,
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    allowed_tld = await read_file('allowed_domains/tld.txt')
    allowed_domains = await read_file('allowed_domains/domains.txt')

    single_article_url = None
    if len(sys.argv) > 1:
        single_article_url = sys.argv[1]

    filename = 'article_links.txt'
    rss_url = 'https://habr.com/ru/rss/articles/?fl=ru'

    found_urls = []
    async with aiohttp.ClientSession() as session:
        if single_article_url:
            links = await extract_links(session, single_article_url)
            found_urls.append(links)
        else:
            article_urls = await fetch_article_urls(session, rss_url)

            previous_links = await read_file(filename)
            unread = list(set(article_urls).difference(set(previous_links)))

            logging.debug(previous_links)
            logging.debug(list(unread))

            if unread:
                await write_file(filename, article_urls)

                unread_articles = [
                    article_url
                    for article_url in article_urls
                    if article_url in unread
                ]
                found_urls = await collect_hyperlinks(session, unread_articles)

        print_results(found_urls, allowed_tld, allowed_domains)


if __name__ == '__main__':
    asyncio.run(main())
