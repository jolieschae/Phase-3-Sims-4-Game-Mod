# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\sndhdr.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 7343 bytes
__all__ = [
 'what', 'whathdr']
from collections import namedtuple
SndHeaders = namedtuple('SndHeaders', 'filetype framerate nchannels nframes sampwidth')
SndHeaders.filetype.__doc__ = "The value for type indicates the data type\nand will be one of the strings 'aifc', 'aiff', 'au','hcom',\n'sndr', 'sndt', 'voc', 'wav', '8svx', 'sb', 'ub', or 'ul'."
SndHeaders.framerate.__doc__ = 'The sampling_rate will be either the actual\nvalue or 0 if unknown or difficult to decode.'
SndHeaders.nchannels.__doc__ = 'The number of channels or 0 if it cannot be\ndetermined or if the value is difficult to decode.'
SndHeaders.nframes.__doc__ = 'The value for frames will be either the number\nof frames or -1.'
SndHeaders.sampwidth.__doc__ = "Either the sample size in bits or\n'A' for A-LAW or 'U' for u-LAW."

def what(filename):
    res = whathdr(filename)
    return res


def whathdr(filename):
    with open(filename, 'rb') as (f):
        h = f.read(512)
        for tf in tests:
            res = tf(h, f)
            if res:
                return SndHeaders(*res)

        return


tests = []

def test_aifc(h, f):
    import aifc
    if not h.startswith(b'FORM'):
        return
    elif h[8:12] == b'AIFC':
        fmt = 'aifc'
    else:
        if h[8:12] == b'AIFF':
            fmt = 'aiff'
        else:
            return
    f.seek(0)
    try:
        a = aifc.open(f, 'r')
    except (EOFError, aifc.Error):
        return
    else:
        return (
         fmt, a.getframerate(), a.getnchannels(),
         a.getnframes(), 8 * a.getsampwidth())


tests.append(test_aifc)

def test_au(h, f):
    if h.startswith(b'.snd'):
        func = get_long_be
    else:
        if h[:4] in (b'\x00ds.', b'dns.'):
            func = get_long_le
        else:
            return
    filetype = 'au'
    hdr_size = func(h[4:8])
    data_size = func(h[8:12])
    encoding = func(h[12:16])
    rate = func(h[16:20])
    nchannels = func(h[20:24])
    sample_size = 1
    if encoding == 1:
        sample_bits = 'U'
    else:
        if encoding == 2:
            sample_bits = 8
        else:
            if encoding == 3:
                sample_bits = 16
                sample_size = 2
            else:
                sample_bits = '?'
    frame_size = sample_size * nchannels
    if frame_size:
        nframe = data_size / frame_size
    else:
        nframe = -1
    return (
     filetype, rate, nchannels, nframe, sample_bits)


tests.append(test_au)

def test_hcom(h, f):
    if h[65:69] != b'FSSD' or h[128:132] != b'HCOM':
        return
    else:
        divisor = get_long_be(h[144:148])
        if divisor:
            rate = 22050 / divisor
        else:
            rate = 0
    return (
     'hcom', rate, 1, -1, 8)


tests.append(test_hcom)

def test_voc(h, f):
    if not h.startswith(b'Creative Voice File\x1a'):
        return
    sbseek = get_short_le(h[20:22])
    rate = 0
    if 0 <= sbseek < 500:
        if h[sbseek] == 1:
            ratecode = 256 - h[sbseek + 4]
            if ratecode:
                rate = int(1000000.0 / ratecode)
    return (
     'voc', rate, 1, -1, 8)


tests.append(test_voc)

def test_wav(h, f):
    import wave
    if not h.startswith(b'RIFF') or h[8:12] != b'WAVE' or h[12:16] != b'fmt ':
        return
    f.seek(0)
    try:
        w = wave.open(f, 'r')
    except (EOFError, wave.Error):
        return
    else:
        return (
         'wav', w.getframerate(), w.getnchannels(),
         w.getnframes(), 8 * w.getsampwidth())


tests.append(test_wav)

def test_8svx(h, f):
    if not h.startswith(b'FORM') or h[8:12] != b'8SVX':
        return
    return ('8svx', 0, 1, 0, 8)


tests.append(test_8svx)

def test_sndt(h, f):
    if h.startswith(b'SOUND'):
        nsamples = get_long_le(h[8:12])
        rate = get_short_le(h[20:22])
        return ('sndt', rate, 1, nsamples, 8)


tests.append(test_sndt)

def test_sndr(h, f):
    if h.startswith(b'\x00\x00'):
        rate = get_short_le(h[2:4])
        if 4000 <= rate <= 25000:
            return (
             'sndr', rate, 1, -1, 8)


tests.append(test_sndr)

def get_long_be(b):
    return b[0] << 24 | b[1] << 16 | b[2] << 8 | b[3]


def get_long_le(b):
    return b[3] << 24 | b[2] << 16 | b[1] << 8 | b[0]


def get_short_be(b):
    return b[0] << 8 | b[1]


def get_short_le(b):
    return b[1] << 8 | b[0]


def test():
    import sys
    recursive = 0
    if sys.argv[1:]:
        if sys.argv[1] == '-r':
            del sys.argv[1:2]
            recursive = 1
    try:
        if sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        else:
            testall(['.'], recursive, 1)
    except KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)


def testall(list, recursive, toplevel):
    import sys, os
    for filename in list:
        if os.path.isdir(filename):
            print((filename + '/:'), end=' ')
            if recursive or toplevel:
                print('recursing down:')
                import glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            else:
                print('*** directory (use -r) ***')
        else:
            print((filename + ':'), end=' ')
            sys.stdout.flush()
            try:
                print(what(filename))
            except OSError:
                print('*** not found ***')


if __name__ == '__main__':
    test()