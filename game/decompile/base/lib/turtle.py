# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\turtle.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 147741 bytes
_ver = 'turtle 1.1b- - for Python 3.1   -  4. 5. 2009'
import tkinter as TK, types, math, time, inspect, sys
from os.path import isfile, split, join
from copy import deepcopy
from tkinter import simpledialog
_tg_classes = [
 "'ScrolledCanvas'", "'TurtleScreen'", "'Screen'", 
 "'RawTurtle'", "'Turtle'", 
 "'RawPen'", "'Pen'", "'Shape'", "'Vec2D'"]
_tg_screen_functions = ["'addshape'", "'bgcolor'", "'bgpic'", "'bye'", 
 "'clearscreen'", "'colormode'", 
 "'delay'", "'exitonclick'", "'getcanvas'", 
 "'getshapes'", "'listen'", 
 "'mainloop'", "'mode'", "'numinput'", 
 "'onkey'", "'onkeypress'", "'onkeyrelease'", 
 "'onscreenclick'", "'ontimer'", 
 "'register_shape'", "'resetscreen'", "'screensize'", 
 "'setup'", 
 "'setworldcoordinates'", "'textinput'", "'title'", "'tracer'", 
 "'turtles'", "'update'", 
 "'window_height'", "'window_width'"]
_tg_turtle_functions = ["'back'", "'backward'", "'begin_fill'", "'begin_poly'", "'bk'", 
 "'circle'", 
 "'clear'", "'clearstamp'", "'clearstamps'", "'clone'", "'color'", 
 "'degrees'", 
 "'distance'", "'dot'", "'down'", "'end_fill'", "'end_poly'", "'fd'", 
 "'fillcolor'", 
 "'filling'", "'forward'", "'get_poly'", "'getpen'", "'getscreen'", "'get_shapepoly'", 
 "'getturtle'", 
 "'goto'", "'heading'", "'hideturtle'", "'home'", "'ht'", "'isdown'", 
 "'isvisible'", 
 "'left'", "'lt'", "'onclick'", "'ondrag'", "'onrelease'", "'pd'", 
 "'pen'", 
 "'pencolor'", "'pendown'", "'pensize'", "'penup'", "'pos'", "'position'", 
 "'pu'", 
 "'radians'", "'right'", "'reset'", "'resizemode'", "'rt'", 
 "'seth'", 
 "'setheading'", "'setpos'", "'setposition'", "'settiltangle'", 
 "'setundobuffer'", 
 "'setx'", "'sety'", "'shape'", "'shapesize'", "'shapetransform'", "'shearfactor'", 
 "'showturtle'", 
 "'speed'", "'st'", "'stamp'", "'tilt'", "'tiltangle'", 
 "'towards'", 
 "'turtlesize'", "'undo'", "'undobufferentries'", "'up'", 
 "'width'", 
 "'write'", "'xcor'", "'ycor'"]
_tg_utilities = ['write_docstringdict', 'done']
__all__ = _tg_classes + _tg_screen_functions + _tg_turtle_functions + _tg_utilities + ['Terminator']
_alias_list = [
 "'addshape'", "'backward'", "'bk'", "'fd'", "'ht'", "'lt'", "'pd'", "'pos'", 
 "'pu'", 
 "'rt'", "'seth'", "'setpos'", "'setposition'", "'st'", 
 "'turtlesize'", 
 "'up'", "'width'"]
_CFG = {
 'width': 0.5, 
 'height': 0.75, 
 'canvwidth': 400, 
 'canvheight': 300, 
 'leftright': None, 
 'topbottom': None, 
 'mode': "'standard'", 
 'colormode': 1.0, 
 'delay': 10, 
 'undobuffersize': 1000, 
 'shape': "'classic'", 
 'pencolor': "'black'", 
 'fillcolor': "'black'", 
 'resizemode': "'noresize'", 
 'visible': True, 
 'language': "'english'", 
 'exampleturtle': "'turtle'", 
 'examplescreen': "'screen'", 
 'title': "'Python Turtle Graphics'", 
 'using_IDLE': False}

def config_dict(filename):
    with open(filename, 'r') as (f):
        cfglines = f.readlines()
    cfgdict = {}
    for line in cfglines:
        line = line.strip()
        if line:
            if line.startswith('#'):
                continue
            else:
                try:
                    key, value = line.split('=')
                except ValueError:
                    print('Bad line in config-file %s:\n%s' % (filename, line))
                    continue

                key = key.strip()
                value = value.strip()
                if value in ('True', 'False', 'None', "''", '""'):
                    value = eval(value)
                else:
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass

            cfgdict[key] = value

    return cfgdict


def readconfig(cfgdict):
    default_cfg = 'turtle.cfg'
    cfgdict1 = {}
    cfgdict2 = {}
    if isfile(default_cfg):
        cfgdict1 = config_dict(default_cfg)
    if 'importconfig' in cfgdict1:
        default_cfg = 'turtle_%s.cfg' % cfgdict1['importconfig']
    try:
        head, tail = split(__file__)
        cfg_file2 = join(head, default_cfg)
    except Exception:
        cfg_file2 = ''

    if isfile(cfg_file2):
        cfgdict2 = config_dict(cfg_file2)
    _CFG.update(cfgdict2)
    _CFG.update(cfgdict1)


try:
    readconfig(_CFG)
except Exception:
    print('No configfile read, reason unknown')

class Vec2D(tuple):

    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))

    def __add__(self, other):
        return Vec2D(self[0] + other[0], self[1] + other[1])

    def __mul__(self, other):
        if isinstance(other, Vec2D):
            return self[0] * other[0] + self[1] * other[1]
        return Vec2D(self[0] * other, self[1] * other)

    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vec2D(self[0] * other, self[1] * other)

    def __sub__(self, other):
        return Vec2D(self[0] - other[0], self[1] - other[1])

    def __neg__(self):
        return Vec2D(-self[0], -self[1])

    def __abs__(self):
        return (self[0] ** 2 + self[1] ** 2) ** 0.5

    def rotate(self, angle):
        perp = Vec2D(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        return Vec2D(self[0] * c + perp[0] * s, self[1] * c + perp[1] * s)

    def __getnewargs__(self):
        return (self[0], self[1])

    def __repr__(self):
        return '(%.2f,%.2f)' % self


def __methodDict(cls, _dict):
    baseList = list(cls.__bases__)
    baseList.reverse()
    for _super in baseList:
        __methodDict(_super, _dict)

    for key, value in cls.__dict__.items():
        if type(value) == types.FunctionType:
            _dict[key] = value


def __methods(cls):
    _dict = {}
    __methodDict(cls, _dict)
    return _dict.keys()


__stringBody = 'def %(method)s(self, *args, **kw): return self.%(attribute)s.%(method)s(*args, **kw)'

def __forwardmethods(fromClass, toClass, toPart, exclude=()):
    _dict_1 = {}
    __methodDict(toClass, _dict_1)
    _dict = {}
    mfc = __methods(fromClass)
    for ex in _dict_1.keys():
        if not ex[:1] == '_':
            if not ex[-1:] == '_':
                if not ex in exclude:
                    if ex in mfc:
                        continue
                    _dict[ex] = _dict_1[ex]

    for method, func in _dict.items():
        d = {'method':method, 
         'func':func}
        if isinstance(toPart, str):
            execString = __stringBody % {'method':method,  'attribute':toPart}
        exec(execString, d)
        setattr(fromClass, method, d[method])


class ScrolledCanvas(TK.Frame):

    def __init__(self, master, width=500, height=350, canvwidth=600, canvheight=500):
        TK.Frame.__init__(self, master, width=width, height=height)
        self._rootwindow = self.winfo_toplevel()
        self.width, self.height = width, height
        self.canvwidth, self.canvheight = canvwidth, canvheight
        self.bg = 'white'
        self._canvas = TK.Canvas(master, width=width, height=height, bg=(self.bg),
          relief=(TK.SUNKEN),
          borderwidth=2)
        self.hscroll = TK.Scrollbar(master, command=(self._canvas.xview), orient=(TK.HORIZONTAL))
        self.vscroll = TK.Scrollbar(master, command=(self._canvas.yview))
        self._canvas.configure(xscrollcommand=(self.hscroll.set), yscrollcommand=(self.vscroll.set))
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(0, weight=1, minsize=0)
        self._canvas.grid(padx=1, in_=self, pady=1, row=0, column=0,
          rowspan=1,
          columnspan=1,
          sticky='news')
        self.vscroll.grid(padx=1, in_=self, pady=1, row=0, column=1,
          rowspan=1,
          columnspan=1,
          sticky='news')
        self.hscroll.grid(padx=1, in_=self, pady=1, row=1, column=0,
          rowspan=1,
          columnspan=1,
          sticky='news')
        self.reset()
        self._rootwindow.bind('<Configure>', self.onResize)

    def reset(self, canvwidth=None, canvheight=None, bg=None):
        if canvwidth:
            self.canvwidth = canvwidth
        if canvheight:
            self.canvheight = canvheight
        if bg:
            self.bg = bg
        self._canvas.config(bg=bg, scrollregion=(
         -self.canvwidth // 2, -self.canvheight // 2,
         self.canvwidth // 2, self.canvheight // 2))
        self._canvas.xview_moveto(0.5 * (self.canvwidth - self.width + 30) / self.canvwidth)
        self._canvas.yview_moveto(0.5 * (self.canvheight - self.height + 30) / self.canvheight)
        self.adjustScrolls()

    def adjustScrolls(self):
        cwidth = self._canvas.winfo_width()
        cheight = self._canvas.winfo_height()
        self._canvas.xview_moveto(0.5 * (self.canvwidth - cwidth) / self.canvwidth)
        self._canvas.yview_moveto(0.5 * (self.canvheight - cheight) / self.canvheight)
        if cwidth < self.canvwidth or cheight < self.canvheight:
            self.hscroll.grid(padx=1, in_=self, pady=1, row=1, column=0,
              rowspan=1,
              columnspan=1,
              sticky='news')
            self.vscroll.grid(padx=1, in_=self, pady=1, row=0, column=1,
              rowspan=1,
              columnspan=1,
              sticky='news')
        else:
            self.hscroll.grid_forget()
            self.vscroll.grid_forget()

    def onResize(self, event):
        self.adjustScrolls()

    def bbox(self, *args):
        return (self._canvas.bbox)(*args)

    def cget(self, *args, **kwargs):
        return (self._canvas.cget)(*args, **kwargs)

    def config(self, *args, **kwargs):
        (self._canvas.config)(*args, **kwargs)

    def bind(self, *args, **kwargs):
        (self._canvas.bind)(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        (self._canvas.unbind)(*args, **kwargs)

    def focus_force(self):
        self._canvas.focus_force()


__forwardmethods(ScrolledCanvas, TK.Canvas, '_canvas')

class _Root(TK.Tk):

    def __init__(self):
        TK.Tk.__init__(self)

    def setupcanvas(self, width, height, cwidth, cheight):
        self._canvas = ScrolledCanvas(self, width, height, cwidth, cheight)
        self._canvas.pack(expand=1, fill='both')

    def _getcanvas(self):
        return self._canvas

    def set_geometry(self, width, height, startx, starty):
        self.geometry('%dx%d%+d%+d' % (width, height, startx, starty))

    def ondestroy(self, destroy):
        self.wm_protocol('WM_DELETE_WINDOW', destroy)

    def win_width(self):
        return self.winfo_screenwidth()

    def win_height(self):
        return self.winfo_screenheight()


Canvas = TK.Canvas

class TurtleScreenBase(object):

    @staticmethod
    def _blankimage():
        img = TK.PhotoImage(width=1, height=1)
        img.blank()
        return img

    @staticmethod
    def _image(filename):
        return TK.PhotoImage(file=filename)

    def __init__(self, cv):
        self.cv = cv
        if isinstance(cv, ScrolledCanvas):
            w = self.cv.canvwidth
            h = self.cv.canvheight
        else:
            w = int(self.cv.cget('width'))
            h = int(self.cv.cget('height'))
            self.cv.config(scrollregion=(-w // 2, -h // 2, w // 2, h // 2))
        self.canvwidth = w
        self.canvheight = h
        self.xscale = self.yscale = 1.0

    def _createpoly(self):
        return self.cv.create_polygon((0, 0, 0, 0, 0, 0), fill='', outline='')

    def _drawpoly(self, polyitem, coordlist, fill=None, outline=None, width=None, top=False):
        cl = []
        for x, y in coordlist:
            cl.append(x * self.xscale)
            cl.append(-y * self.yscale)

        (self.cv.coords)(polyitem, *cl)
        if fill is not None:
            self.cv.itemconfigure(polyitem, fill=fill)
        if outline is not None:
            self.cv.itemconfigure(polyitem, outline=outline)
        if width is not None:
            self.cv.itemconfigure(polyitem, width=width)
        if top:
            self.cv.tag_raise(polyitem)

    def _createline(self):
        return self.cv.create_line(0, 0, 0, 0, fill='', width=2, capstyle=(TK.ROUND))

    def _drawline(self, lineitem, coordlist=None, fill=None, width=None, top=False):
        if coordlist is not None:
            cl = []
            for x, y in coordlist:
                cl.append(x * self.xscale)
                cl.append(-y * self.yscale)

            (self.cv.coords)(lineitem, *cl)
        if fill is not None:
            self.cv.itemconfigure(lineitem, fill=fill)
        if width is not None:
            self.cv.itemconfigure(lineitem, width=width)
        if top:
            self.cv.tag_raise(lineitem)

    def _delete(self, item):
        self.cv.delete(item)

    def _update(self):
        self.cv.update()

    def _delay(self, delay):
        self.cv.after(delay)

    def _iscolorstring(self, color):
        try:
            rgb = self.cv.winfo_rgb(color)
            ok = True
        except TK.TclError:
            ok = False

        return ok

    def _bgcolor(self, color=None):
        if color is not None:
            self.cv.config(bg=color)
            self._update()
        else:
            return self.cv.cget('bg')

    def _write(self, pos, txt, align, font, pencolor):
        x, y = pos
        x = x * self.xscale
        y = y * self.yscale
        anchor = {'left':'sw',  'center':'s',  'right':'se'}
        item = self.cv.create_text((x - 1), (-y), text=txt, anchor=(anchor[align]), fill=pencolor,
          font=font)
        x0, y0, x1, y1 = self.cv.bbox(item)
        self.cv.update()
        return (item, x1 - 1)

    def _onclick(self, item, fun, num=1, add=None):
        if fun is None:
            self.cv.tag_unbind(item, '<Button-%s>' % num)
        else:

            def eventfun(event):
                x, y = self.cv.canvasx(event.x) / self.xscale, -self.cv.canvasy(event.y) / self.yscale
                fun(x, y)

            self.cv.tag_bind(item, '<Button-%s>' % num, eventfun, add)

    def _onrelease(self, item, fun, num=1, add=None):
        if fun is None:
            self.cv.tag_unbind(item, '<Button%s-ButtonRelease>' % num)
        else:

            def eventfun(event):
                x, y = self.cv.canvasx(event.x) / self.xscale, -self.cv.canvasy(event.y) / self.yscale
                fun(x, y)

            self.cv.tag_bind(item, '<Button%s-ButtonRelease>' % num, eventfun, add)

    def _ondrag(self, item, fun, num=1, add=None):
        if fun is None:
            self.cv.tag_unbind(item, '<Button%s-Motion>' % num)
        else:

            def eventfun(event):
                try:
                    x, y = self.cv.canvasx(event.x) / self.xscale, -self.cv.canvasy(event.y) / self.yscale
                    fun(x, y)
                except Exception:
                    pass

            self.cv.tag_bind(item, '<Button%s-Motion>' % num, eventfun, add)

    def _onscreenclick(self, fun, num=1, add=None):
        if fun is None:
            self.cv.unbind('<Button-%s>' % num)
        else:

            def eventfun(event):
                x, y = self.cv.canvasx(event.x) / self.xscale, -self.cv.canvasy(event.y) / self.yscale
                fun(x, y)

            self.cv.bind('<Button-%s>' % num, eventfun, add)

    def _onkeyrelease(self, fun, key):
        if fun is None:
            self.cv.unbind('<KeyRelease-%s>' % key, None)
        else:

            def eventfun(event):
                fun()

            self.cv.bind('<KeyRelease-%s>' % key, eventfun)

    def _onkeypress(self, fun, key=None):
        if fun is None:
            if key is None:
                self.cv.unbind('<KeyPress>', None)
            else:
                self.cv.unbind('<KeyPress-%s>' % key, None)
        else:

            def eventfun(event):
                fun()

            if key is None:
                self.cv.bind('<KeyPress>', eventfun)
            else:
                self.cv.bind('<KeyPress-%s>' % key, eventfun)

    def _listen(self):
        self.cv.focus_force()

    def _ontimer(self, fun, t):
        if t == 0:
            self.cv.after_idle(fun)
        else:
            self.cv.after(t, fun)

    def _createimage(self, image):
        return self.cv.create_image(0, 0, image=image)

    def _drawimage(self, item, pos, image):
        x, y = pos
        self.cv.coords(item, (x * self.xscale, -y * self.yscale))
        self.cv.itemconfig(item, image=image)

    def _setbgpic(self, item, image):
        self.cv.itemconfig(item, image=image)
        self.cv.tag_lower(item)

    def _type(self, item):
        return self.cv.type(item)

    def _pointlist(self, item):
        cl = self.cv.coords(item)
        pl = [(cl[i], -cl[i + 1]) for i in range(0, len(cl), 2)]
        return pl

    def _setscrollregion(self, srx1, sry1, srx2, sry2):
        self.cv.config(scrollregion=(srx1, sry1, srx2, sry2))

    def _rescale(self, xscalefactor, yscalefactor):
        items = self.cv.find_all()
        for item in items:
            coordinates = list(self.cv.coords(item))
            newcoordlist = []
            while coordinates:
                x, y = coordinates[:2]
                newcoordlist.append(x * xscalefactor)
                newcoordlist.append(y * yscalefactor)
                coordinates = coordinates[2:]

            (self.cv.coords)(item, *newcoordlist)

    def _resize(self, canvwidth=None, canvheight=None, bg=None):
        if not isinstance(self.cv, ScrolledCanvas):
            return (
             self.canvwidth, self.canvheight)
        if canvwidth is canvheight is bg is None:
            return (
             self.cv.canvwidth, self.cv.canvheight)
        if canvwidth is not None:
            self.canvwidth = canvwidth
        if canvheight is not None:
            self.canvheight = canvheight
        self.cv.reset(canvwidth, canvheight, bg)

    def _window_size(self):
        width = self.cv.winfo_width()
        if width <= 1:
            width = self.cv['width']
        height = self.cv.winfo_height()
        if height <= 1:
            height = self.cv['height']
        return (
         width, height)

    def mainloop(self):
        TK.mainloop()

    def textinput(self, title, prompt):
        return simpledialog.askstring(title, prompt)

    def numinput(self, title, prompt, default=None, minval=None, maxval=None):
        return simpledialog.askfloat(title, prompt, initialvalue=default, minvalue=minval,
          maxvalue=maxval)


class Terminator(Exception):
    pass


class TurtleGraphicsError(Exception):
    pass


class Shape(object):

    def __init__(self, type_, data=None):
        self._type = type_
        if type_ == 'polygon':
            if isinstance(data, list):
                data = tuple(data)
        elif type_ == 'image':
            if isinstance(data, str) and data.lower().endswith('.gif') and isfile(data):
                data = TurtleScreen._image(data)
        elif type_ == 'compound':
            data = []
        else:
            raise TurtleGraphicsError('There is no shape type %s' % type_)
        self._data = data

    def addcomponent(self, poly, fill, outline=None):
        if self._type != 'compound':
            raise TurtleGraphicsError('Cannot add component to %s Shape' % self._type)
        if outline is None:
            outline = fill
        self._data.append([poly, fill, outline])


class Tbuffer(object):

    def __init__(self, bufsize=10):
        self.bufsize = bufsize
        self.buffer = [[None]] * bufsize
        self.ptr = -1
        self.cumulate = False

    def reset(self, bufsize=None):
        if bufsize is None:
            for i in range(self.bufsize):
                self.buffer[i] = [
                 None]

        else:
            self.bufsize = bufsize
            self.buffer = [[None]] * bufsize
        self.ptr = -1

    def push(self, item):
        if self.bufsize > 0:
            if not self.cumulate:
                self.ptr = (self.ptr + 1) % self.bufsize
                self.buffer[self.ptr] = item
            else:
                self.buffer[self.ptr].append(item)

    def pop(self):
        if self.bufsize > 0:
            item = self.buffer[self.ptr]
            if item is None:
                return
            self.buffer[self.ptr] = [
             None]
            self.ptr = (self.ptr - 1) % self.bufsize
            return item

    def nr_of_items(self):
        return self.bufsize - self.buffer.count([None])

    def __repr__(self):
        return str(self.buffer) + ' ' + str(self.ptr)


class TurtleScreen(TurtleScreenBase):
    _RUNNING = True

    def __init__(self, cv, mode=_CFG['mode'], colormode=_CFG['colormode'], delay=_CFG['delay']):
        self._shapes = {'arrow':Shape('polygon', ((-10, 0), (10, 0), (0, 10))), 
         'turtle':Shape('polygon', ((0, 16), (-2, 14), (-1, 10), (-4, 7), (-7, 9), (-9, 8), (-6, 5),
                  (-7, 1), (-5, -3), (-8, -6), (-6, -8), (-4, -5), (0, -7), (4, -5),
                  (6, -8), (8, -6), (5, -3), (7, 1), (6, 5), (9, 8), (7, 9), (4, 7),
                  (1, 10), (2, 14))), 
         'circle':Shape('polygon', ((10, 0), (9.51, 3.09), (8.09, 5.88), (5.88, 8.09), (3.09, 9.51),
                  (0, 10), (-3.09, 9.51), (-5.88, 8.09), (-8.09, 5.88), (-9.51, 3.09),
                  (-10, 0), (-9.51, -3.09), (-8.09, -5.88), (-5.88, -8.09), (-3.09, -9.51),
                  (-0.0, -10.0), (3.09, -9.51), (5.88, -8.09), (8.09, -5.88), (9.51, -3.09))), 
         'square':Shape('polygon', ((10, -10), (10, 10), (-10, 10), (-10, -10))), 
         'triangle':Shape('polygon', ((10, -5.77), (0, 11.55), (-10, -5.77))), 
         'classic':Shape('polygon', ((0, 0), (-5, -9), (0, -7), (5, -9))), 
         'blank':Shape('image', self._blankimage())}
        self._bgpics = {'nopic': ''}
        TurtleScreenBase.__init__(self, cv)
        self._mode = mode
        self._delayvalue = delay
        self._colormode = _CFG['colormode']
        self._keys = []
        self.clear()
        if sys.platform == 'darwin':
            rootwindow = cv.winfo_toplevel()
            rootwindow.call('wm', 'attributes', '.', '-topmost', '1')
            rootwindow.call('wm', 'attributes', '.', '-topmost', '0')

    def clear(self):
        self._delayvalue = _CFG['delay']
        self._colormode = _CFG['colormode']
        self._delete('all')
        self._bgpic = self._createimage('')
        self._bgpicname = 'nopic'
        self._tracing = 1
        self._updatecounter = 0
        self._turtles = []
        self.bgcolor('white')
        for btn in (1, 2, 3):
            self.onclick(None, btn)

        self.onkeypress(None)
        for key in self._keys[:]:
            self.onkey(None, key)
            self.onkeypress(None, key)

        Turtle._pen = None

    def mode(self, mode=None):
        if mode is None:
            return self._mode
        mode = mode.lower()
        if mode not in ('standard', 'logo', 'world'):
            raise TurtleGraphicsError('No turtle-graphics-mode %s' % mode)
        self._mode = mode
        if mode in ('standard', 'logo'):
            self._setscrollregion(-self.canvwidth // 2, -self.canvheight // 2, self.canvwidth // 2, self.canvheight // 2)
            self.xscale = self.yscale = 1.0
        self.reset()

    def setworldcoordinates(self, llx, lly, urx, ury):
        if self.mode() != 'world':
            self.mode('world')
        xspan = float(urx - llx)
        yspan = float(ury - lly)
        wx, wy = self._window_size()
        self.screensize(wx - 20, wy - 20)
        oldxscale, oldyscale = self.xscale, self.yscale
        self.xscale = self.canvwidth / xspan
        self.yscale = self.canvheight / yspan
        srx1 = llx * self.xscale
        sry1 = -ury * self.yscale
        srx2 = self.canvwidth + srx1
        sry2 = self.canvheight + sry1
        self._setscrollregion(srx1, sry1, srx2, sry2)
        self._rescale(self.xscale / oldxscale, self.yscale / oldyscale)
        self.update()

    def register_shape(self, name, shape=None):
        if shape is None:
            if name.lower().endswith('.gif'):
                shape = Shape('image', self._image(name))
            else:
                raise TurtleGraphicsError('Bad arguments for register_shape.\nUse  help(register_shape)')
        elif isinstance(shape, tuple):
            shape = Shape('polygon', shape)
        self._shapes[name] = shape

    def _colorstr--- This code section failed: ---

 L.1152         0  LOAD_GLOBAL              len
                2  LOAD_FAST                'color'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  LOAD_CONST               1
                8  COMPARE_OP               ==
               10  POP_JUMP_IF_FALSE    20  'to 20'

 L.1153        12  LOAD_FAST                'color'
               14  LOAD_CONST               0
               16  BINARY_SUBSCR    
               18  STORE_FAST               'color'
             20_0  COME_FROM            10  '10'

 L.1154        20  LOAD_GLOBAL              isinstance
               22  LOAD_FAST                'color'
               24  LOAD_GLOBAL              str
               26  CALL_FUNCTION_2       2  '2 positional arguments'
               28  POP_JUMP_IF_FALSE    68  'to 68'

 L.1155        30  LOAD_FAST                'self'
               32  LOAD_METHOD              _iscolorstring
               34  LOAD_FAST                'color'
               36  CALL_METHOD_1         1  '1 positional argument'
               38  POP_JUMP_IF_TRUE     48  'to 48'
               40  LOAD_FAST                'color'
               42  LOAD_STR                 ''
               44  COMPARE_OP               ==
               46  POP_JUMP_IF_FALSE    52  'to 52'
             48_0  COME_FROM            38  '38'

 L.1156        48  LOAD_FAST                'color'
               50  RETURN_VALUE     
             52_0  COME_FROM            46  '46'

 L.1158        52  LOAD_GLOBAL              TurtleGraphicsError
               54  LOAD_STR                 'bad color string: %s'
               56  LOAD_GLOBAL              str
               58  LOAD_FAST                'color'
               60  CALL_FUNCTION_1       1  '1 positional argument'
               62  BINARY_MODULO    
               64  CALL_FUNCTION_1       1  '1 positional argument'
               66  RAISE_VARARGS_1       1  'exception instance'
             68_0  COME_FROM            28  '28'

 L.1159        68  SETUP_EXCEPT         84  'to 84'

 L.1160        70  LOAD_FAST                'color'
               72  UNPACK_SEQUENCE_3     3 
               74  STORE_FAST               'r'
               76  STORE_FAST               'g'
               78  STORE_FAST               'b'
               80  POP_BLOCK        
               82  JUMP_FORWARD        124  'to 124'
             84_0  COME_FROM_EXCEPT     68  '68'

 L.1161        84  DUP_TOP          
               86  LOAD_GLOBAL              TypeError
               88  LOAD_GLOBAL              ValueError
               90  BUILD_TUPLE_2         2 
               92  COMPARE_OP               exception-match
               94  POP_JUMP_IF_FALSE   122  'to 122'
               96  POP_TOP          
               98  POP_TOP          
              100  POP_TOP          

 L.1162       102  LOAD_GLOBAL              TurtleGraphicsError
              104  LOAD_STR                 'bad color arguments: %s'
              106  LOAD_GLOBAL              str
              108  LOAD_FAST                'color'
              110  CALL_FUNCTION_1       1  '1 positional argument'
              112  BINARY_MODULO    
              114  CALL_FUNCTION_1       1  '1 positional argument'
              116  RAISE_VARARGS_1       1  'exception instance'
              118  POP_EXCEPT       
              120  JUMP_FORWARD        124  'to 124'
            122_0  COME_FROM            94  '94'
              122  END_FINALLY      
            124_0  COME_FROM           120  '120'
            124_1  COME_FROM            82  '82'

 L.1163       124  LOAD_FAST                'self'
              126  LOAD_ATTR                _colormode
              128  LOAD_CONST               1.0
              130  COMPARE_OP               ==
              132  POP_JUMP_IF_FALSE   160  'to 160'

 L.1164       134  LOAD_LISTCOMP            '<code_object <listcomp>>'
              136  LOAD_STR                 'TurtleScreen._colorstr.<locals>.<listcomp>'
              138  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              140  LOAD_FAST                'r'
              142  LOAD_FAST                'g'
              144  LOAD_FAST                'b'
              146  BUILD_TUPLE_3         3 
              148  GET_ITER         
              150  CALL_FUNCTION_1       1  '1 positional argument'
              152  UNPACK_SEQUENCE_3     3 
              154  STORE_FAST               'r'
              156  STORE_FAST               'g'
              158  STORE_FAST               'b'
            160_0  COME_FROM           132  '132'

 L.1165       160  LOAD_CONST               0
              162  LOAD_FAST                'r'
              164  DUP_TOP          
              166  ROT_THREE        
              168  COMPARE_OP               <=
              170  POP_JUMP_IF_FALSE   180  'to 180'
              172  LOAD_CONST               255
              174  COMPARE_OP               <=
              176  POP_JUMP_IF_FALSE   230  'to 230'
              178  JUMP_FORWARD        184  'to 184'
            180_0  COME_FROM           170  '170'
              180  POP_TOP          
              182  JUMP_FORWARD        230  'to 230'
            184_0  COME_FROM           178  '178'
              184  LOAD_CONST               0
              186  LOAD_FAST                'g'
              188  DUP_TOP          
              190  ROT_THREE        
              192  COMPARE_OP               <=
              194  POP_JUMP_IF_FALSE   204  'to 204'
              196  LOAD_CONST               255
              198  COMPARE_OP               <=
              200  POP_JUMP_IF_FALSE   230  'to 230'
              202  JUMP_FORWARD        208  'to 208'
            204_0  COME_FROM           194  '194'
              204  POP_TOP          
              206  JUMP_FORWARD        230  'to 230'
            208_0  COME_FROM           202  '202'
              208  LOAD_CONST               0
              210  LOAD_FAST                'b'
              212  DUP_TOP          
              214  ROT_THREE        
              216  COMPARE_OP               <=
              218  POP_JUMP_IF_FALSE   228  'to 228'
              220  LOAD_CONST               255
              222  COMPARE_OP               <=
              224  POP_JUMP_IF_TRUE    246  'to 246'
              226  JUMP_FORWARD        230  'to 230'
            228_0  COME_FROM           218  '218'
              228  POP_TOP          
            230_0  COME_FROM           226  '226'
            230_1  COME_FROM           206  '206'
            230_2  COME_FROM           200  '200'
            230_3  COME_FROM           182  '182'
            230_4  COME_FROM           176  '176'

 L.1166       230  LOAD_GLOBAL              TurtleGraphicsError
              232  LOAD_STR                 'bad color sequence: %s'
              234  LOAD_GLOBAL              str
              236  LOAD_FAST                'color'
              238  CALL_FUNCTION_1       1  '1 positional argument'
              240  BINARY_MODULO    
              242  CALL_FUNCTION_1       1  '1 positional argument'
              244  RAISE_VARARGS_1       1  'exception instance'
            246_0  COME_FROM           224  '224'

 L.1167       246  LOAD_STR                 '#%02x%02x%02x'
              248  LOAD_FAST                'r'
              250  LOAD_FAST                'g'
              252  LOAD_FAST                'b'
              254  BUILD_TUPLE_3         3 
              256  BINARY_MODULO    
              258  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 246_0

    def _color(self, cstr):
        if not cstr.startswith('#'):
            return cstr
        elif len(cstr) == 7:
            cl = [int(cstr[i:i + 2], 16) for i in (1, 3, 5)]
        else:
            if len(cstr) == 4:
                cl = [16 * int(cstr[h], 16) for h in cstr[1:]]
            else:
                raise TurtleGraphicsError('bad colorstring: %s' % cstr)
        return tuple((c * self._colormode / 255 for c in cl))

    def colormode(self, cmode=None):
        if cmode is None:
            return self._colormode
        elif cmode == 1.0:
            self._colormode = float(cmode)
        else:
            if cmode == 255:
                self._colormode = int(cmode)

    def reset(self):
        for turtle in self._turtles:
            turtle._setmode(self._mode)
            turtle.reset()

    def turtles(self):
        return self._turtles

    def bgcolor(self, *args):
        if args:
            color = self._colorstr(args)
        else:
            color = None
        color = self._bgcolor(color)
        if color is not None:
            color = self._color(color)
        return color

    def tracer(self, n=None, delay=None):
        if n is None:
            return self._tracing
        self._tracing = int(n)
        self._updatecounter = 0
        if delay is not None:
            self._delayvalue = int(delay)
        if self._tracing:
            self.update()

    def delay(self, delay=None):
        if delay is None:
            return self._delayvalue
        self._delayvalue = int(delay)

    def _incrementudc(self):
        if not TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = True
            raise Terminator
        if self._tracing > 0:
            self._updatecounter += 1
            self._updatecounter %= self._tracing

    def update(self):
        tracing = self._tracing
        self._tracing = True
        for t in self.turtles():
            t._update_data()
            t._drawturtle()

        self._tracing = tracing
        self._update()

    def window_width(self):
        return self._window_size()[0]

    def window_height(self):
        return self._window_size()[1]

    def getcanvas(self):
        return self.cv

    def getshapes(self):
        return sorted(self._shapes.keys())

    def onclick(self, fun, btn=1, add=None):
        self._onscreenclick(fun, btn, add)

    def onkey(self, fun, key):
        if fun is None:
            if key in self._keys:
                self._keys.remove(key)
        elif key not in self._keys:
            self._keys.append(key)
        self._onkeyrelease(fun, key)

    def onkeypress(self, fun, key=None):
        if fun is None:
            if key in self._keys:
                self._keys.remove(key)
        elif key is not None:
            if key not in self._keys:
                self._keys.append(key)
        self._onkeypress(fun, key)

    def listen(self, xdummy=None, ydummy=None):
        self._listen()

    def ontimer(self, fun, t=0):
        self._ontimer(fun, t)

    def bgpic(self, picname=None):
        if picname is None:
            return self._bgpicname
        if picname not in self._bgpics:
            self._bgpics[picname] = self._image(picname)
        self._setbgpic(self._bgpic, self._bgpics[picname])
        self._bgpicname = picname

    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        return self._resize(canvwidth, canvheight, bg)

    onscreenclick = onclick
    resetscreen = reset
    clearscreen = clear
    addshape = register_shape
    onkeyrelease = onkey


class TNavigator(object):
    START_ORIENTATION = {'standard':Vec2D(1.0, 0.0), 
     'world':Vec2D(1.0, 0.0), 
     'logo':Vec2D(0.0, 1.0)}
    DEFAULT_MODE = 'standard'
    DEFAULT_ANGLEOFFSET = 0
    DEFAULT_ANGLEORIENT = 1

    def __init__(self, mode=DEFAULT_MODE):
        self._angleOffset = self.DEFAULT_ANGLEOFFSET
        self._angleOrient = self.DEFAULT_ANGLEORIENT
        self._mode = mode
        self.undobuffer = None
        self.degrees()
        self._mode = None
        self._setmode(mode)
        TNavigator.reset(self)

    def reset(self):
        self._position = Vec2D(0.0, 0.0)
        self._orient = TNavigator.START_ORIENTATION[self._mode]

    def _setmode(self, mode=None):
        if mode is None:
            return self._mode
            if mode not in ('standard', 'logo', 'world'):
                return
            self._mode = mode
            if mode in ('standard', 'world'):
                self._angleOffset = 0
                self._angleOrient = 1
        else:
            self._angleOffset = self._fullcircle / 4.0
            self._angleOrient = -1

    def _setDegreesPerAU(self, fullcircle):
        self._fullcircle = fullcircle
        self._degreesPerAU = 360 / fullcircle
        if self._mode == 'standard':
            self._angleOffset = 0
        else:
            self._angleOffset = fullcircle / 4.0

    def degrees(self, fullcircle=360.0):
        self._setDegreesPerAU(fullcircle)

    def radians(self):
        self._setDegreesPerAU(2 * math.pi)

    def _go(self, distance):
        ende = self._position + self._orient * distance
        self._goto(ende)

    def _rotate(self, angle):
        angle *= self._degreesPerAU
        self._orient = self._orient.rotate(angle)

    def _goto(self, end):
        self._position = end

    def forward(self, distance):
        self._go(distance)

    def back(self, distance):
        self._go(-distance)

    def right(self, angle):
        self._rotate(-angle)

    def left(self, angle):
        self._rotate(angle)

    def pos(self):
        return self._position

    def xcor(self):
        return self._position[0]

    def ycor(self):
        return self._position[1]

    def goto(self, x, y=None):
        if y is None:
            self._goto(Vec2D(*x))
        else:
            self._goto(Vec2D(x, y))

    def home(self):
        self.goto(0, 0)
        self.setheading(0)

    def setx(self, x):
        self._goto(Vec2D(x, self._position[1]))

    def sety(self, y):
        self._goto(Vec2D(self._position[0], y))

    def distance(self, x, y=None):
        if y is not None:
            pos = Vec2D(x, y)
        elif isinstance(x, Vec2D):
            pos = x
        else:
            if isinstance(x, tuple):
                pos = Vec2D(*x)
            else:
                if isinstance(x, TNavigator):
                    pos = x._position
        return abs(pos - self._position)

    def towards(self, x, y=None):
        if y is not None:
            pos = Vec2D(x, y)
        elif isinstance(x, Vec2D):
            pos = x
        else:
            if isinstance(x, tuple):
                pos = Vec2D(*x)
            else:
                if isinstance(x, TNavigator):
                    pos = x._position
        x, y = pos - self._position
        result = round(math.atan2(y, x) * 180.0 / math.pi, 10) % 360.0
        result /= self._degreesPerAU
        return (self._angleOffset + self._angleOrient * result) % self._fullcircle

    def heading(self):
        x, y = self._orient
        result = round(math.atan2(y, x) * 180.0 / math.pi, 10) % 360.0
        result /= self._degreesPerAU
        return (self._angleOffset + self._angleOrient * result) % self._fullcircle

    def setheading(self, to_angle):
        angle = (to_angle - self.heading()) * self._angleOrient
        full = self._fullcircle
        angle = (angle + full / 2.0) % full - full / 2.0
        self._rotate(angle)

    def circle(self, radius, extent=None, steps=None):
        if self.undobuffer:
            self.undobuffer.push(['seq'])
            self.undobuffer.cumulate = True
        else:
            speed = self.speed()
            if extent is None:
                extent = self._fullcircle
            if steps is None:
                frac = abs(extent) / self._fullcircle
                steps = 1 + int(min(11 + abs(radius) / 6.0, 59.0) * frac)
            w = 1.0 * extent / steps
            w2 = 0.5 * w
            l = 2.0 * radius * math.sin(w2 * math.pi / 180.0 * self._degreesPerAU)
            if radius < 0:
                l, w, w2 = -l, -w, -w2
            tr = self._tracer()
            dl = self._delay()
            if speed == 0:
                self._tracer(0, 0)
            else:
                self.speed(0)
        self._rotate(w2)
        for i in range(steps):
            self.speed(speed)
            self._go(l)
            self.speed(0)
            self._rotate(w)

        self._rotate(-w2)
        if speed == 0:
            self._tracer(tr, dl)
        self.speed(speed)
        if self.undobuffer:
            self.undobuffer.cumulate = False

    def speed(self, s=0):
        pass

    def _tracer(self, a=None, b=None):
        pass

    def _delay(self, n=None):
        pass

    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    position = pos
    setpos = goto
    setposition = goto
    seth = setheading


class TPen(object):

    def __init__(self, resizemode=_CFG['resizemode']):
        self._resizemode = resizemode
        self.undobuffer = None
        TPen._reset(self)

    def _reset(self, pencolor=_CFG['pencolor'], fillcolor=_CFG['fillcolor']):
        self._pensize = 1
        self._shown = True
        self._pencolor = pencolor
        self._fillcolor = fillcolor
        self._drawing = True
        self._speed = 3
        self._stretchfactor = (1.0, 1.0)
        self._shearfactor = 0.0
        self._tilt = 0.0
        self._shapetrafo = (1.0, 0.0, 0.0, 1.0)
        self._outlinewidth = 1

    def resizemode(self, rmode=None):
        if rmode is None:
            return self._resizemode
        rmode = rmode.lower()
        if rmode in ('auto', 'user', 'noresize'):
            self.pen(resizemode=rmode)

    def pensize(self, width=None):
        if width is None:
            return self._pensize
        self.pen(pensize=width)

    def penup(self):
        if not self._drawing:
            return
        self.pen(pendown=False)

    def pendown(self):
        if self._drawing:
            return
        self.pen(pendown=True)

    def isdown(self):
        return self._drawing

    def speed(self, speed=None):
        speeds = {
         'fastest': 0, 'fast': 10, 'normal': 6, 'slow': 3, 'slowest': 1}
        if speed is None:
            return self._speed
        if speed in speeds:
            speed = speeds[speed]
        else:
            if 0.5 < speed < 10.5:
                speed = int(round(speed))
            else:
                speed = 0
        self.pen(speed=speed)

    def color(self, *args):
        if args:
            l = len(args)
            if l == 1:
                pcolor = fcolor = args[0]
            else:
                if l == 2:
                    pcolor, fcolor = args
                else:
                    if l == 3:
                        pcolor = fcolor = args
            pcolor = self._colorstr(pcolor)
            fcolor = self._colorstr(fcolor)
            self.pen(pencolor=pcolor, fillcolor=fcolor)
        else:
            return (
             self._color(self._pencolor), self._color(self._fillcolor))

    def pencolor(self, *args):
        if args:
            color = self._colorstr(args)
            if color == self._pencolor:
                return
            self.pen(pencolor=color)
        else:
            return self._color(self._pencolor)

    def fillcolor(self, *args):
        if args:
            color = self._colorstr(args)
            if color == self._fillcolor:
                return
            self.pen(fillcolor=color)
        else:
            return self._color(self._fillcolor)

    def showturtle(self):
        self.pen(shown=True)

    def hideturtle(self):
        self.pen(shown=False)

    def isvisible(self):
        return self._shown

    def pen(self, pen=None, **pendict):
        _pd = {'shown':self._shown, 
         'pendown':self._drawing, 
         'pencolor':self._pencolor, 
         'fillcolor':self._fillcolor, 
         'pensize':self._pensize, 
         'speed':self._speed, 
         'resizemode':self._resizemode, 
         'stretchfactor':self._stretchfactor, 
         'shearfactor':self._shearfactor, 
         'outline':self._outlinewidth, 
         'tilt':self._tilt}
        if not pen:
            if not pendict:
                return _pd
        elif isinstance(pen, dict):
            p = pen
        else:
            p = {}
        p.update(pendict)
        _p_buf = {}
        for key in p:
            _p_buf[key] = _pd[key]

        if self.undobuffer:
            self.undobuffer.push(('pen', _p_buf))
        newLine = False
        if 'pendown' in p:
            if self._drawing != p['pendown']:
                newLine = True
        if 'pencolor' in p:
            if isinstance(p['pencolor'], tuple):
                p['pencolor'] = self._colorstr((p['pencolor'],))
            if self._pencolor != p['pencolor']:
                newLine = True
        if 'pensize' in p:
            if self._pensize != p['pensize']:
                newLine = True
        if newLine:
            self._newLine()
        if 'pendown' in p:
            self._drawing = p['pendown']
        if 'pencolor' in p:
            self._pencolor = p['pencolor']
        if 'pensize' in p:
            self._pensize = p['pensize']
        if 'fillcolor' in p:
            if isinstance(p['fillcolor'], tuple):
                p['fillcolor'] = self._colorstr((p['fillcolor'],))
            self._fillcolor = p['fillcolor']
        if 'speed' in p:
            self._speed = p['speed']
        if 'resizemode' in p:
            self._resizemode = p['resizemode']
        if 'stretchfactor' in p:
            sf = p['stretchfactor']
            if isinstance(sf, (int, float)):
                sf = (
                 sf, sf)
            self._stretchfactor = sf
        if 'shearfactor' in p:
            self._shearfactor = p['shearfactor']
        if 'outline' in p:
            self._outlinewidth = p['outline']
        if 'shown' in p:
            self._shown = p['shown']
        if 'tilt' in p:
            self._tilt = p['tilt']
        if 'stretchfactor' in p or 'tilt' in p or 'shearfactor' in p:
            scx, scy = self._stretchfactor
            shf = self._shearfactor
            sa, ca = math.sin(self._tilt), math.cos(self._tilt)
            self._shapetrafo = (scx * ca, scy * (shf * ca + sa),
             -scx * sa, scy * (ca - shf * sa))
        self._update()

    def _newLine(self, usePos=True):
        pass

    def _update(self, count=True, forced=False):
        pass

    def _color(self, args):
        pass

    def _colorstr(self, args):
        pass

    width = pensize
    up = penup
    pu = penup
    pd = pendown
    down = pendown
    st = showturtle
    ht = hideturtle


class _TurtleImage(object):

    def __init__(self, screen, shapeIndex):
        self.screen = screen
        self._type = None
        self._setshape(shapeIndex)

    def _setshape(self, shapeIndex):
        screen = self.screen
        self.shapeIndex = shapeIndex
        if self._type == 'polygon' == screen._shapes[shapeIndex]._type:
            return
        if self._type == 'image' == screen._shapes[shapeIndex]._type:
            return
        if self._type in ('image', 'polygon'):
            screen._delete(self._item)
        else:
            if self._type == 'compound':
                for item in self._item:
                    screen._delete(item)

            else:
                self._type = screen._shapes[shapeIndex]._type
                if self._type == 'polygon':
                    self._item = screen._createpoly()
                else:
                    if self._type == 'image':
                        self._item = screen._createimage(screen._shapes['blank']._data)
                    else:
                        if self._type == 'compound':
                            self._item = [screen._createpoly() for item in screen._shapes[shapeIndex]._data]


class RawTurtle(TPen, TNavigator):
    screens = []

    def __init__(self, canvas=None, shape=_CFG['shape'], undobuffersize=_CFG['undobuffersize'], visible=_CFG['visible']):
        if isinstance(canvas, _Screen):
            self.screen = canvas
        else:
            if isinstance(canvas, TurtleScreen):
                if canvas not in RawTurtle.screens:
                    RawTurtle.screens.append(canvas)
                self.screen = canvas
            else:
                if isinstance(canvas, (ScrolledCanvas, Canvas)):
                    for screen in RawTurtle.screens:
                        if screen.cv == canvas:
                            self.screen = screen
                            break
                    else:
                        self.screen = TurtleScreen(canvas)
                        RawTurtle.screens.append(self.screen)

                else:
                    raise TurtleGraphicsError('bad canvas argument %s' % canvas)
        screen = self.screen
        TNavigator.__init__(self, screen.mode())
        TPen.__init__(self)
        screen._turtles.append(self)
        self.drawingLineItem = screen._createline()
        self.turtle = _TurtleImage(screen, shape)
        self._poly = None
        self._creatingPoly = False
        self._fillitem = self._fillpath = None
        self._shown = visible
        self._hidden_from_screen = False
        self.currentLineItem = screen._createline()
        self.currentLine = [self._position]
        self.items = [self.currentLineItem]
        self.stampItems = []
        self._undobuffersize = undobuffersize
        self.undobuffer = Tbuffer(undobuffersize)
        self._update()

    def reset(self):
        TNavigator.reset(self)
        TPen._reset(self)
        self._clear()
        self._drawturtle()
        self._update()

    def setundobuffer(self, size):
        if size is None or size <= 0:
            self.undobuffer = None
        else:
            self.undobuffer = Tbuffer(size)

    def undobufferentries(self):
        if self.undobuffer is None:
            return 0
        return self.undobuffer.nr_of_items()

    def _clear(self):
        self._fillitem = self._fillpath = None
        for item in self.items:
            self.screen._delete(item)

        self.currentLineItem = self.screen._createline()
        self.currentLine = []
        if self._drawing:
            self.currentLine.append(self._position)
        self.items = [
         self.currentLineItem]
        self.clearstamps()
        self.setundobuffer(self._undobuffersize)

    def clear(self):
        self._clear()
        self._update()

    def _update_data(self):
        self.screen._incrementudc()
        if self.screen._updatecounter != 0:
            return
        if len(self.currentLine) > 1:
            self.screen._drawline(self.currentLineItem, self.currentLine, self._pencolor, self._pensize)

    def _update(self):
        screen = self.screen
        if screen._tracing == 0:
            return
        if screen._tracing == 1:
            self._update_data()
            self._drawturtle()
            screen._update()
            screen._delay(screen._delayvalue)
        else:
            self._update_data()
            if screen._updatecounter == 0:
                for t in screen.turtles():
                    t._drawturtle()

                screen._update()

    def _tracer(self, flag=None, delay=None):
        return self.screen.tracer(flag, delay)

    def _color(self, args):
        return self.screen._color(args)

    def _colorstr(self, args):
        return self.screen._colorstr(args)

    def _cc--- This code section failed: ---

 L.2701         0  LOAD_GLOBAL              isinstance
                2  LOAD_FAST                'args'
                4  LOAD_GLOBAL              str
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  POP_JUMP_IF_FALSE    14  'to 14'

 L.2702        10  LOAD_FAST                'args'
               12  RETURN_VALUE     
             14_0  COME_FROM             8  '8'

 L.2703        14  SETUP_EXCEPT         30  'to 30'

 L.2704        16  LOAD_FAST                'args'
               18  UNPACK_SEQUENCE_3     3 
               20  STORE_FAST               'r'
               22  STORE_FAST               'g'
               24  STORE_FAST               'b'
               26  POP_BLOCK        
               28  JUMP_FORWARD         70  'to 70'
             30_0  COME_FROM_EXCEPT     14  '14'

 L.2705        30  DUP_TOP          
               32  LOAD_GLOBAL              TypeError
               34  LOAD_GLOBAL              ValueError
               36  BUILD_TUPLE_2         2 
               38  COMPARE_OP               exception-match
               40  POP_JUMP_IF_FALSE    68  'to 68'
               42  POP_TOP          
               44  POP_TOP          
               46  POP_TOP          

 L.2706        48  LOAD_GLOBAL              TurtleGraphicsError
               50  LOAD_STR                 'bad color arguments: %s'
               52  LOAD_GLOBAL              str
               54  LOAD_FAST                'args'
               56  CALL_FUNCTION_1       1  '1 positional argument'
               58  BINARY_MODULO    
               60  CALL_FUNCTION_1       1  '1 positional argument'
               62  RAISE_VARARGS_1       1  'exception instance'
               64  POP_EXCEPT       
               66  JUMP_FORWARD         70  'to 70'
             68_0  COME_FROM            40  '40'
               68  END_FINALLY      
             70_0  COME_FROM            66  '66'
             70_1  COME_FROM            28  '28'

 L.2707        70  LOAD_FAST                'self'
               72  LOAD_ATTR                screen
               74  LOAD_ATTR                _colormode
               76  LOAD_CONST               1.0
               78  COMPARE_OP               ==
               80  POP_JUMP_IF_FALSE   108  'to 108'

 L.2708        82  LOAD_LISTCOMP            '<code_object <listcomp>>'
               84  LOAD_STR                 'RawTurtle._cc.<locals>.<listcomp>'
               86  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               88  LOAD_FAST                'r'
               90  LOAD_FAST                'g'
               92  LOAD_FAST                'b'
               94  BUILD_TUPLE_3         3 
               96  GET_ITER         
               98  CALL_FUNCTION_1       1  '1 positional argument'
              100  UNPACK_SEQUENCE_3     3 
              102  STORE_FAST               'r'
              104  STORE_FAST               'g'
              106  STORE_FAST               'b'
            108_0  COME_FROM            80  '80'

 L.2709       108  LOAD_CONST               0
              110  LOAD_FAST                'r'
              112  DUP_TOP          
              114  ROT_THREE        
              116  COMPARE_OP               <=
              118  POP_JUMP_IF_FALSE   128  'to 128'
              120  LOAD_CONST               255
              122  COMPARE_OP               <=
              124  POP_JUMP_IF_FALSE   178  'to 178'
              126  JUMP_FORWARD        132  'to 132'
            128_0  COME_FROM           118  '118'
              128  POP_TOP          
              130  JUMP_FORWARD        178  'to 178'
            132_0  COME_FROM           126  '126'
              132  LOAD_CONST               0
              134  LOAD_FAST                'g'
              136  DUP_TOP          
              138  ROT_THREE        
              140  COMPARE_OP               <=
              142  POP_JUMP_IF_FALSE   152  'to 152'
              144  LOAD_CONST               255
              146  COMPARE_OP               <=
              148  POP_JUMP_IF_FALSE   178  'to 178'
              150  JUMP_FORWARD        156  'to 156'
            152_0  COME_FROM           142  '142'
              152  POP_TOP          
              154  JUMP_FORWARD        178  'to 178'
            156_0  COME_FROM           150  '150'
              156  LOAD_CONST               0
              158  LOAD_FAST                'b'
              160  DUP_TOP          
              162  ROT_THREE        
              164  COMPARE_OP               <=
              166  POP_JUMP_IF_FALSE   176  'to 176'
              168  LOAD_CONST               255
              170  COMPARE_OP               <=
              172  POP_JUMP_IF_TRUE    194  'to 194'
              174  JUMP_FORWARD        178  'to 178'
            176_0  COME_FROM           166  '166'
              176  POP_TOP          
            178_0  COME_FROM           174  '174'
            178_1  COME_FROM           154  '154'
            178_2  COME_FROM           148  '148'
            178_3  COME_FROM           130  '130'
            178_4  COME_FROM           124  '124'

 L.2710       178  LOAD_GLOBAL              TurtleGraphicsError
              180  LOAD_STR                 'bad color sequence: %s'
              182  LOAD_GLOBAL              str
              184  LOAD_FAST                'args'
              186  CALL_FUNCTION_1       1  '1 positional argument'
              188  BINARY_MODULO    
              190  CALL_FUNCTION_1       1  '1 positional argument'
              192  RAISE_VARARGS_1       1  'exception instance'
            194_0  COME_FROM           172  '172'

 L.2711       194  LOAD_STR                 '#%02x%02x%02x'
              196  LOAD_FAST                'r'
              198  LOAD_FAST                'g'
              200  LOAD_FAST                'b'
              202  BUILD_TUPLE_3         3 
              204  BINARY_MODULO    
              206  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 194_0

    def clone(self):
        screen = self.screen
        self._newLine(self._drawing)
        turtle = self.turtle
        self.screen = None
        self.turtle = None
        q = deepcopy(self)
        self.screen = screen
        self.turtle = turtle
        q.screen = screen
        q.turtle = _TurtleImage(screen, self.turtle.shapeIndex)
        screen._turtles.append(q)
        ttype = screen._shapes[self.turtle.shapeIndex]._type
        if ttype == 'polygon':
            q.turtle._item = screen._createpoly()
        else:
            if ttype == 'image':
                q.turtle._item = screen._createimage(screen._shapes['blank']._data)
            else:
                if ttype == 'compound':
                    q.turtle._item = [screen._createpoly() for item in screen._shapes[self.turtle.shapeIndex]._data]
        q.currentLineItem = screen._createline()
        q._update()
        return q

    def shape(self, name=None):
        if name is None:
            return self.turtle.shapeIndex
        if name not in self.screen.getshapes():
            raise TurtleGraphicsError('There is no shape named %s' % name)
        self.turtle._setshape(name)
        self._update()

    def shapesize(self, stretch_wid=None, stretch_len=None, outline=None):
        if stretch_wid is stretch_len is outline is None:
            stretch_wid, stretch_len = self._stretchfactor
            return (stretch_wid, stretch_len, self._outlinewidth)
        elif not stretch_wid == 0:
            if stretch_len == 0:
                raise TurtleGraphicsError('stretch_wid/stretch_len must not be zero')
            if stretch_wid is not None:
                if stretch_len is None:
                    stretchfactor = (
                     stretch_wid, stretch_wid)
                else:
                    stretchfactor = (
                     stretch_wid, stretch_len)
        elif stretch_len is not None:
            stretchfactor = (
             self._stretchfactor[0], stretch_len)
        else:
            stretchfactor = self._stretchfactor
        if outline is None:
            outline = self._outlinewidth
        self.pen(resizemode='user', stretchfactor=stretchfactor,
          outline=outline)

    def shearfactor(self, shear=None):
        if shear is None:
            return self._shearfactor
        self.pen(resizemode='user', shearfactor=shear)

    def settiltangle(self, angle):
        tilt = -angle * self._degreesPerAU * self._angleOrient
        tilt = tilt * math.pi / 180.0 % (2 * math.pi)
        self.pen(resizemode='user', tilt=tilt)

    def tiltangle(self, angle=None):
        if angle is None:
            tilt = -self._tilt * (180.0 / math.pi) * self._angleOrient
            return tilt / self._degreesPerAU % self._fullcircle
        self.settiltangle(angle)

    def tilt(self, angle):
        self.settiltangle(angle + self.tiltangle())

    def shapetransform(self, t11=None, t12=None, t21=None, t22=None):
        if t11 is t12  is t21 is t22 is None:
            return self._shapetrafo
        m11, m12, m21, m22 = self._shapetrafo
        if t11 is not None:
            m11 = t11
        if t12 is not None:
            m12 = t12
        if t21 is not None:
            m21 = t21
        if t22 is not None:
            m22 = t22
        if t11 * t22 - t12 * t21 == 0:
            raise TurtleGraphicsError('Bad shape transform matrix: must not be singular')
        self._shapetrafo = (
         m11, m12, m21, m22)
        alfa = math.atan2(-m21, m11) % (2 * math.pi)
        sa, ca = math.sin(alfa), math.cos(alfa)
        a11, a12, a21, a22 = (ca * m11 - sa * m21, ca * m12 - sa * m22,
         sa * m11 + ca * m21, sa * m12 + ca * m22)
        self._stretchfactor = (a11, a22)
        self._shearfactor = a12 / a22
        self._tilt = alfa
        self.pen(resizemode='user')

    def _polytrafo(self, poly):
        screen = self.screen
        p0, p1 = self._position
        e0, e1 = self._orient
        e = Vec2D(e0, e1 * screen.yscale / screen.xscale)
        e0, e1 = 1.0 / abs(e) * e
        return [(p0 + (e1 * x + e0 * y) / screen.xscale, p1 + (-e0 * x + e1 * y) / screen.yscale) for x, y in poly]

    def get_shapepoly(self):
        shape = self.screen._shapes[self.turtle.shapeIndex]
        if shape._type == 'polygon':
            return self._getshapepoly(shape._data, shape._type == 'compound')

    def _getshapepoly(self, polygon, compound=False):
        if self._resizemode == 'user' or compound:
            t11, t12, t21, t22 = self._shapetrafo
        else:
            if self._resizemode == 'auto':
                l = max(1, self._pensize / 5.0)
                t11, t12, t21, t22 = (l, 0, 0, l)
            else:
                if self._resizemode == 'noresize':
                    return polygon
        return tuple(((t11 * x + t12 * y, t21 * x + t22 * y) for x, y in polygon))

    def _drawturtle(self):
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        titem = self.turtle._item
        if self._shown:
            if screen._updatecounter == 0 and screen._tracing > 0:
                self._hidden_from_screen = False
                tshape = shape._data
                if ttype == 'polygon':
                    if self._resizemode == 'noresize':
                        w = 1
                    else:
                        if self._resizemode == 'auto':
                            w = self._pensize
                        else:
                            w = self._outlinewidth
                    shape = self._polytrafo(self._getshapepoly(tshape))
                    fc, oc = self._fillcolor, self._pencolor
                    screen._drawpoly(titem, shape, fill=fc, outline=oc, width=w,
                      top=True)
            elif ttype == 'image':
                screen._drawimage(titem, self._position, tshape)
            else:
                if ttype == 'compound':
                    for item, (poly, fc, oc) in zip(titem, tshape):
                        poly = self._polytrafo(self._getshapepoly(poly, True))
                        screen._drawpoly(item, poly, fill=(self._cc(fc)), outline=(self._cc(oc)),
                          width=(self._outlinewidth),
                          top=True)

        else:
            if self._hidden_from_screen:
                return
                if ttype == 'polygon':
                    screen._drawpoly(titem, ((0, 0), (0, 0), (0, 0)), '', '')
            elif ttype == 'image':
                screen._drawimage(titem, self._position, screen._shapes['blank']._data)
            else:
                if ttype == 'compound':
                    for item in titem:
                        screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), '', '')

            self._hidden_from_screen = True

    def stamp(self):
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        tshape = shape._data
        if ttype == 'polygon':
            stitem = screen._createpoly()
            if self._resizemode == 'noresize':
                w = 1
            else:
                if self._resizemode == 'auto':
                    w = self._pensize
                else:
                    w = self._outlinewidth
            shape = self._polytrafo(self._getshapepoly(tshape))
            fc, oc = self._fillcolor, self._pencolor
            screen._drawpoly(stitem, shape, fill=fc, outline=oc, width=w,
              top=True)
        else:
            if ttype == 'image':
                stitem = screen._createimage('')
                screen._drawimage(stitem, self._position, tshape)
            else:
                if ttype == 'compound':
                    stitem = []
                    for element in tshape:
                        item = screen._createpoly()
                        stitem.append(item)

                    stitem = tuple(stitem)
                    for item, (poly, fc, oc) in zip(stitem, tshape):
                        poly = self._polytrafo(self._getshapepoly(poly, True))
                        screen._drawpoly(item, poly, fill=(self._cc(fc)), outline=(self._cc(oc)),
                          width=(self._outlinewidth),
                          top=True)

                self.stampItems.append(stitem)
                self.undobuffer.push(('stamp', stitem))
                return stitem

    def _clearstamp(self, stampid):
        if stampid in self.stampItems:
            if isinstance(stampid, tuple):
                for subitem in stampid:
                    self.screen._delete(subitem)

            else:
                self.screen._delete(stampid)
            self.stampItems.remove(stampid)
        item = (
         'stamp', stampid)
        buf = self.undobuffer
        if item not in buf.buffer:
            return
        index = buf.buffer.index(item)
        buf.buffer.remove(item)
        if index <= buf.ptr:
            buf.ptr = (buf.ptr - 1) % buf.bufsize
        buf.buffer.insert((buf.ptr + 1) % buf.bufsize, [None])

    def clearstamp(self, stampid):
        self._clearstamp(stampid)
        self._update()

    def clearstamps(self, n=None):
        if n is None:
            toDelete = self.stampItems[:]
        else:
            if n >= 0:
                toDelete = self.stampItems[:n]
            else:
                toDelete = self.stampItems[n:]
        for item in toDelete:
            self._clearstamp(item)

        self._update()

    def _goto(self, end):
        go_modes = (
         self._drawing,
         self._pencolor,
         self._pensize,
         isinstance(self._fillpath, list))
        screen = self.screen
        undo_entry = ('go', self._position, end, go_modes,
         (
          self.currentLineItem,
          self.currentLine[:],
          screen._pointlist(self.currentLineItem),
          self.items[:]))
        if self.undobuffer:
            self.undobuffer.push(undo_entry)
        start = self._position
        if self._speed:
            if screen._tracing == 1:
                diff = end - start
                diffsq = (diff[0] * screen.xscale) ** 2 + (diff[1] * screen.yscale) ** 2
                nhops = 1 + int(diffsq ** 0.5 / (3 * 1.1 ** self._speed * self._speed))
                delta = diff * (1.0 / nhops)
                for n in range(1, nhops):
                    if n == 1:
                        top = True
                    else:
                        top = False
                    self._position = start + delta * n
                    if self._drawing:
                        screen._drawline(self.drawingLineItem, (
                         start, self._position), self._pencolor, self._pensize, top)
                    self._update()

                if self._drawing:
                    screen._drawline((self.drawingLineItem), ((0, 0), (0, 0)), fill='',
                      width=(self._pensize))
        if self._drawing:
            self.currentLine.append(end)
        if isinstance(self._fillpath, list):
            self._fillpath.append(end)
        self._position = end
        if self._creatingPoly:
            self._poly.append(end)
        if len(self.currentLine) > 42:
            self._newLine()
        self._update()

    def _undogoto(self, entry):
        old, new, go_modes, coodata = entry
        drawing, pc, ps, filling = go_modes
        cLI, cL, pl, items = coodata
        screen = self.screen
        if abs(self._position - new) > 0.5:
            print('undogoto: HALLO-DA-STIMMT-WAS-NICHT!')
        else:
            self.currentLineItem = cLI
            self.currentLine = cL
            if pl == [(0, 0), (0, 0)]:
                usepc = ''
            else:
                usepc = pc
        screen._drawline(cLI, pl, fill=usepc, width=ps)
        todelete = [i for i in self.items if i not in items if screen._type(i) == 'line']
        for i in todelete:
            screen._delete(i)
            self.items.remove(i)

        start = old
        if self._speed:
            if screen._tracing == 1:
                diff = old - new
                diffsq = (diff[0] * screen.xscale) ** 2 + (diff[1] * screen.yscale) ** 2
                nhops = 1 + int(diffsq ** 0.5 / (3 * 1.1 ** self._speed * self._speed))
                delta = diff * (1.0 / nhops)
                for n in range(1, nhops):
                    if n == 1:
                        top = True
                    else:
                        top = False
                    self._position = new + delta * n
                    if drawing:
                        screen._drawline(self.drawingLineItem, (
                         start, self._position), pc, ps, top)
                    self._update()

                if drawing:
                    screen._drawline((self.drawingLineItem), ((0, 0), (0, 0)), fill='',
                      width=ps)
        self._position = old
        if self._creatingPoly:
            if len(self._poly) > 0:
                self._poly.pop()
            if self._poly == []:
                self._creatingPoly = False
                self._poly = None
        if filling:
            if self._fillpath == []:
                self._fillpath = None
                print('Unwahrscheinlich in _undogoto!')
            else:
                if self._fillpath is not None:
                    self._fillpath.pop()
        self._update()

    def _rotate(self, angle):
        if self.undobuffer:
            self.undobuffer.push(('rot', angle, self._degreesPerAU))
        angle *= self._degreesPerAU
        neworient = self._orient.rotate(angle)
        tracing = self.screen._tracing
        if tracing == 1:
            if self._speed > 0:
                anglevel = 3.0 * self._speed
                steps = 1 + int(abs(angle) / anglevel)
                delta = 1.0 * angle / steps
                for _ in range(steps):
                    self._orient = self._orient.rotate(delta)
                    self._update()

        self._orient = neworient
        self._update()

    def _newLine(self, usePos=True):
        if len(self.currentLine) > 1:
            self.screen._drawline(self.currentLineItem, self.currentLine, self._pencolor, self._pensize)
            self.currentLineItem = self.screen._createline()
            self.items.append(self.currentLineItem)
        else:
            self.screen._drawline((self.currentLineItem), top=True)
        self.currentLine = []
        if usePos:
            self.currentLine = [
             self._position]

    def filling(self):
        return isinstance(self._fillpath, list)

    def begin_fill(self):
        if not self.filling():
            self._fillitem = self.screen._createpoly()
            self.items.append(self._fillitem)
        self._fillpath = [
         self._position]
        self._newLine()
        if self.undobuffer:
            self.undobuffer.push(('beginfill', self._fillitem))
        self._update()

    def end_fill(self):
        if self.filling():
            if len(self._fillpath) > 2:
                self.screen._drawpoly((self._fillitem), (self._fillpath), fill=(self._fillcolor))
                if self.undobuffer:
                    self.undobuffer.push(('dofill', self._fillitem))
            self._fillitem = self._fillpath = None
            self._update()

    def dot(self, size=None, *color):
        if not color:
            if isinstance(size, (str, tuple)):
                color = self._colorstr(size)
                size = self._pensize + max(self._pensize, 4)
            else:
                color = self._pencolor
                if not size:
                    size = self._pensize + max(self._pensize, 4)
                else:
                    if size is None:
                        size = self._pensize + max(self._pensize, 4)
                    color = self._colorstr(color)
                if hasattr(self.screen, '_dot'):
                    item = self.screen._dot(self._position, size, color)
                    self.items.append(item)
                    if self.undobuffer:
                        self.undobuffer.push(('dot', item))
        else:
            pen = self.pen()
            if self.undobuffer:
                self.undobuffer.push(['seq'])
                self.undobuffer.cumulate = True
            try:
                if self.resizemode() == 'auto':
                    self.ht()
                self.pendown()
                self.pensize(size)
                self.pencolor(color)
                self.forward(0)
            finally:
                self.pen(pen)

            if self.undobuffer:
                self.undobuffer.cumulate = False

    def _write(self, txt, align, font):
        item, end = self.screen._write(self._position, txt, align, font, self._pencolor)
        self.items.append(item)
        if self.undobuffer:
            self.undobuffer.push(('wri', item))
        return end

    def write(self, arg, move=False, align='left', font=('Arial', 8, 'normal')):
        if self.undobuffer:
            self.undobuffer.push(['seq'])
            self.undobuffer.cumulate = True
        end = self._write(str(arg), align.lower(), font)
        if move:
            x, y = self.pos()
            self.setpos(end, y)
        if self.undobuffer:
            self.undobuffer.cumulate = False

    def begin_poly(self):
        self._poly = [
         self._position]
        self._creatingPoly = True

    def end_poly(self):
        self._creatingPoly = False

    def get_poly(self):
        if self._poly is not None:
            return tuple(self._poly)

    def getscreen(self):
        return self.screen

    def getturtle(self):
        return self

    getpen = getturtle

    def _delay(self, delay=None):
        return self.screen.delay(delay)

    def onclick(self, fun, btn=1, add=None):
        self.screen._onclick(self.turtle._item, fun, btn, add)
        self._update()

    def onrelease(self, fun, btn=1, add=None):
        self.screen._onrelease(self.turtle._item, fun, btn, add)
        self._update()

    def ondrag(self, fun, btn=1, add=None):
        self.screen._ondrag(self.turtle._item, fun, btn, add)

    def _undo(self, action, data):
        if self.undobuffer is None:
            return
            if action == 'rot':
                angle, degPAU = data
                self._rotate(-angle * degPAU / self._degreesPerAU)
                dummy = self.undobuffer.pop()
        elif action == 'stamp':
            stitem = data[0]
            self.clearstamp(stitem)
        else:
            if action == 'go':
                self._undogoto(data)
            else:
                if action in ('wri', 'dot'):
                    item = data[0]
                    self.screen._delete(item)
                    self.items.remove(item)
                else:
                    if action == 'dofill':
                        item = data[0]
                        self.screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), fill='',
                          outline='')
                    else:
                        if action == 'beginfill':
                            item = data[0]
                            self._fillitem = self._fillpath = None
                            if item in self.items:
                                self.screen._delete(item)
                                self.items.remove(item)
                        elif action == 'pen':
                            TPen.pen(self, data[0])
                            self.undobuffer.pop()

    def undo(self):
        if self.undobuffer is None:
            return
            item = self.undobuffer.pop()
            action = item[0]
            data = item[1:]
            if action == 'seq':
                while data:
                    item = data.pop()
                    self._undo(item[0], item[1:])

        else:
            self._undo(action, data)

    turtlesize = shapesize


RawPen = RawTurtle

def Screen():
    if Turtle._screen is None:
        Turtle._screen = _Screen()
    return Turtle._screen


class _Screen(TurtleScreen):
    _root = None
    _canvas = None
    _title = _CFG['title']

    def __init__(self):
        if _Screen._root is None:
            _Screen._root = self._root = _Root()
            self._root.title(_Screen._title)
            self._root.ondestroy(self._destroy)
        if _Screen._canvas is None:
            width = _CFG['width']
            height = _CFG['height']
            canvwidth = _CFG['canvwidth']
            canvheight = _CFG['canvheight']
            leftright = _CFG['leftright']
            topbottom = _CFG['topbottom']
            self._root.setupcanvas(width, height, canvwidth, canvheight)
            _Screen._canvas = self._root._getcanvas()
            TurtleScreen.__init__(self, _Screen._canvas)
            self.setup(width, height, leftright, topbottom)

    def setup(self, width=_CFG['width'], height=_CFG['height'], startx=_CFG['leftright'], starty=_CFG['topbottom']):
        if not hasattr(self._root, 'set_geometry'):
            return
            sw = self._root.win_width()
            sh = self._root.win_height()
            if isinstance(width, float):
                if 0 <= width <= 1:
                    width = sw * width
            if startx is None:
                startx = (sw - width) / 2
        elif isinstance(height, float):
            if 0 <= height <= 1:
                height = sh * height
        if starty is None:
            starty = (sh - height) / 2
        self._root.set_geometry(width, height, startx, starty)
        self.update()

    def title(self, titlestring):
        if _Screen._root is not None:
            _Screen._root.title(titlestring)
        _Screen._title = titlestring

    def _destroy(self):
        root = self._root
        if root is _Screen._root:
            Turtle._pen = None
            Turtle._screen = None
            _Screen._root = None
            _Screen._canvas = None
        TurtleScreen._RUNNING = False
        root.destroy()

    def bye(self):
        self._destroy()

    def exitonclick(self):

        def exitGracefully(x, y):
            self.bye()

        self.onclick(exitGracefully)
        if _CFG['using_IDLE']:
            return
        try:
            mainloop()
        except AttributeError:
            exit(0)


class Turtle(RawTurtle):
    _pen = None
    _screen = None

    def __init__(self, shape=_CFG['shape'], undobuffersize=_CFG['undobuffersize'], visible=_CFG['visible']):
        if Turtle._screen is None:
            Turtle._screen = Screen()
        RawTurtle.__init__(self, (Turtle._screen), shape=shape,
          undobuffersize=undobuffersize,
          visible=visible)


Pen = Turtle

def write_docstringdict(filename='turtle_docstringdict'):
    docsdict = {}
    for methodname in _tg_screen_functions:
        key = '_Screen.' + methodname
        docsdict[key] = eval(key).__doc__

    for methodname in _tg_turtle_functions:
        key = 'Turtle.' + methodname
        docsdict[key] = eval(key).__doc__

    with open('%s.py' % filename, 'w') as (f):
        keys = sorted((x for x in docsdict if x.split('.')[1] not in _alias_list))
        f.write('docsdict = {\n\n')
        for key in keys[:-1]:
            f.write('%s :\n' % repr(key))
            f.write('        """%s\n""",\n\n' % docsdict[key])

        key = keys[-1]
        f.write('%s :\n' % repr(key))
        f.write('        """%s\n"""\n\n' % docsdict[key])
        f.write('}\n')
        f.close()


def read_docstrings(lang):
    modname = 'turtle_docstringdict_%(language)s' % {'language': lang.lower()}
    module = __import__(modname)
    docsdict = module.docsdict
    for key in docsdict:
        try:
            eval(key).__doc__ = docsdict[key]
        except Exception:
            print('Bad docstring-entry: %s' % key)


_LANGUAGE = _CFG['language']
try:
    if _LANGUAGE != 'english':
        read_docstrings(_LANGUAGE)
except ImportError:
    print('Cannot find docsdict for', _LANGUAGE)
except Exception:
    print('Unknown Error when trying to import %s-docstring-dictionary' % _LANGUAGE)

def getmethparlist(ob):
    defText = callText = ''
    args, varargs, varkw = inspect.getargs(ob.__code__)
    items2 = args[1:]
    realArgs = args[1:]
    defaults = ob.__defaults__ or []
    defaults = ['=%r' % (value,) for value in defaults]
    defaults = [''] * (len(realArgs) - len(defaults)) + defaults
    items1 = [arg + dflt for arg, dflt in zip(realArgs, defaults)]
    if varargs is not None:
        items1.append('*' + varargs)
        items2.append('*' + varargs)
    if varkw is not None:
        items1.append('**' + varkw)
        items2.append('**' + varkw)
    defText = ', '.join(items1)
    defText = '(%s)' % defText
    callText = ', '.join(items2)
    callText = '(%s)' % callText
    return (defText, callText)


def _turtle_docrevise(docstr):
    import re
    if docstr is None:
        return
    turtlename = _CFG['exampleturtle']
    newdocstr = docstr.replace('%s.' % turtlename, '')
    parexp = re.compile(' \\(.+ %s\\):' % turtlename)
    newdocstr = parexp.sub(':', newdocstr)
    return newdocstr


def _screen_docrevise(docstr):
    import re
    if docstr is None:
        return
    screenname = _CFG['examplescreen']
    newdocstr = docstr.replace('%s.' % screenname, '')
    parexp = re.compile(' \\(.+ %s\\):' % screenname)
    newdocstr = parexp.sub(':', newdocstr)
    return newdocstr


__func_body = 'def {name}{paramslist}:\n    if {obj} is None:\n        if not TurtleScreen._RUNNING:\n            TurtleScreen._RUNNING = True\n            raise Terminator\n        {obj} = {init}\n    try:\n        return {obj}.{name}{argslist}\n    except TK.TclError:\n        if not TurtleScreen._RUNNING:\n            TurtleScreen._RUNNING = True\n            raise Terminator\n        raise\n'

def _make_global_funcs(functions, cls, obj, init, docrevise):
    for methodname in functions:
        method = getattr(cls, methodname)
        pl1, pl2 = getmethparlist(method)
        if pl1 == '':
            print('>>>>>>', pl1, pl2)
            continue
        defstr = __func_body.format(obj=obj, init=init, name=methodname, paramslist=pl1,
          argslist=pl2)
        exec(defstr, globals())
        globals()[methodname].__doc__ = docrevise(method.__doc__)


_make_global_funcs(_tg_screen_functions, _Screen, 'Turtle._screen', 'Screen()', _screen_docrevise)
_make_global_funcs(_tg_turtle_functions, Turtle, 'Turtle._pen', 'Turtle()', _turtle_docrevise)
done = mainloop
if __name__ == '__main__':

    def switchpen():
        if isdown():
            pu()
        else:
            pd()


    def demo1():
        reset()
        tracer(True)
        up()
        backward(100)
        down()
        width(3)
        for i in range(3):
            if i == 2:
                begin_fill()
            for _ in range(4):
                forward(20)
                left(90)

            if i == 2:
                color('maroon')
                end_fill()
            up()
            forward(30)
            down()

        width(1)
        color('black')
        tracer(False)
        up()
        right(90)
        forward(100)
        right(90)
        forward(100)
        right(180)
        down()
        write('startstart', 1)
        write('start', 1)
        color('red')
        for i in range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)

        tracer(True)
        begin_fill()
        for i in range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)

        end_fill()


    def demo2():
        speed(1)
        st()
        pensize(3)
        setheading(towards(0, 0))
        radius = distance(0, 0) / 2.0
        rt(90)
        for _ in range(18):
            switchpen()
            circle(radius, 10)

        write('wait a moment...')
        while undobufferentries():
            undo()

        reset()
        lt(90)
        colormode(255)
        laenge = 10
        pencolor('green')
        pensize(3)
        lt(180)
        for i in range(-2, 16):
            if i > 0:
                begin_fill()
                fillcolor(255 - 15 * i, 0, 15 * i)
            for _ in range(3):
                fd(laenge)
                lt(120)

            end_fill()
            laenge += 10
            lt(15)
            speed((speed() + 1) % 12)

        lt(120)
        pu()
        fd(70)
        rt(30)
        pd()
        color('red', 'yellow')
        speed(0)
        begin_fill()
        for _ in range(4):
            circle(50, 90)
            rt(90)
            fd(30)
            rt(90)

        end_fill()
        lt(90)
        pu()
        fd(30)
        pd()
        shape('turtle')
        tri = getturtle()
        tri.resizemode('auto')
        turtle = Turtle()
        turtle.resizemode('auto')
        turtle.shape('turtle')
        turtle.reset()
        turtle.left(90)
        turtle.speed(0)
        turtle.up()
        turtle.goto(280, 40)
        turtle.lt(30)
        turtle.down()
        turtle.speed(6)
        turtle.color('blue', 'orange')
        turtle.pensize(2)
        tri.speed(6)
        setheading(towards(turtle))
        count = 1
        while tri.distance(turtle) > 4:
            turtle.fd(3.5)
            turtle.lt(0.6)
            tri.setheading(tri.towards(turtle))
            tri.fd(4)
            if count % 20 == 0:
                turtle.stamp()
                tri.stamp()
                switchpen()
            count += 1

        tri.write('CAUGHT! ', font=('Arial', 16, 'bold'), align='right')
        tri.pencolor('black')
        tri.pencolor('red')

        def baba(xdummy, ydummy):
            clearscreen()
            bye()

        time.sleep(2)
        while undobufferentries():
            tri.undo()
            turtle.undo()

        tri.fd(50)
        tri.write('  Click me!', font=('Courier', 12, 'bold'))
        tri.onclick(baba, 1)


    demo1()
    demo2()
    exitonclick()