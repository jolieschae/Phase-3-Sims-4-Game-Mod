# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\antigravity.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 493 bytes
import webbrowser, hashlib
webbrowser.open('https://xkcd.com/353/')

def geohash(latitude, longitude, datedow):
    h = hashlib.md5(datedow).hexdigest()
    p, q = ['%f' % float.fromhex('0.' + x) for x in (h[:16], h[16:32])]
    print('%d%s %d%s' % (latitude, p[1:], longitude, q[1:]))