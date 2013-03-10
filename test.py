#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import requests


response = requests.get(sys.argv[1])
response.raise_for_status()
print response.content
