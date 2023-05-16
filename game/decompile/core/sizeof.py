# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sizeof.py
# Compiled at: 2020-10-06 13:11:30
# Size of source mod 2**32: 17781 bytes
import collections, gc, itertools, struct, sys
from types import FunctionType, ModuleType

def recursive_sizeof(roots, skip_atomic=False):
    handler_cache = {}
    pending = collections.deque(((root, root) for root in roots))
    visited = set()
    sizes = {id(root): 0 for root in roots}
    while pending:
        obj, root = pending.popleft()
        if id(obj) in visited:
            continue
        if not skip_atomic or gc.is_tracked(obj):
            sizes[id(root)] += sys.getsizeof(obj)
        visited.add(id(obj))
        for child in enumerate_children(obj, handler_cache, HANDLERS):
            if child is None:
                continue
            pending.append((child, root))

    results = []
    for root in roots:
        results.append((root, sizes[id(root)]))

    return results


def report(labeled_roots, skip_atomic=False):
    labels = []
    roots = []
    for label, root in labeled_roots:
        labels.append(label)
        roots.append(root)

    results = recursive_sizeof(roots, skip_atomic=skip_atomic)
    counter = collections.Counter()
    for label, (root, size) in zip(labels, results):
        counter[label] += size

    return counter


class Node:
    __slots__ = ('sep', 'name', 'obj', 'size', 'sizerec', 'parent', 'child', 'sibling')

    def __init__(self, sep, name, obj, size):
        self.sep = sep
        self.name = name
        self.obj = obj
        self.size = size
        self.sizerec = 0
        self.parent = None
        self.child = None
        self.sibling = None

    def add_child(self, node):
        node.parent = self
        node.sibling = self.child
        self.child = node

    def __str__(self):
        obj = self
        name = ''
        while obj is not None:
            name = '{}{}{}'.format(obj.sep, obj.name, name)
            obj = obj.parent

        return name


def calc_sizerec--- This code section failed: ---

 L. 105         0  LOAD_FAST                'node'
                2  LOAD_CONST               None
                4  BUILD_TUPLE_2         2 
                6  BUILD_LIST_1          1 
                8  STORE_FAST               'pending'

 L. 109        10  SETUP_LOOP          140  'to 140'
             12_0  COME_FROM           116  '116'
             12_1  COME_FROM           106  '106'
               12  LOAD_FAST                'pending'
               14  POP_JUMP_IF_FALSE   138  'to 138'

 L. 110        16  LOAD_FAST                'pending'
               18  LOAD_METHOD              pop
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  UNPACK_SEQUENCE_2     2 
               24  STORE_FAST               'first'
               26  STORE_FAST               'second'

 L. 111        28  LOAD_FAST                'first'
               30  LOAD_CONST               None
               32  COMPARE_OP               is-not
               34  POP_JUMP_IF_FALSE   100  'to 100'

 L. 112        36  LOAD_FAST                'first'
               38  LOAD_ATTR                size
               40  LOAD_FAST                'first'
               42  STORE_ATTR               sizerec

 L. 113        44  LOAD_FAST                'pending'
               46  LOAD_METHOD              append
               48  LOAD_CONST               None
               50  LOAD_FAST                'first'
               52  BUILD_TUPLE_2         2 
               54  CALL_METHOD_1         1  '1 positional argument'
               56  POP_TOP          

 L. 114        58  LOAD_FAST                'first'
               60  LOAD_ATTR                child
               62  STORE_FAST               'child'

 L. 115        64  SETUP_LOOP          136  'to 136'
               66  LOAD_FAST                'child'
               68  LOAD_CONST               None
               70  COMPARE_OP               is-not
               72  POP_JUMP_IF_FALSE    96  'to 96'

 L. 116        74  LOAD_FAST                'pending'
               76  LOAD_METHOD              append
               78  LOAD_FAST                'child'
               80  LOAD_CONST               None
               82  BUILD_TUPLE_2         2 
               84  CALL_METHOD_1         1  '1 positional argument'
               86  POP_TOP          

 L. 117        88  LOAD_FAST                'child'
               90  LOAD_ATTR                sibling
               92  STORE_FAST               'child'
               94  JUMP_BACK            66  'to 66'
             96_0  COME_FROM            72  '72'
               96  POP_BLOCK        
               98  JUMP_BACK            12  'to 12'
            100_0  COME_FROM            34  '34'

 L. 118       100  LOAD_FAST                'second'
              102  LOAD_CONST               None
              104  COMPARE_OP               is-not
              106  POP_JUMP_IF_FALSE    12  'to 12'

 L. 119       108  LOAD_FAST                'second'
              110  LOAD_ATTR                parent
              112  LOAD_CONST               None
              114  COMPARE_OP               is-not
              116  POP_JUMP_IF_FALSE    12  'to 12'

 L. 120       118  LOAD_FAST                'second'
              120  LOAD_ATTR                parent
              122  DUP_TOP          
              124  LOAD_ATTR                sizerec
              126  LOAD_FAST                'second'
              128  LOAD_ATTR                sizerec
              130  INPLACE_ADD      
              132  ROT_TWO          
              134  STORE_ATTR               sizerec
            136_0  COME_FROM_LOOP       64  '64'
              136  JUMP_BACK            12  'to 12'
            138_0  COME_FROM            14  '14'
              138  POP_BLOCK        
            140_0  COME_FROM_LOOP       10  '10'

Parse error at or near `COME_FROM' instruction at offset 138_0


def get_object_tree(labeled_roots, skip_atomic=False, allowed_ids=None, bfs=True, include_cycles=False):
    handler_cache = {}
    root = Node('', 'Root', None, 0)
    visited = {
     id(root)}
    pending = collections.deque([(obj, '', name, root) for name, obj in labeled_roots])
    while pending:
        if bfs:
            obj, sep, name, parent = pending.popleft()
        else:
            obj, sep, name, parent = pending.pop()
        obj_id = id(obj)
        if obj_id in visited:
            continue
        visited.add(obj_id)
        if allowed_ids is not None:
            if obj_id not in allowed_ids:
                continue
        if skip_atomic:
            if not gc.is_tracked(obj):
                continue
        size = sys.getsizeof(obj)
        node = Node(sep, name, obj, size)
        parent.add_child(node)
        try:
            for sep, field, child in enumerate_children(obj, handler_cache, FIELD_HANDLERS):
                if child is None:
                    continue
                if allowed_ids is not None:
                    if id(child) not in allowed_ids:
                        continue
                if id(child) in visited:
                    if include_cycles:
                        child_node = Node(sep, field + '&', child, 0)
                        node.add_child(child_node)
                        continue
                    pending.append((child, sep, field, node))

        except:
            pass

    calc_sizerec(root)
    return root


def _store_string(string_table, s):
    if s in string_table:
        return string_table[s]
    index = len(string_table)
    string_table[s] = index
    return index


def write_object_tree(node, fd):
    pending = [
     node]
    ns = struct.Struct('<4QL1s3L')
    string_table = collections.OrderedDict()
    fd.write(struct.pack('=b', 1))
    node_count = 0
    node_count_offset = fd.tell()
    fd.write(struct.pack('<Q', 0))
    while pending:
        node_count += 1
        node = pending.pop()
        parent_id = id(node.parent.obj) if node.parent is not None else 0
        fd.write(ns.pack(id(node.obj), parent_id, id(type(node.obj)), node.sizerec, node.size, node.sep.encode('utf-8'), sys.getrefcount(node.obj), _store_string(string_table, node.name), _store_string(string_table, short_str((node.obj), strip_object_name=True))))
        child = node.child
        while child is not None:
            pending.append(child)
            child = child.sibling

    string_table_offset = fd.tell()
    fd.seek(node_count_offset)
    fd.write(struct.pack('<Q', node_count))
    fd.seek(string_table_offset)
    fd.write(struct.pack('<Q', len(string_table)))
    for s in string_table:
        try:
            utf8 = s.encode('utf-8', errors='xmlcharrefreplace')
        except:
            utf8 = ('UTF-8 error: ' + repr(s)).encode('utf-8', errors='replace')

        fd.write(struct.pack('<L', len(utf8)))
        fd.write(utf8)


def enumerate_children(obj, handler_cache, handlers):
    t = type(obj)
    if t not in handler_cache:
        for st in t.__mro__:
            handler = handlers.get(st)
            if handler is not None:
                handler_cache[t] = handler
                break
        else:
            handler_cache[t] = None

    handler = handler_cache[t]
    if handler is not None:
        return handler(obj)
    return ()


def object_iter(obj):
    children = []
    for attr in dir(obj):
        try:
            v = getattr(obj, attr, None)
        except:
            continue

        ref = sys.getrefcount(v)
        if not v is None:
            if ref <= 2:
                continue
            children.append(v)

    return children


def module_iter(module):
    name = module.__name__
    members = []
    module_dict = vars(module)
    for value in module_dict.values():
        if isinstance(value, (type, FunctionType)):
            if value.__module__ != name:
                continue
        members.append(value)

    members.append(vars(module))
    return members


child_iter = iter
dict_iter = lambda obj: itertools.chain.from_iterable(obj.items())
HANDLERS = {collections.deque: child_iter, 
 frozenset: child_iter, 
 list: child_iter, 
 set: child_iter, 
 tuple: child_iter, 
 dict: dict_iter, 
 object: object_iter, 
 ModuleType: module_iter}

def _format_function_strings(string_to_update, prefix):
    at_index = string_to_update.find(' at ')
    if at_index > 0:
        return string_to_update[:at_index].replace(prefix, '')
    return string_to_update


def safe_str(obj, strip_object_name=False):
    if strip_object_name:
        try:
            if isinstance(obj, list):
                return 'list'
            if isinstance(obj, dict):
                return 'dict'
            obj_class_name = obj.__class__.__name__
            if 'metaclass' in obj_class_name.lower():
                return obj.__name__
            obj_string = str(obj)
            if 'type' == obj_class_name:
                return obj_string
            prefixes_to_test = [
             '<function ', '<code ', '<bound method ']
            for prefix_to_test in prefixes_to_test:
                if obj_string.startswith(prefix_to_test):
                    obj_string = _format_function_strings(obj_string, prefix_to_test)
                    return obj_string

            if obj_string.startswith('<cell'):
                at_index = obj_string.find(': ')
                if at_index > 0:
                    obj_string = obj_string[at_index:]
                at_index = obj_string.find(' at ')
                if at_index >= 0:
                    obj_string = obj_string[:at_index]
                return obj_string
            return obj_string
        except:
            pass

    try:
        return str(obj)
    except:
        pass

    try:
        return object.__str__(obj)
    except:
        pass

    try:
        t = type(obj)
        return '<{}.{} object at {:#X}>'.format(t.__module__, t.__qualname__, id(obj))
    except:
        pass

    return '<??? object at {:#X}>'.format(id(obj))


def short_str(obj, strip_object_name=False, maxlen=64, tail=17):
    s = safe_str(obj, strip_object_name=strip_object_name)
    if len(s) > maxlen:
        s = '{}...{}'.format(s[0:maxlen - tail - 3], s[len(s) - tail:])
    return s


def list_fields(obj):
    for i, value in enumerate(obj):
        field = sys.intern('[{}]'.format(i))
        yield ('', field, value)


def dict_fields(obj):
    try:
        for key, value in obj.items():
            yield ('.', short_str(key), value)

    except:
        pass

    yield from list_fields(obj)


def module_fields(module):
    name = module.__name__
    members = []
    module_dict = vars(module)
    for name, value in module_dict.items():
        if isinstance(value, (type, FunctionType)):
            if value.__module__ != name:
                continue
        members.append(('.', name, value))

    return members


def object_fields(obj):
    children = []
    children.append(('.', '__type__', type(obj)))
    ids = set()
    ids.add(id(type(obj)))
    ref_ids = set((id(v) for v in gc.get_referents(obj)))
    for attr in dir(obj):
        if attr == '__qualname__':
            continue
        try:
            v = getattr(obj, attr, None)
        except:
            continue

        vid = id(v)
        if vid not in ref_ids:
            continue
        ids.add(vid)
        ref = sys.getrefcount(v)
        if not v is None:
            if ref <= 2:
                continue
            if attr == '__annotations__':
                if ref == 3:
                    if not v:
                        delattr(obj, attr)
                        continue
            children.append(('.', attr, v))

    refs = gc.get_referents(obj)
    for v in refs:
        if id(v) not in ids:
            children.append(('.', '<gcref>', v))

    return children


FIELD_HANDLERS = {collections.deque: list_fields, 
 frozenset: list_fields, 
 list: list_fields, 
 set: list_fields, 
 tuple: list_fields, 
 dict: dict_fields, 
 object: object_fields, 
 ModuleType: module_fields}