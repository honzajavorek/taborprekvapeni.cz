import datetime


class BasicInfo(dict):
    """Basic info about the camp. Previously fetched from tabory.cz,
    now hotfixed as hardcoded content.
    """

    def __init__(self):
        self['junior'] = {
            'age_from': 6,
            'age_to': 9,
            'starts_at': datetime.date(2018, 7, 15),
            'ends_at': datetime.date(2018, 7, 28),
            'topic': u'Divoký západ a western',
            'book_url': 'http://www.veselaspolecnost.cz/klasicky-letni-tabor/',
            'poster_url': 'http://img9.rajce.idnes.cz/d0902/8/8487/8487696_736315498cf25b645868230322dca902/images/DSC_0862.jpg?ver=2',
            'price': 4750,
        }
        self['senior'] = {
            'age_from': 10,
            'age_to': 14,
            'starts_at': datetime.date(2018, 7, 15),
            'ends_at': datetime.date(2018, 7, 28),
            'topic': u'Divoký západ a western',
            'book_url': 'http://www.veselaspolecnost.cz/klasicky-letni-tabor/',
            'poster_url': 'http://img9.rajce.idnes.cz/d0902/8/8487/8487696_736315498cf25b645868230322dca902/images/DSC_0885.jpg?ver=0',
            # http://img5.rajce.idnes.cz/d0508/8/8500/8500812_6838f7e81857603deb5e43210379fe96/images/tabor20130915.jpg?ver=2
            'price': 4750,
        }
