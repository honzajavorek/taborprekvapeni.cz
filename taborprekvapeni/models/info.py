# -*- coding: utf-8 -*-


import datetime


class BasicInfo(dict):
    """Basic info about the camp. Previously fetched from tabory.cz,
    now hotfixed as hardcoded content.
    """

    def __init__(self):
        self['junior'] = {
            'age_from': 6,
            'age_to': 9,
            'starts_at': datetime.date(2017, 7, 1),
            'ends_at': datetime.date(2017, 7, 13),
            'topic': u'Atlantida - ztracená země',
            'book_url': 'http://www.taborbezhranic.cz/index.php?stranka=kontakty',
            'poster_url': 'http://img9.rajce.idnes.cz/d0902/8/8487/8487696_736315498cf25b645868230322dca902/images/DSC_0862.jpg?ver=2',
            'price': 5190,
        }
        self['senior'] = {
            'age_from': 10,
            'age_to': 17,
            'starts_at': datetime.date(2017, 7, 1),
            'ends_at': datetime.date(2017, 7, 13),
            'topic': u'Atlantida - ztracená země',
            'book_url': 'http://www.taborbezhranic.cz/index.php?stranka=kontakty',
            'poster_url': 'http://img5.rajce.idnes.cz/d0508/8/8500/8500812_6838f7e81857603deb5e43210379fe96/images/tabor20130839.jpg',
            # http://img5.rajce.idnes.cz/d0508/8/8500/8500812_6838f7e81857603deb5e43210379fe96/images/tabor20130915.jpg?ver=2
            'price': 5190,
        }
