import re
import urllib.parse
import itertools
from io import BytesIO

import requests
from lxml import html
from PIL import Image, ExifTags, ImageEnhance


class ImageEditor(object):

    def __init__(self, image):
        self.image = image

    def rotate(self):
        image = self.image

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        try:
            exif = dict(image._getexif() or {})
        except AttributeError:
            pass
        else:
            if orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
                self.image = image

    def crop(self, pixels):
        image = self.image
        w, h = image.size
        box = (pixels, pixels, w - pixels, h - pixels)
        self.image = image.crop(box)

    def resize(self, width, height):
        image = self.image
        old_w, old_h = image.size

        # resize
        keep_height = (
            (old_w < old_h and width > height)
            or
            (old_w > old_h and width <= height)
        )
        if keep_height:
            size = (old_w * height // old_h, height)
        else:
            size = (width, old_h * width // old_w)

        image = image.resize(size, Image.ANTIALIAS)

        # crop the rest, centered
        left = abs(size[0] - width) // 2
        top = abs(size[1] - height) // 2

        box = (left, top, left + width, top + height)
        self.image = image.crop(box)

    def sharpen(self, sharpness=1.6):
        image = self.image
        sharpener = ImageEnhance.Sharpness(image)
        return sharpener.enhance(sharpness)

    @property
    def stream(self):
        stream = BytesIO()
        self.image.save(stream, 'JPEG', quality=100)
        stream.seek(0)
        return stream

    @property
    def bytes(self):
        return self.stream.read()


class Photo(bytes):

    def __new__(cls, url, crop=None, resize=None):
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        stream = BytesIO(resp.content)

        image = Image.open(stream)
        editor = ImageEditor(image)
        editor.rotate()
        if crop:
            editor.crop(int(crop))
        if resize:
            editor.resize(*resize)
        if crop or resize:
            editor.sharpen()

        return bytes.__new__(cls, editor.bytes)


class PhotoAlbums(list):

    _url = 'http://hlavas.rajce.idnes.cz/'
    _camp_re = re.compile(r'(t[áa]bor\D{0,3}(\d{4}|\d{2})|^[Aa]tlanti)', re.I)

    def __init__(self):
        all_albums = self._regroup_sorted(self._generate_albums(self._url))
        self.extend(all_albums)

    def _regroup_sorted(self, all_albums):
        # sort it by year (reverse = descendant by time)
        def key_year(a):
            return a['year']
        all_albums = sorted(all_albums, key=key_year, reverse=True)

        # regroup it by year, sort every album set by title
        def key_title(a):
            return a['title'].lower()
        for year, albums in itertools.groupby(all_albums, key=key_year):
            yield year, sorted(albums, key=key_title)

    def _generate_albums(self, url):
        for page in itertools.count():
            # fetch page URL
            params = urllib.parse.urlencode({'page': page})
            page_url = '?'.join([url, params])

            resp = requests.get(page_url)
            resp.raise_for_status()
            dom = html.fromstring(resp.content)

            # parse out album names
            query = """
                //div[contains(@class, 'albumList')]
                //a[
                    not(ancestor::*[contains(@class, 'navigation')])
                    and
                    contains(@class, 'albumName')
                ]
            """
            albums = dom.xpath(re.sub(r'\s+', ' ', query.strip()))

            # break infinite iteration
            if not albums:
                break

            # else, filter album names to camp-related only
            for album in albums:
                is_camp = self._is_camp_related(album)
                is_secure = self._is_secure(album)

                if is_camp and not is_secure:
                    yield {
                        'title': self._parse_title(album),
                        'year': self._parse_year(album),
                        'url': self._parse_url(album),
                        'image_url': self._parse_image_url(album),
                        'count': self._parse_count(album),
                    }

    def _is_camp_related(self, album):
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
        query = "./ancestor::*[contains(@class, 'albumItem')]//*[contains(@class, 'photo')]//img"
        thumb = album.xpath(query)[0].get('src')
        return thumb.replace('/thumb/', '/images/')

    def _parse_count(self, album):
        query = "./ancestor::*[contains(@class, 'albumItem')]//*[contains(@style, 'mediaCount')]/text()"
        count_text = album.xpath(query)[0]
        count = int(re.match('\d+', count_text).group(0))
        return count
