# -*- coding: utf-8 -*-


import requests
from PIL import Image as PILImage, ExifTags, ImageEnhance

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


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

        if exif:
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

        print (old_w, old_h), size, (left, top)

        box = (left, top, left + width, top + height)
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
