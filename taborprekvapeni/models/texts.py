# -*- coding: utf-8 -*-


import os
import re


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

    _dirname = os.path.join(os.path.dirname(__file__), 'history')

    def __new__(cls, year):
        # get the text
        path = os.path.join(cls._dirname, str(year) + '.md')
        text, meta = TextParser().parse(path)

        obj = unicode.__new__(cls, text)

        # set properties
        obj.title = meta['title']
        obj.place = meta.get('parentheses')
        obj.year = int(year)
        return obj

    @classmethod
    def all(cls):
        texts = []
        for basename in os.listdir(cls._dirname):
            year = int(basename[:4])  # YYYY.md
            text = cls(year)
            texts.append(text)
        return sorted(texts, key=lambda t: t.year, reverse=True)


class TeamMemberText(unicode):

    _dirname = os.path.join(os.path.dirname(__file__), 'team')

    def __new__(cls, basename):
        order, slug = basename.split('-', 1)
        slug = slug[:-3]  # name-surname.md

        # get the text
        path = os.path.join(cls._dirname, basename)
        text, meta = TextParser().parse(path)

        obj = unicode.__new__(cls, text)

        # set properties
        obj.order = int(order)
        obj.full_name = obj.title = meta['title']
        obj.names = meta['title'].split()
        obj.nickname = meta.get('parentheses')
        obj.post = meta.get('square_brackets', u'vedoucí')
        obj.basename = basename
        obj.slug = slug
        return obj

    @classmethod
    def from_slug(cls, slug):
        for basename in os.listdir(cls._dirname):
            order, name = basename.split('-', 1)
            if name[:-3] == slug:  # name-surname.md
                return cls(basename)
        return None

    @classmethod
    def all(cls):
        texts = []
        for basename in os.listdir(cls._dirname):
            if re.match(r'\d', basename):
                text = cls(basename)
                texts.append(text)
        key_order = lambda t: t.order
        return sorted(texts, key=key_order)
