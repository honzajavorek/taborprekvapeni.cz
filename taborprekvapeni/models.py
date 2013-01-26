# -*- coding: utf-8 -*-


import os
import re
import urllib
import datetime
import itertools
from lxml import html

from taborprekvapeni import app, http
from taborprekvapeni.cache import cache


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
        data = cache(self.__class__.__name__, self._fetch)
        self.update(data)

    def _fetch(self):
        return self._parse(http.get(self._url))

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

    def _parse_price(self, cell):
        # get the first cluster of numbers
        price = re.search(r'\d+', cell.text).group(0)
        return int(price)

    def _parse_topic(self, cell):
        texts = cell.xpath('.//text()')
        return ' '.join(texts).strip()

    def _parse_id(self, url):
        return int(re.search(r'id=(\d+)', url).group(1))

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

            poster_url = self._create_url('upoutavka.php', camp_id)
            departure_url = self._create_url('odjezdy.php', camp_id)

            rows.append({
                'id': camp_id,
                'age_from': age_from,
                'age_to': age_to,
                'starts_at': starts_at,
                'ends_at': ends_at,
                'topic': self._parse_topic(tr[4]),
                'fb_url': self._parse_url(tr[3]),
                'book_url': book_url,
                'poster_url': poster_url,
                'departure_url': departure_url,
                'price': self._parse_price(tr[5]),
            })

        if rows[0]['age_from'] < rows[1]['age_from']:
            return {'junior': rows[0], 'senior': rows[1]}
        return {'junior': rows[1], 'senior': rows[0]}


class HistoryText(unicode):

    _dir = os.path.join(app.root_path, 'texts')
    _place_re = re.compile(r'\(([^\)]+)\)$')

    def __new__(cls, year):
        # get the text
        filename = 'history{0}.md'.format(year)
        path = os.path.join(cls._dir, filename)
        try:
            with open(path) as f:
                text = f.read().strip().decode('utf-8')
        except IOError:
            text = ''

        title = None
        place = None

        # find title
        lines = []
        for line in text.splitlines():
            if line.startswith('# '):
                title = line[2:]
            else:
                lines.append(line)
        text = '\n'.join(lines)

        # parse out place
        match = cls._place_re.search(title)
        if match:
            place = match.group(1)
            title = cls._place_re.sub('', title).strip()

        # set properties
        obj = unicode.__new__(cls, text)
        obj.title = title
        obj.place = place
        obj.year = int(year)
        return obj

    @classmethod
    def find_all(cls):
        texts = []
        for basename in os.listdir(cls._dir):
            if basename.startswith('history'):
                year = int(basename[7:11])  # historyXXXX.md
                text = cls(year)
                texts.append(text)
        return sorted(texts, key=lambda t: t.year, reverse=True)


class PhotoAlbums(dict):

    _url = 'http://hlavas.rajce.idnes.cz/'
    _camp_re = re.compile(u't[áa]bor\D{0,3}(\d{4}|\d{2})', re.I)

    def __init__(self):
        data = self._fetch()  # cache(self.__class__.__name__, self._fetch)
        self.update(data)

    def _is_camp_specific(self, album):
        return bool(self._camp_re.search(album.text))

    def _is_secure(self, album):
        return 'secure' in album.get('class').split()

    def _parse_year(self, album):
        year = int(self._camp_re.search(album.text).group(1))
        if year < 90:
            return 2000 + year
        if year < 100:
            return 1900 + year
        return year

    def _parse_url(self, album):
        return album.get('href')

    def _parse_image_url(self, album):
        query = "./ancestor::li[1]//*[contains(@class, 'photo')]//img"
        thumb = album.xpath(query)[0].get('src')
        return thumb.replace('/thumb/', '/images/')

    def _parse_count(self, album):
        query = "./ancestor::li[1]//*[contains(@style, 'mediaCount')]/text()"
        count_text = album.xpath(query)[0]
        count = int(re.match('\d+', count_text).group(0))
        return count

    def _generate_albums(self, url):
        for page in itertools.count():
            # fetch page URL
            params = urllib.urlencode({'page': page})
            page_url = '?'.join([url, params])
            dom = html.fromstring(http.get(page_url))

            # parse out album names
            query = "//a[contains(@class, 'albumName')]"
            albums = dom.xpath(query)

            # break infinite iteration
            if not albums:
                break

            # else, filter album names to camp-specific only
            for album in albums:
                is_camp = self._is_camp_specific(album)
                is_secure = self._is_secure(album)

                if is_camp and not is_secure:
                    yield {
                        'year': self._parse_year(album),
                        'url': self._parse_url(album),
                        'image_url': self._parse_image_url(album),
                        'count': self._parse_count(album),
                    }

    def _fetch(self):
        key = lambda a: a['year']
        all_albums = sorted(self._generate_albums(self._url),
                            key=key, reverse=True)
        for year, albums in itertools.groupby(all_albums, key=key):
            yield year, list(albums)
