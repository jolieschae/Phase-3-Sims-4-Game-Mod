# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\dom\domreg.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3499 bytes
well_known_implementations = {'minidom':'xml.dom.minidom', 
 '4DOM':'xml.dom.DOMImplementation'}
registered = {}

def registerDOMImplementation(name, factory):
    registered[name] = factory


def _good_enough(dom, features):
    for f, v in features:
        if not dom.hasFeature(f, v):
            return 0

    return 1


def getDOMImplementation(name=None, features=()):
    import os
    creator = None
    mod = well_known_implementations.get(name)
    if mod:
        mod = __import__(mod, {}, {}, ['getDOMImplementation'])
        return mod.getDOMImplementation()
    if name:
        return registered[name]()
    if 'PYTHON_DOM' in os.environ:
        return getDOMImplementation(name=(os.environ['PYTHON_DOM']))
    if isinstance(features, str):
        features = _parse_feature_string(features)
    for creator in registered.values():
        dom = creator()
        if _good_enough(dom, features):
            return dom

    for creator in well_known_implementations.keys():
        try:
            dom = getDOMImplementation(name=creator)
        except Exception:
            continue

        if _good_enough(dom, features):
            return dom

    raise ImportError('no suitable DOM implementation found')


def _parse_feature_string(s):
    features = []
    parts = s.split()
    i = 0
    length = len(parts)
    while i < length:
        feature = parts[i]
        if feature[0] in '0123456789':
            raise ValueError('bad feature name: %r' % (feature,))
        i = i + 1
        version = None
        if i < length:
            v = parts[i]
            if v[0] in '0123456789':
                i = i + 1
                version = v
        features.append((feature, version))

    return tuple(features)