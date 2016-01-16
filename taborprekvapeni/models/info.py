# -*- coding: utf-8 -*-


import datetime


class BasicInfo(dict):
    """Basic info about the camp. Previously fetched from tabory.cz,
    now hotfixed as hardcoded content.

    You can access data in following way::

        >>> bi = BasicInfo()
        >>> bi['senior'].keys()  # junior/senior camp
        ['age_from', 'age_to', 'starts_at', 'ends_at',
         'topic', 'fb_url', 'book_url', 'price']

    Ages and ``price`` are numbers. ``starts_at`` and ``ends_at`` are
    regular :class:`datetime.date` objects. ``topic`` is string,
    ``fb_url`` is URL of Facebook page, ``book_url`` is URL to use
    for booking.
    """

    def __init__(self):
        self['junior'] = {
            'age_from': 6,
            'age_to': 9,
            'starts_at': datetime.date(2016, 8, 6),
            'ends_at': datetime.date(2016, 8, 20),
            'topic': u'Mars 2049 – osídlování rudé planety',
            'fb_url': 'https://www.facebook.com/Ran%C4%8D-v-%C3%BAdol%C3%AD-195015720518776/',
            'details_url': 'http://www.taboriste.cz/letni-tabory-2016/a4-beh-2016/',
            'book_url': 'http://www.taboriste.cz/letni-tabory-2016/dulezite-informace-k-letnim-taborum/',
            'departure_url': 'http://www.taboriste.cz/letni-tabory-2016/dulezite-informace-k-letnim-taborum/',
            'price': 6990,
        }
        self['senior'] = {
            'age_from': 10,
            'age_to': 18,
            'starts_at': datetime.date(2016, 8, 6),
            'ends_at': datetime.date(2016, 8, 20),
            'topic': u'Mars 2049 – osídlování rudé planety',
            'fb_url': 'https://www.facebook.com/Ran%C4%8D-v-%C3%BAdol%C3%AD-195015720518776/',
            'details_url': 'http://www.taboriste.cz/letni-tabory-2016/a4-beh-2016/',
            'book_url': 'http://www.taboriste.cz/letni-tabory-2016/dulezite-informace-k-letnim-taborum/',
            'departure_url': 'http://www.taboriste.cz/letni-tabory-2016/dulezite-informace-k-letnim-taborum/',
            'price': 6990,
        }
