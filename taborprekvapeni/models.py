# -*- coding: utf-8 -*-


import os
import re
import urllib
import logging
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
        self.update(data or {})

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

    def _parse_poster_url(self, poster_page_url):
        contents = http.get(poster_page_url)
        dom = html.fromstring(contents)
        img = dom.xpath('.//img')[0]
        return img.get('src')

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

            poster_page_url = self._create_url('upoutavka.php', camp_id)
            poster_url = self._parse_poster_url(poster_page_url)

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


class TextParser(object):

    _meta_re = {
        'parentheses': re.compile(r'\(([^\)]+)\)'),
        'square_brackets': re.compile(r'\[([^\]]+)\]'),
        'braces': re.compile(r'\{([^\}]+)\}'),
    }

    def parse(self, filename):
        with open(filename) as f:
            text = f.read().strip().decode('utf-8')

        # find title and extract it
        title = None
        lines = []
        for line in text.splitlines():
            if line.startswith('# '):
                title = line[2:]
            else:
                lines.append(line)
        text = '\n'.join(lines)

        # parse properties
        meta = self._parse_meta(title) if title else {}
        return text, meta

    def _parse_meta(self, title):
        meta = {}
        for meta_name, meta_re in self._meta_re.items():
            match = meta_re.search(title)
            if match:
                meta[meta_name] = match.group(1)
                title = meta_re.sub('', title).strip()
        meta['title'] = title
        return meta


class HistoryText(unicode):

    _dir = os.path.join(app.root_path, 'texts', 'history')

    def __new__(cls, year):
        # get the text
        path = os.path.join(cls._dir, str(year) + '.md')
        text, meta = TextParser().parse(path)

        obj = unicode.__new__(cls, text)

        # set properties
        obj.title = meta['title']
        obj.place = meta.get('parentheses')
        obj.year = int(year)
        return obj

    @classmethod
    def find_all(cls):
        texts = []
        for basename in os.listdir(cls._dir):
            year = int(basename[:4])  # YYYY.md
            text = cls(year)
            texts.append(text)
        return sorted(texts, key=lambda t: t.year, reverse=True)


class TeamMemberText(unicode):

    _dir = os.path.join(app.root_path, 'texts', 'team')

    def __new__(cls, basename):
        order, slug_file = basename.split('_', 1)
        slug_file = slug_file[:-3]  # name_surname.md

        # get the text
        path = os.path.join(cls._dir, basename)
        text, meta = TextParser().parse(path)

        obj = unicode.__new__(cls, text)

        # set properties
        obj.order = int(order)
        obj.full_name = obj.title = meta['title']
        obj.names = meta['title'].split()
        obj.nickname = meta.get('parentheses')
        obj.post = meta.get('square_brackets', u'vedoucí')
        obj.slug_url = slug_file.replace('_', '-')
        obj.slug_file = slug_file
        obj.basename = basename
        return obj

    @classmethod
    def from_slug_url(cls, slug_url):
        return cls.from_slug_file(slug_url.replace('-', '_'))

    @classmethod
    def from_slug_file(cls, slug_file):
        for basename in os.listdir(cls._dir):
            order, name = basename.split('_', 1)
            if name[:-3] == slug_file:  # name_surname.md
                return cls(basename)
        return None

    @classmethod
    def find_all(cls):
        texts = []
        for basename in os.listdir(cls._dir):
            try:
                text = cls(basename)
                texts.append(text)
            except:
                logging.exception('Error in loading team member text: %s',
                                  basename)

        key_order = lambda t: t.order
        return sorted(texts, key=key_order)


class PhotoAlbums(dict):

    _url = 'http://hlavas.rajce.idnes.cz/'
    _camp_re = re.compile(u't[áa]bor\D{0,3}(\d{4}|\d{2})', re.I)

    def __init__(self):
        try:
            data = cache(self.__class__.__name__, self._fetch)
        except:
            logging.exception('Error in loading photo albums.')
        self.update(data or {})

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

    def _parse_title(self, album):
        return album.text

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
            query = ("//ul[contains(@id, 'albumList')]"
                     "//a[contains(@class, 'albumName')]")
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
                        'title': self._parse_title(album),
                        'year': self._parse_year(album),
                        'url': self._parse_url(album),
                        'image_url': self._parse_image_url(album),
                        'count': self._parse_count(album),
                    }

    def _regroup_sorted(self, all_albums):
        key_year = lambda a: a['year']
        key_title = lambda a: a['title'].lower()

        # sort it by year (reverse = descendant by time)
        all_albums = sorted(all_albums, key=key_year, reverse=True)

        # regroup it by year, sort every album set by title
        for year, albums in itertools.groupby(all_albums, key=key_year):
            yield year, sorted(albums, key=key_title)

    def _fetch(self):
        all_albums = self._generate_albums(self._url)
        return list(self._regroup_sorted(all_albums))
