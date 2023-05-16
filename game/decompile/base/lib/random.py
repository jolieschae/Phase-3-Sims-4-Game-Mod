# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\random.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 28259 bytes
from warnings import warn as _warn
from types import MethodType as _MethodType, BuiltinMethodType as _BuiltinMethodType
from math import log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
from math import sqrt as _sqrt, acos as _acos, cos as _cos, sin as _sin
from os import urandom as _urandom
from _collections_abc import Set as _Set, Sequence as _Sequence
from hashlib import sha512 as _sha512
import itertools as _itertools, bisect as _bisect, os as _os
__all__ = [
 "'Random'", "'seed'", "'random'", "'uniform'", "'randint'", "'choice'", "'sample'", 
 "'randrange'", 
 "'shuffle'", "'normalvariate'", "'lognormvariate'", 
 "'expovariate'", "'vonmisesvariate'", 
 "'gammavariate'", "'triangular'", 
 "'gauss'", "'betavariate'", "'paretovariate'", 
 "'weibullvariate'", 
 "'getstate'", "'setstate'", "'getrandbits'", "'choices'", 
 "'SystemRandom'"]
NV_MAGICCONST = 4 * _exp(-0.5) / _sqrt(2.0)
TWOPI = 2.0 * _pi
LOG4 = _log(4.0)
SG_MAGICCONST = 1.0 + _log(4.5)
BPF = 53
RECIP_BPF = 2 ** (-BPF)
import _random

class Random(_random.Random):
    VERSION = 3

    def __init__(self, x=None):
        self.seed(x)
        self.gauss_next = None

    def seed(self, a=None, version=2):
        if version == 1:
            if isinstance(a, (str, bytes)):
                a = a.decode('latin-1') if isinstance(a, bytes) else a
                x = ord(a[0]) << 7 if a else 0
                for c in map(ord, a):
                    x = (1000003 * x ^ c) & 18446744073709551615

                x ^= len(a)
                a = -2 if x == -1 else x
        elif version == 2 and isinstance(a, (str, bytes, bytearray)):
            if isinstance(a, str):
                a = a.encode()
            a += _sha512(a).digest()
            a = int.from_bytes(a, 'big')
        super().seed(a)
        self.gauss_next = None

    def getstate(self):
        return (
         self.VERSION, super().getstate(), self.gauss_next)

    def setstate(self, state):
        version = state[0]
        if version == 3:
            version, internalstate, self.gauss_next = state
            super().setstate(internalstate)
        else:
            if version == 2:
                version, internalstate, self.gauss_next = state
                try:
                    internalstate = tuple((x % 4294967296 for x in internalstate))
                except ValueError as e:
                    try:
                        raise TypeError from e
                    finally:
                        e = None
                        del e

                super().setstate(internalstate)
            else:
                raise ValueError('state with version %s passed to Random.setstate() of version %s' % (
                 version, self.VERSION))

    def __getstate__(self):
        return self.getstate()

    def __setstate__(self, state):
        self.setstate(state)

    def __reduce__(self):
        return (
         self.__class__, (), self.getstate())

    def randrange(self, start, stop=None, step=1, _int=int):
        istart = _int(start)
        if istart != start:
            raise ValueError('non-integer arg 1 for randrange()')
        if stop is None:
            if istart > 0:
                return self._randbelow(istart)
            raise ValueError('empty range for randrange()')
        istop = _int(stop)
        if istop != stop:
            raise ValueError('non-integer stop for randrange()')
        else:
            width = istop - istart
            if step == 1:
                if width > 0:
                    return istart + self._randbelow(width)
            else:
                if step == 1:
                    raise ValueError('empty range for randrange() (%d,%d, %d)' % (istart, istop, width))
                istep = _int(step)
                if istep != step:
                    raise ValueError('non-integer step for randrange()')
                if istep > 0:
                    n = (width + istep - 1) // istep
                else:
                    if istep < 0:
                        n = (width + istep + 1) // istep
                    else:
                        raise ValueError('zero step for randrange()')
        if n <= 0:
            raise ValueError('empty range for randrange()')
        return istart + istep * self._randbelow(n)

    def randint(self, a, b):
        return self.randrange(a, b + 1)

    def _randbelow(self, n, int=int, maxsize=1 << BPF, type=type, Method=_MethodType, BuiltinMethod=_BuiltinMethodType):
        random = self.random
        getrandbits = self.getrandbits
        if type(random) is BuiltinMethod or type(getrandbits) is Method:
            k = n.bit_length()
            r = getrandbits(k)
            while r >= n:
                r = getrandbits(k)

            return r
        if n >= maxsize:
            _warn('Underlying random() generator does not supply \nenough bits to choose from a population range this large.\nTo remove the range limitation, add a getrandbits() method.')
            return int(random() * n)
        if n == 0:
            raise ValueError('Boundary cannot be zero')
        rem = maxsize % n
        limit = (maxsize - rem) / maxsize
        r = random()
        while r >= limit:
            r = random()

        return int(r * maxsize) % n

    def choice(self, seq):
        try:
            i = self._randbelow(len(seq))
        except ValueError:
            raise IndexError('Cannot choose from an empty sequence') from None

        return seq[i]

    def shuffle(self, x, random=None):
        if random is None:
            randbelow = self._randbelow
            for i in reversed(range(1, len(x))):
                j = randbelow(i + 1)
                x[i], x[j] = x[j], x[i]

        else:
            _int = int
            for i in reversed(range(1, len(x))):
                j = _int(random() * (i + 1))
                x[i], x[j] = x[j], x[i]

    def sample(self, population, k):
        if isinstance(population, _Set):
            population = tuple(population)
        if not isinstance(population, _Sequence):
            raise TypeError('Population must be a sequence or set.  For dicts, use list(d).')
        randbelow = self._randbelow
        n = len(population)
        if not 0 <= k <= n:
            raise ValueError('Sample larger than population or is negative')
        result = [
         None] * k
        setsize = 21
        if k > 5:
            setsize += 4 ** _ceil(_log(k * 3, 4))
        if n <= setsize:
            pool = list(population)
            for i in range(k):
                j = randbelow(n - i)
                result[i] = pool[j]
                pool[j] = pool[n - i - 1]

        else:
            selected = set()
            selected_add = selected.add
            for i in range(k):
                j = randbelow(n)
                while j in selected:
                    j = randbelow(n)

                selected_add(j)
                result[i] = population[j]

        return result

    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        random = self.random
        if cum_weights is None:
            if weights is None:
                _int = int
                total = len(population)
                return [population[_int(random() * total)] for i in range(k)]
            cum_weights = list(_itertools.accumulate(weights))
        else:
            if weights is not None:
                raise TypeError('Cannot specify both weights and cumulative weights')
        if len(cum_weights) != len(population):
            raise ValueError('The number of weights does not match the population')
        bisect = _bisect.bisect
        total = cum_weights[-1]
        return [population[bisect(cum_weights, random() * total)] for i in range(k)]

    def uniform(self, a, b):
        return a + (b - a) * self.random()

    def triangular(self, low=0.0, high=1.0, mode=None):
        u = self.random()
        try:
            c = 0.5 if mode is None else (mode - low) / (high - low)
        except ZeroDivisionError:
            return low
        else:
            if u > c:
                u = 1.0 - u
                c = 1.0 - c
                low, high = high, low
            return low + (high - low) * _sqrt(u * c)

    def normalvariate(self, mu, sigma):
        random = self.random
        while 1:
            u1 = random()
            u2 = 1.0 - random()
            z = NV_MAGICCONST * (u1 - 0.5) / u2
            zz = z * z / 4.0
            if zz <= -_log(u2):
                break

        return mu + z * sigma

    def lognormvariate(self, mu, sigma):
        return _exp(self.normalvariate(mu, sigma))

    def expovariate(self, lambd):
        return -_log(1.0 - self.random()) / lambd

    def vonmisesvariate(self, mu, kappa):
        random = self.random
        if kappa <= 1e-06:
            return TWOPI * random()
        else:
            s = 0.5 / kappa
            r = s + _sqrt(1.0 + s * s)
            while 1:
                u1 = random()
                z = _cos(_pi * u1)
                d = z / (r + z)
                u2 = random()
                if u2 < 1.0 - d * d or u2 <= (1.0 - d) * _exp(d):
                    break

            q = 1.0 / r
            f = (q + z) / (1.0 + q * z)
            u3 = random()
            if u3 > 0.5:
                theta = (mu + _acos(f)) % TWOPI
            else:
                theta = (mu - _acos(f)) % TWOPI
        return theta

    def gammavariate--- This code section failed: ---

 L. 519         0  LOAD_FAST                'alpha'
                2  LOAD_CONST               0.0
                4  COMPARE_OP               <=
                6  POP_JUMP_IF_TRUE     16  'to 16'
                8  LOAD_FAST                'beta'
               10  LOAD_CONST               0.0
               12  COMPARE_OP               <=
               14  POP_JUMP_IF_FALSE    24  'to 24'
             16_0  COME_FROM             6  '6'

 L. 520        16  LOAD_GLOBAL              ValueError
               18  LOAD_STR                 'gammavariate: alpha and beta must be > 0.0'
               20  CALL_FUNCTION_1       1  '1 positional argument'
               22  RAISE_VARARGS_1       1  'exception instance'
             24_0  COME_FROM            14  '14'

 L. 522        24  LOAD_FAST                'self'
               26  LOAD_ATTR                random
               28  STORE_FAST               'random'

 L. 523        30  LOAD_FAST                'alpha'
               32  LOAD_CONST               1.0
               34  COMPARE_OP               >
               36  POP_JUMP_IF_FALSE   218  'to 218'

 L. 529        38  LOAD_GLOBAL              _sqrt
               40  LOAD_CONST               2.0
               42  LOAD_FAST                'alpha'
               44  BINARY_MULTIPLY  
               46  LOAD_CONST               1.0
               48  BINARY_SUBTRACT  
               50  CALL_FUNCTION_1       1  '1 positional argument'
               52  STORE_FAST               'ainv'

 L. 530        54  LOAD_FAST                'alpha'
               56  LOAD_GLOBAL              LOG4
               58  BINARY_SUBTRACT  
               60  STORE_FAST               'bbb'

 L. 531        62  LOAD_FAST                'alpha'
               64  LOAD_FAST                'ainv'
               66  BINARY_ADD       
               68  STORE_FAST               'ccc'

 L. 533        70  SETUP_LOOP          216  'to 216'
             72_0  COME_FROM           202  '202'

 L. 534        72  LOAD_FAST                'random'
               74  CALL_FUNCTION_0       0  '0 positional arguments'
               76  STORE_FAST               'u1'

 L. 535        78  LOAD_CONST               1e-07
               80  LOAD_FAST                'u1'
               82  DUP_TOP          
               84  ROT_THREE        
               86  COMPARE_OP               <
               88  POP_JUMP_IF_FALSE    98  'to 98'
               90  LOAD_CONST               0.9999999
               92  COMPARE_OP               <
               94  POP_JUMP_IF_TRUE    102  'to 102'
               96  JUMP_BACK            72  'to 72'
             98_0  COME_FROM            88  '88'
               98  POP_TOP          

 L. 536       100  CONTINUE             72  'to 72'
            102_0  COME_FROM            94  '94'

 L. 537       102  LOAD_CONST               1.0
              104  LOAD_FAST                'random'
              106  CALL_FUNCTION_0       0  '0 positional arguments'
              108  BINARY_SUBTRACT  
              110  STORE_FAST               'u2'

 L. 538       112  LOAD_GLOBAL              _log
              114  LOAD_FAST                'u1'
              116  LOAD_CONST               1.0
              118  LOAD_FAST                'u1'
              120  BINARY_SUBTRACT  
              122  BINARY_TRUE_DIVIDE
              124  CALL_FUNCTION_1       1  '1 positional argument'
              126  LOAD_FAST                'ainv'
              128  BINARY_TRUE_DIVIDE
              130  STORE_FAST               'v'

 L. 539       132  LOAD_FAST                'alpha'
              134  LOAD_GLOBAL              _exp
              136  LOAD_FAST                'v'
              138  CALL_FUNCTION_1       1  '1 positional argument'
              140  BINARY_MULTIPLY  
              142  STORE_FAST               'x'

 L. 540       144  LOAD_FAST                'u1'
              146  LOAD_FAST                'u1'
              148  BINARY_MULTIPLY  
              150  LOAD_FAST                'u2'
              152  BINARY_MULTIPLY  
              154  STORE_FAST               'z'

 L. 541       156  LOAD_FAST                'bbb'
              158  LOAD_FAST                'ccc'
              160  LOAD_FAST                'v'
              162  BINARY_MULTIPLY  
              164  BINARY_ADD       
              166  LOAD_FAST                'x'
              168  BINARY_SUBTRACT  
              170  STORE_FAST               'r'

 L. 542       172  LOAD_FAST                'r'
              174  LOAD_GLOBAL              SG_MAGICCONST
              176  BINARY_ADD       
              178  LOAD_CONST               4.5
              180  LOAD_FAST                'z'
              182  BINARY_MULTIPLY  
              184  BINARY_SUBTRACT  
              186  LOAD_CONST               0.0
              188  COMPARE_OP               >=
              190  POP_JUMP_IF_TRUE    204  'to 204'
              192  LOAD_FAST                'r'
              194  LOAD_GLOBAL              _log
              196  LOAD_FAST                'z'
              198  CALL_FUNCTION_1       1  '1 positional argument'
              200  COMPARE_OP               >=
              202  POP_JUMP_IF_FALSE    72  'to 72'
            204_0  COME_FROM           190  '190'

 L. 543       204  LOAD_FAST                'x'
              206  LOAD_FAST                'beta'
              208  BINARY_MULTIPLY  
              210  RETURN_VALUE     
              212  JUMP_BACK            72  'to 72'
              214  POP_BLOCK        
            216_0  COME_FROM_LOOP       70  '70'
              216  JUMP_FORWARD        408  'to 408'
            218_0  COME_FROM            36  '36'

 L. 545       218  LOAD_FAST                'alpha'
              220  LOAD_CONST               1.0
              222  COMPARE_OP               ==
          224_226  POP_JUMP_IF_FALSE   268  'to 268'

 L. 547       228  LOAD_FAST                'random'
              230  CALL_FUNCTION_0       0  '0 positional arguments'
              232  STORE_FAST               'u'

 L. 548       234  SETUP_LOOP          254  'to 254'
              236  LOAD_FAST                'u'
              238  LOAD_CONST               1e-07
              240  COMPARE_OP               <=
              242  POP_JUMP_IF_FALSE   252  'to 252'

 L. 549       244  LOAD_FAST                'random'
              246  CALL_FUNCTION_0       0  '0 positional arguments'
              248  STORE_FAST               'u'
              250  JUMP_BACK           236  'to 236'
            252_0  COME_FROM           242  '242'
              252  POP_BLOCK        
            254_0  COME_FROM_LOOP      234  '234'

 L. 550       254  LOAD_GLOBAL              _log
              256  LOAD_FAST                'u'
              258  CALL_FUNCTION_1       1  '1 positional argument'
              260  UNARY_NEGATIVE   
              262  LOAD_FAST                'beta'
              264  BINARY_MULTIPLY  
              266  RETURN_VALUE     
            268_0  COME_FROM           224  '224'

 L. 556       268  SETUP_LOOP          400  'to 400'
            270_0  COME_FROM           388  '388'

 L. 557       270  LOAD_FAST                'random'
              272  CALL_FUNCTION_0       0  '0 positional arguments'
              274  STORE_FAST               'u'

 L. 558       276  LOAD_GLOBAL              _e
              278  LOAD_FAST                'alpha'
              280  BINARY_ADD       
              282  LOAD_GLOBAL              _e
              284  BINARY_TRUE_DIVIDE
              286  STORE_FAST               'b'

 L. 559       288  LOAD_FAST                'b'
              290  LOAD_FAST                'u'
              292  BINARY_MULTIPLY  
              294  STORE_FAST               'p'

 L. 560       296  LOAD_FAST                'p'
              298  LOAD_CONST               1.0
              300  COMPARE_OP               <=
          302_304  POP_JUMP_IF_FALSE   320  'to 320'

 L. 561       306  LOAD_FAST                'p'
              308  LOAD_CONST               1.0
              310  LOAD_FAST                'alpha'
              312  BINARY_TRUE_DIVIDE
              314  BINARY_POWER     
              316  STORE_FAST               'x'
              318  JUMP_FORWARD        338  'to 338'
            320_0  COME_FROM           302  '302'

 L. 563       320  LOAD_GLOBAL              _log
              322  LOAD_FAST                'b'
              324  LOAD_FAST                'p'
              326  BINARY_SUBTRACT  
              328  LOAD_FAST                'alpha'
              330  BINARY_TRUE_DIVIDE
              332  CALL_FUNCTION_1       1  '1 positional argument'
              334  UNARY_NEGATIVE   
              336  STORE_FAST               'x'
            338_0  COME_FROM           318  '318'

 L. 564       338  LOAD_FAST                'random'
              340  CALL_FUNCTION_0       0  '0 positional arguments'
              342  STORE_FAST               'u1'

 L. 565       344  LOAD_FAST                'p'
              346  LOAD_CONST               1.0
              348  COMPARE_OP               >
          350_352  POP_JUMP_IF_FALSE   376  'to 376'

 L. 566       354  LOAD_FAST                'u1'
              356  LOAD_FAST                'x'
              358  LOAD_FAST                'alpha'
              360  LOAD_CONST               1.0
              362  BINARY_SUBTRACT  
              364  BINARY_POWER     
              366  COMPARE_OP               <=
          368_370  POP_JUMP_IF_FALSE   394  'to 394'

 L. 567       372  BREAK_LOOP       
              374  JUMP_BACK           270  'to 270'
            376_0  COME_FROM           350  '350'

 L. 568       376  LOAD_FAST                'u1'
              378  LOAD_GLOBAL              _exp
              380  LOAD_FAST                'x'
              382  UNARY_NEGATIVE   
              384  CALL_FUNCTION_1       1  '1 positional argument'
              386  COMPARE_OP               <=
          388_390  POP_JUMP_IF_FALSE   270  'to 270'

 L. 569       392  BREAK_LOOP       
            394_0  COME_FROM           368  '368'
          394_396  JUMP_BACK           270  'to 270'
              398  POP_BLOCK        
            400_0  COME_FROM_LOOP      268  '268'

 L. 570       400  LOAD_FAST                'x'
              402  LOAD_FAST                'beta'
              404  BINARY_MULTIPLY  
              406  RETURN_VALUE     
            408_0  COME_FROM           216  '216'

Parse error at or near `CONTINUE' instruction at offset 100

    def gauss(self, mu, sigma):
        random = self.random
        z = self.gauss_next
        self.gauss_next = None
        if z is None:
            x2pi = random() * TWOPI
            g2rad = _sqrt(-2.0 * _log(1.0 - random()))
            z = _cos(x2pi) * g2rad
            self.gauss_next = _sin(x2pi) * g2rad
        return mu + z * sigma

    def betavariate(self, alpha, beta):
        y = self.gammavariate(alpha, 1.0)
        if y == 0:
            return 0.0
        return y / (y + self.gammavariate(beta, 1.0))

    def paretovariate(self, alpha):
        u = 1.0 - self.random()
        return 1.0 / u ** (1.0 / alpha)

    def weibullvariate(self, alpha, beta):
        u = 1.0 - self.random()
        return alpha * (-_log(u)) ** (1.0 / beta)


class SystemRandom(Random):

    def random(self):
        return (int.from_bytes(_urandom(7), 'big') >> 3) * RECIP_BPF

    def getrandbits(self, k):
        if k <= 0:
            raise ValueError('number of bits must be greater than zero')
        if k != int(k):
            raise TypeError('number of bits should be an integer')
        numbytes = (k + 7) // 8
        x = int.from_bytes(_urandom(numbytes), 'big')
        return x >> numbytes * 8 - k

    def seed(self, *args, **kwds):
        pass

    def _notimplemented(self, *args, **kwds):
        raise NotImplementedError('System entropy source does not have state.')

    getstate = setstate = _notimplemented


def _test_generator(n, func, args):
    import time
    print(n, 'times', func.__name__)
    total = 0.0
    sqsum = 0.0
    smallest = 10000000000.0
    largest = -10000000000.0
    t0 = time.time()
    for i in range(n):
        x = func(*args)
        total += x
        sqsum = sqsum + x * x
        smallest = min(x, smallest)
        largest = max(x, largest)

    t1 = time.time()
    print((round(t1 - t0, 3)), 'sec,', end=' ')
    avg = total / n
    stddev = _sqrt(sqsum / n - avg * avg)
    print('avg %g, stddev %g, min %g, max %g\n' % (
     avg, stddev, smallest, largest))


def _test(N=2000):
    _test_generator(N, random, ())
    _test_generator(N, normalvariate, (0.0, 1.0))
    _test_generator(N, lognormvariate, (0.0, 1.0))
    _test_generator(N, vonmisesvariate, (0.0, 1.0))
    _test_generator(N, gammavariate, (0.01, 1.0))
    _test_generator(N, gammavariate, (0.1, 1.0))
    _test_generator(N, gammavariate, (0.1, 2.0))
    _test_generator(N, gammavariate, (0.5, 1.0))
    _test_generator(N, gammavariate, (0.9, 1.0))
    _test_generator(N, gammavariate, (1.0, 1.0))
    _test_generator(N, gammavariate, (2.0, 1.0))
    _test_generator(N, gammavariate, (20.0, 1.0))
    _test_generator(N, gammavariate, (200.0, 1.0))
    _test_generator(N, gauss, (0.0, 1.0))
    _test_generator(N, betavariate, (3.0, 3.0))
    _test_generator(N, triangular, (0.0, 1.0, 0.3333333333333333))


_inst = Random()
seed = _inst.seed
random = _inst.random
uniform = _inst.uniform
triangular = _inst.triangular
randint = _inst.randint
choice = _inst.choice
randrange = _inst.randrange
sample = _inst.sample
shuffle = _inst.shuffle
choices = _inst.choices
normalvariate = _inst.normalvariate
lognormvariate = _inst.lognormvariate
expovariate = _inst.expovariate
vonmisesvariate = _inst.vonmisesvariate
gammavariate = _inst.gammavariate
gauss = _inst.gauss
betavariate = _inst.betavariate
paretovariate = _inst.paretovariate
weibullvariate = _inst.weibullvariate
getstate = _inst.getstate
setstate = _inst.setstate
getrandbits = _inst.getrandbits
if hasattr(_os, 'fork'):
    _os.register_at_fork(after_in_child=(_inst.seed))
if __name__ == '__main__':
    _test()