# -*- coding: utf-8 -*-


import re
import urllib
import datetime

import requests
from lxml import html


class BasicInfo(dict):
    """Basic info about the camp fetched from tabory.cz.

    You can access data in following way::

        >>> bi = BasicInfo()
        >>> bi['senior'].keys()  # junior/senior camp
        ['age_from', 'age_to', 'starts_at', 'ends_at',
         'topic', 'fb_url', 'book_url', 'price']

    Ages and ``price`` are numbers. ``starts_at`` and ``ends_at`` are
    regular :class:`datetime.date` objects. ``topic`` is string,
    ``fb_url`` is URL of Facebook page, ``book_url`` is URL to use
    for booking.

    Both parsed data and HTTP requests are cached.
    """

    _url = 'http://www.tabory.cz/lokalita/letni-tabory-cr/varvazov/'
    _redirect = 'http://www.tabory.cz/externi.php?p='

    def __init__(self):
        resp = requests.get(self._url)
        resp.raise_for_status()
        data = self._parse(resp.content)
        self.update(data or {})

    def _parse(self, contents):
        dom = html.fromstring(contents)
        rows = []

        # get all TR elements containing a string 'Gál'
        query = u"//text()[contains(.,'Gál')]/ancestor::tr[1]"

        for tr in dom.xpath(query):
            starts_at, ends_at = self._parse_date(tr[0])
            age_from, age_to = self._parse_age(tr[1])

            book_url = self._parse_url(tr[6])
            camp_id = self._parse_id(book_url)

            topic = self._parse_topic(tr[4])
            details_url = self._parse_details_url(dom, topic)
            poster_url = self._parse_poster_url(details_url)

            departure_url = self._create_url('odjezdy.php', camp_id)

            rows.append({
                'id': camp_id,
                'age_from': age_from,
                'age_to': age_to,
                'starts_at': starts_at,
                'ends_at': ends_at,
                'topic': topic,
                'fb_url': self._parse_url(tr[3]),
                'details_url': details_url,
                'book_url': book_url,
                'poster_url': poster_url,
                'departure_url': departure_url,
                'price': self._parse_price(tr[5]),
            })

        if rows[0]['age_from'] < rows[1]['age_from']:
            return {'junior': rows[0], 'senior': rows[1]}
        return {'junior': rows[1], 'senior': rows[0]}

    def _remove_redirect(self, url):
        if self._redirect in url:
            url = url.replace(self._redirect, '')
            url = urllib.unquote(url)
        return url

    def _create_url(self, filename, camp_id):
        return ('http://www.tabory.cz/{0}?'
                'zajezd_id={1}').format(filename, camp_id)

    def _parse_age(self, cell):
        # get two clusters of numbers
        return map(int, re.findall(r'\d+', cell.text))

    def _parse_date(self, cell):
        # get five clusters of numbers
        results = map(int, re.findall(r'\d+', cell.text))
        start_day, start_month, end_day, end_month, year = results

        year = 2000 + year if year < 2000 else year

        starts_at = datetime.date(year, start_month, start_day)
        ends_at = datetime.date(year, end_month, end_day)
        return starts_at, ends_at

    def _parse_url(self, cell):
        a = cell.xpath('.//a')[0]  # find fist A element
        url = a.get('href')  # get its href attribute
        return self._remove_redirect(url)

    def _parse_poster_url(self, poster_page_url):
        resp = requests.get(poster_page_url)
        resp.raise_for_status()
        dom = html.fromstring(resp.content)

        for img in dom.xpath(".//*[@id='main_col']//img"):
            try:
                link = next(img.iterancestors(tag='a'))
            except StopIteration:
                pass
            return link.get('href')
        return None

    def _parse_details_url(self, dom, topic):
        for link in dom.xpath(".//*[@id='main_menu']//a"):
            text = (link.text_content() or '').strip()
            if text and text == topic:
                return link.get('href')
        return None

    def _parse_price(self, cell):
        # get the first cluster of numbers
        price = re.search(r'\d+', cell.text).group(0)
        return int(price)

    def _parse_topic(self, cell):
        texts = cell.xpath('.//text()')
        return ' '.join(texts).strip()

    def _parse_id(self, url):
        return int(re.search(r'id=(\d+)', url).group(1))
