import asyncio
import logging
import os

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


async def fetch_articles(session, rss_url):
    async with session.get(rss_url) as response:
        resp_body = await response.text()
        feed = feedparser.parse(resp_body)
        articles = [
            (entry['id'], entry['title'])
            for entry in feed.entries
        ]
        return articles


async def extract_links(session, article):
    url, title = article
    async with session.get(url) as response:
        resp_body = await response.text()
        soup = BeautifulSoup(resp_body, 'lxml')
        post_content_body = soup.find('div', {'id': 'post-content-body'})

        found_links = None
        if post_content_body:
            a_tag = post_content_body.find_all('a')
            found_links = [
                (link['href'], link.get_text(strip=True))
                for link in a_tag if link.has_attr('href')
            ]

        return {
            'url': url,
            'title': title,
            'found_links': found_links
        }


async def collect_hyperlinks(session, articles):
    tasks = [
        extract_links(session, article) for article in articles
        if not 'companies' in urlparse(article[0]).path.split('/')
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
    logging.basicConfig(
        format='%(funcName)s \u2192  %(asctime)s %(message)s',
        level=logging.DEBUG,
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    allowed_tld = await read_file('allowed_domains/tld.txt')
    allowed_domains = await read_file('allowed_domains/domains.txt')

    filename = 'article_links.txt'
    rss_url = 'https://habr.com/ru/rss/articles/?fl=ru'

    async with aiohttp.ClientSession() as session:
        articles = await fetch_articles(session, rss_url)

        previous_links = await read_file(filename)
        current_links = [item[0] for item in articles]
        unread = list(set(current_links).difference(set(previous_links)))

        logging.debug(previous_links)
        logging.debug(list(unread))

        if unread:
            await write_file(filename, current_links)

            unread_articles = [
                article
                for article in articles
                if article[0] in unread
            ]
            results = await collect_hyperlinks(session, unread_articles)

            print_results(results, allowed_tld, allowed_domains)


if __name__ == '__main__':
    asyncio.run(main())
