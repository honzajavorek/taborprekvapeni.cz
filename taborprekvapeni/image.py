# -*- coding: utf-8 -*-


import requests
from hashlib import sha1
from functools import wraps
from flask import send_file, request
from PIL import Image as PILImage, ExifTags, ImageEnhance

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from taborprekvapeni.cache import cache


class Image(object):

    def __init__(self, f):
        self.image = PILImage.open(f)

    def rotate(self):
        """Rotate according to EXIF data."""
        image = self.image

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif() or {})

        if orientation in exif:
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)

        self.image = image

    def resize_crop(self, width, height):
        image = self.image
        is_rect = width == height
        old_w, old_h = image.size

        # resize by shorter side
        if width < height or (is_rect and old_w < old_h):
            size = (width, old_h * width / old_w)
        else:
            size = (old_w * height / old_h, height)
        image = image.resize(size, PILImage.ANTIALIAS)

        # crop the rest, centered
        left = abs(size[0] - width) / 2
        top = abs(size[1] - height) / 2

        box = (left, top, left + width, top + height)
        image = image.crop(box)

        self.image = image

    def crop(self, pixels):
        image = self.image

        w, h = image.size
        box = (pixels, pixels, w - pixels, h - pixels)
        image = image.crop(box)

        self.image = image

    def sharpen(self, sharpness=1.6):
        sharpener = ImageEnhance.Sharpness(self.image)
        self.image = sharpener.enhance(sharpness)

    def to_stream(self):
        img_io = StringIO()
        self.image.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        return img_io

    @classmethod
    def from_url(cls, url):
        """Download an image and provide it as memory stream."""
        response = requests.get(url)
        response.raise_for_status()
        return cls(StringIO(response.content))


def generated_image(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        def generate_image():
            stream = f(*args, **kwargs)
            return stream.read()
        bytes = cache(request.url, generate_image)

        response = send_file(StringIO(bytes), mimetype='image/jpeg')
        response.set_etag(sha1(bytes).hexdigest())
        response.make_conditional(request)
        return response

    return decorated_function
