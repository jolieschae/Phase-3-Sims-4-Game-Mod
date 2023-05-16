# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\pyclbr.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 15538 bytes
import io, sys, importlib.util, tokenize
from token import NAME, DEDENT, OP
__all__ = [
 'readmodule', 'readmodule_ex', 'Class', 'Function']
_modules = {}

class _Object:

    def __init__(self, module, name, file, lineno, parent):
        self.module = module
        self.name = name
        self.file = file
        self.lineno = lineno
        self.parent = parent
        self.children = {}

    def _addchild(self, name, obj):
        self.children[name] = obj


class Function(_Object):

    def __init__(self, module, name, file, lineno, parent=None):
        _Object.__init__(self, module, name, file, lineno, parent)


class Class(_Object):

    def __init__(self, module, name, super, file, lineno, parent=None):
        _Object.__init__(self, module, name, file, lineno, parent)
        self.super = [] if super is None else super
        self.methods = {}

    def _addmethod(self, name, lineno):
        self.methods[name] = lineno


def _nest_function(ob, func_name, lineno):
    newfunc = Function(ob.module, func_name, ob.file, lineno, ob)
    ob._addchild(func_name, newfunc)
    if isinstance(ob, Class):
        ob._addmethod(func_name, lineno)
    return newfunc


def _nest_class(ob, class_name, lineno, super=None):
    newclass = Class(ob.module, class_name, super, ob.file, lineno, ob)
    ob._addchild(class_name, newclass)
    return newclass


def readmodule(module, path=None):
    res = {}
    for key, value in _readmodule(module, path or []).items():
        if isinstance(value, Class):
            res[key] = value

    return res


def readmodule_ex(module, path=None):
    return _readmodule(module, path or [])


def _readmodule(module, path, inpackage=None):
    if inpackage is not None:
        fullmodule = '%s.%s' % (inpackage, module)
    else:
        fullmodule = module
    if fullmodule in _modules:
        return _modules[fullmodule]
    tree = {}
    if module in sys.builtin_module_names:
        if inpackage is None:
            _modules[module] = tree
            return tree
    else:
        i = module.rfind('.')
        if i >= 0:
            package = module[:i]
            submodule = module[i + 1:]
            parent = _readmodule(package, path, inpackage)
            if inpackage is not None:
                package = '%s.%s' % (inpackage, package)
            if '__path__' not in parent:
                raise ImportError('No package named {}'.format(package))
            return _readmodule(submodule, parent['__path__'], package)
            f = None
            if inpackage is not None:
                search_path = path
        else:
            search_path = path + sys.path
    spec = importlib.util._find_spec_from_path(fullmodule, search_path)
    _modules[fullmodule] = tree
    if spec.submodule_search_locations is not None:
        tree['__path__'] = spec.submodule_search_locations
    try:
        source = spec.loader.get_source(fullmodule)
        if source is None:
            return tree
    except (AttributeError, ImportError):
        return tree
    else:
        fname = spec.loader.get_filename(fullmodule)
        return _create_tree(fullmodule, path, fname, source, tree, inpackage)


def _create_tree(fullmodule, path, fname, source, tree, inpackage):
    f = io.StringIO(source)
    stack = []
    g = tokenize.generate_tokens(f.readline)
    try:
        for tokentype, token, start, _end, _line in g:
            if tokentype == DEDENT:
                lineno, thisindent = start
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]

            elif token == 'def':
                lineno, thisindent = start
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]

                tokentype, func_name, start = next(g)[0:3]
                if tokentype != NAME:
                    continue
                cur_func = None
                if stack:
                    cur_obj = stack[-1][0]
                    cur_func = _nest_function(cur_obj, func_name, lineno)
                else:
                    cur_func = Function(fullmodule, func_name, fname, lineno)
                    tree[func_name] = cur_func
                stack.append((cur_func, thisindent))
            elif token == 'class':
                lineno, thisindent = start
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]

                tokentype, class_name, start = next(g)[0:3]
                if tokentype != NAME:
                    continue
                tokentype, token, start = next(g)[0:3]
                inherit = None
                if token == '(':
                    names = []
                    level = 1
                    super = []
                    while 1:
                        tokentype, token, start = next(g)[0:3]
                        if token in (')', ','):
                            if level == 1:
                                n = ''.join(super)
                                if n in tree:
                                    n = tree[n]
                                else:
                                    c = n.split('.')
                                    if len(c) > 1:
                                        m = c[-2]
                                        c = c[-1]
                                        if m in _modules:
                                            d = _modules[m]
                                            if c in d:
                                                n = d[c]
                                    names.append(n)
                                super = []
                        if token == '(':
                            level += 1
                        elif token == ')':
                            level -= 1
                            if level == 0:
                                break
                        else:
                            if token == ',':
                                if level == 1:
                                    continue
                            if tokentype in (NAME, OP):
                                if level == 1:
                                    super.append(token)

                    inherit = names
                if stack:
                    cur_obj = stack[-1][0]
                    cur_class = _nest_class(cur_obj, class_name, lineno, inherit)
                else:
                    cur_class = Class(fullmodule, class_name, inherit, fname, lineno)
                    tree[class_name] = cur_class
                stack.append((cur_class, thisindent))
            else:
                if token == 'import':
                    if start[1] == 0:
                        modules = _getnamelist(g)
                        for mod, _mod2 in modules:
                            try:
                                if inpackage is None:
                                    _readmodule(mod, path)
                                else:
                                    try:
                                        _readmodule(mod, path, inpackage)
                                    except ImportError:
                                        _readmodule(mod, [])

                            except:
                                pass

            if token == 'from':
                if start[1] == 0:
                    mod, token = _getname(g)
                    if mod:
                        if token != 'import':
                            continue
                names = _getnamelist(g)
                try:
                    d = _readmodule(mod, path, inpackage)
                except:
                    continue

                for n, n2 in names:
                    if n in d:
                        tree[n2 or n] = d[n]

    except StopIteration:
        pass

    f.close()
    return tree


def _getnamelist(g):
    names = []
    while 1:
        name, token = _getname(g)
        if not name:
            break
        elif token == 'as':
            name2, token = _getname(g)
        else:
            name2 = None
        names.append((name, name2))
        while token != ',' and '\n' not in token:
            token = next(g)[1]

        if token != ',':
            break

    return names


def _getname(g):
    parts = []
    tokentype, token = next(g)[0:2]
    if tokentype != NAME:
        if token != '*':
            return (
             None, token)
    parts.append(token)
    while True:
        tokentype, token = next(g)[0:2]
        if token != '.':
            break
        tokentype, token = next(g)[0:2]
        if tokentype != NAME:
            break
        parts.append(token)

    return (
     '.'.join(parts), token)


def _main():
    import os
    try:
        mod = sys.argv[1]
    except:
        mod = __file__

    if os.path.exists(mod):
        path = [
         os.path.dirname(mod)]
        mod = os.path.basename(mod)
        if mod.lower().endswith('.py'):
            mod = mod[:-3]
    else:
        path = []
    tree = readmodule_ex(mod, path)
    lineno_key = lambda a: getattr(a, 'lineno', 0)
    objs = sorted((tree.values()), key=lineno_key, reverse=True)
    indent_level = 2
    while objs:
        obj = objs.pop()
        if isinstance(obj, list):
            continue
        if not hasattr(obj, 'indent'):
            obj.indent = 0
        if isinstance(obj, _Object):
            new_objs = sorted((obj.children.values()), key=lineno_key,
              reverse=True)
            for ob in new_objs:
                ob.indent = obj.indent + indent_level

            objs.extend(new_objs)
        if isinstance(obj, Class):
            print('{}class {} {} {}'.format(' ' * obj.indent, obj.name, obj.super, obj.lineno))
        elif isinstance(obj, Function):
            print('{}def {} {}'.format(' ' * obj.indent, obj.name, obj.lineno))


if __name__ == '__main__':
    _main()