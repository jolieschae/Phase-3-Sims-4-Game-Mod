# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\mailbox.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 80800 bytes
import os, time, calendar, socket, errno, copy, warnings, email, email.message, email.generator, io, contextlib
try:
    import fcntl
except ImportError:
    fcntl = None

__all__ = ["'Mailbox'", "'Maildir'", "'mbox'", "'MH'", "'Babyl'", "'MMDF'", 
 "'Message'", 
 "'MaildirMessage'", "'mboxMessage'", "'MHMessage'", 
 "'BabylMessage'", "'MMDFMessage'", 
 "'Error'", "'NoSuchMailboxError'", 
 "'NotEmptyError'", "'ExternalClashError'", 
 "'FormatError'"]
linesep = os.linesep.encode('ascii')

class Mailbox:

    def __init__(self, path, factory=None, create=True):
        self._path = os.path.abspath(os.path.expanduser(path))
        self._factory = factory

    def add(self, message):
        raise NotImplementedError('Method must be implemented by subclass')

    def remove(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def __delitem__(self, key):
        self.remove(key)

    def discard(self, key):
        try:
            self.remove(key)
        except KeyError:
            pass

    def __setitem__(self, key, message):
        raise NotImplementedError('Method must be implemented by subclass')

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key):
        if not self._factory:
            return self.get_message(key)
        with contextlib.closing(self.get_file(key)) as (file):
            return self._factory(file)

    def get_message(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def get_string(self, key):
        return email.message_from_bytes(self.get_bytes(key)).as_string()

    def get_bytes(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def get_file(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def iterkeys(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        for key in self.iterkeys():
            try:
                value = self[key]
            except KeyError:
                continue

            yield value

    def __iter__(self):
        return self.itervalues()

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for key in self.iterkeys():
            try:
                value = self[key]
            except KeyError:
                continue

            yield (
             key, value)

    def items(self):
        return list(self.iteritems())

    def __contains__(self, key):
        raise NotImplementedError('Method must be implemented by subclass')

    def __len__(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def clear(self):
        for key in self.keys():
            self.discard(key)

    def pop(self, key, default=None):
        try:
            result = self[key]
        except KeyError:
            return default
        else:
            self.discard(key)
            return result

    def popitem(self):
        for key in self.iterkeys():
            return (key, self.pop(key))
        else:
            raise KeyError('No messages in mailbox')

    def update(self, arg=None):
        if hasattr(arg, 'iteritems'):
            source = arg.iteritems()
        else:
            if hasattr(arg, 'items'):
                source = arg.items()
            else:
                source = arg
        bad_key = False
        for key, message in source:
            try:
                self[key] = message
            except KeyError:
                bad_key = True

        if bad_key:
            raise KeyError('No message with key(s)')

    def flush(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def lock(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def unlock(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def close(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def _string_to_bytes(self, message):
        try:
            return message.encode('ascii')
        except UnicodeError:
            raise ValueError('String input must be ASCII-only; use bytes or a Message instead')

    _append_newline = False

    def _dump_message(self, message, target, mangle_from_=False):
        if isinstance(message, email.message.Message):
            buffer = io.BytesIO()
            gen = email.generator.BytesGenerator(buffer, mangle_from_, 0)
            gen.flatten(message)
            buffer.seek(0)
            data = buffer.read()
            data = data.replace(b'\n', linesep)
            target.write(data)
            if self._append_newline:
                if not data.endswith(linesep):
                    target.write(linesep)
        else:
            if isinstance(message, (str, bytes, io.StringIO)):
                if isinstance(message, io.StringIO):
                    warnings.warn('Use of StringIO input is deprecated, use BytesIO instead', DeprecationWarning, 3)
                    message = message.getvalue()
                if isinstance(message, str):
                    message = self._string_to_bytes(message)
                if mangle_from_:
                    message = message.replace(b'\nFrom ', b'\n>From ')
                message = message.replace(b'\n', linesep)
                target.write(message)
                if self._append_newline:
                    message.endswith(linesep) or target.write(linesep)
            elif hasattr(message, 'read'):
                if hasattr(message, 'buffer'):
                    warnings.warn('Use of text mode files is deprecated, use a binary mode file instead', DeprecationWarning, 3)
                    message = message.buffer
                lastline = None
                while True:
                    line = message.readline()
                    if line.endswith(b'\r\n'):
                        line = line[:-2] + b'\n'
                    else:
                        if line.endswith(b'\r'):
                            line = line[:-1] + b'\n'
                        else:
                            if not line:
                                break
                            if mangle_from_ and line.startswith(b'From '):
                                line = b'>From ' + line[5:]
                        line = line.replace(b'\n', linesep)
                        target.write(line)
                        lastline = line

                if self._append_newline and lastline:
                    lastline.endswith(linesep) or target.write(linesep)
            else:
                raise TypeError('Invalid message type: %s' % type(message))


class Maildir(Mailbox):
    colon = ':'

    def __init__(self, dirname, factory=None, create=True):
        Mailbox.__init__(self, dirname, factory, create)
        self._paths = {'tmp':os.path.join(self._path, 'tmp'), 
         'new':os.path.join(self._path, 'new'), 
         'cur':os.path.join(self._path, 'cur')}
        if not os.path.exists(self._path):
            if create:
                os.mkdir(self._path, 448)
                for path in self._paths.values():
                    os.mkdir(path, 448)

            else:
                raise NoSuchMailboxError(self._path)
        self._toc = {}
        self._toc_mtimes = {'cur':0, 
         'new':0}
        self._last_read = 0
        self._skewfactor = 0.1

    def add(self, message):
        tmp_file = self._create_tmp()
        try:
            self._dump_message(message, tmp_file)
        except BaseException:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise

        _sync_close(tmp_file)
        if isinstance(message, MaildirMessage):
            subdir = message.get_subdir()
            suffix = self.colon + message.get_info()
            if suffix == self.colon:
                suffix = ''
        else:
            subdir = 'new'
            suffix = ''
        uniq = os.path.basename(tmp_file.name).split(self.colon)[0]
        dest = os.path.join(self._path, subdir, uniq + suffix)
        if isinstance(message, MaildirMessage):
            os.utime(tmp_file.name, (
             os.path.getatime(tmp_file.name), message.get_date()))
        try:
            try:
                os.link(tmp_file.name, dest)
            except (AttributeError, PermissionError):
                os.rename(tmp_file.name, dest)
            else:
                os.remove(tmp_file.name)
        except OSError as e:
            try:
                os.remove(tmp_file.name)
                if e.errno == errno.EEXIST:
                    raise ExternalClashError('Name clash with existing message: %s' % dest)
                else:
                    raise
            finally:
                e = None
                del e

        return uniq

    def remove(self, key):
        os.remove(os.path.join(self._path, self._lookup(key)))

    def discard(self, key):
        try:
            self.remove(key)
        except (KeyError, FileNotFoundError):
            pass

    def __setitem__(self, key, message):
        old_subpath = self._lookup(key)
        temp_key = self.add(message)
        temp_subpath = self._lookup(temp_key)
        if isinstance(message, MaildirMessage):
            dominant_subpath = temp_subpath
        else:
            dominant_subpath = old_subpath
        subdir = os.path.dirname(dominant_subpath)
        if self.colon in dominant_subpath:
            suffix = self.colon + dominant_subpath.split(self.colon)[-1]
        else:
            suffix = ''
        self.discard(key)
        tmp_path = os.path.join(self._path, temp_subpath)
        new_path = os.path.join(self._path, subdir, key + suffix)
        if isinstance(message, MaildirMessage):
            os.utime(tmp_path, (
             os.path.getatime(tmp_path), message.get_date()))
        os.rename(tmp_path, new_path)

    def get_message(self, key):
        subpath = self._lookup(key)
        with open(os.path.join(self._path, subpath), 'rb') as (f):
            if self._factory:
                msg = self._factory(f)
            else:
                msg = MaildirMessage(f)
        subdir, name = os.path.split(subpath)
        msg.set_subdir(subdir)
        if self.colon in name:
            msg.set_info(name.split(self.colon)[-1])
        msg.set_date(os.path.getmtime(os.path.join(self._path, subpath)))
        return msg

    def get_bytes(self, key):
        with open(os.path.join(self._path, self._lookup(key)), 'rb') as (f):
            return f.read().replace(linesep, b'\n')

    def get_file(self, key):
        f = open(os.path.join(self._path, self._lookup(key)), 'rb')
        return _ProxyFile(f)

    def iterkeys(self):
        self._refresh()
        for key in self._toc:
            try:
                self._lookup(key)
            except KeyError:
                continue

            yield key

    def __contains__(self, key):
        self._refresh()
        return key in self._toc

    def __len__(self):
        self._refresh()
        return len(self._toc)

    def flush(self):
        pass

    def lock(self):
        pass

    def unlock(self):
        pass

    def close(self):
        pass

    def list_folders(self):
        result = []
        for entry in os.listdir(self._path):
            if len(entry) > 1 and entry[0] == '.' and os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry[1:])

        return result

    def get_folder(self, folder):
        return Maildir((os.path.join(self._path, '.' + folder)), factory=(self._factory),
          create=False)

    def add_folder(self, folder):
        path = os.path.join(self._path, '.' + folder)
        result = Maildir(path, factory=(self._factory))
        maildirfolder_path = os.path.join(path, 'maildirfolder')
        if not os.path.exists(maildirfolder_path):
            os.close(os.open(maildirfolder_path, os.O_CREAT | os.O_WRONLY, 438))
        return result

    def remove_folder(self, folder):
        path = os.path.join(self._path, '.' + folder)
        for entry in os.listdir(os.path.join(path, 'new')) + os.listdir(os.path.join(path, 'cur')):
            if len(entry) < 1 or entry[0] != '.':
                raise NotEmptyError('Folder contains message(s): %s' % folder)

        for entry in os.listdir(path):
            if entry != 'new' and entry != 'cur' and entry != 'tmp' and os.path.isdir(os.path.join(path, entry)):
                raise NotEmptyError("Folder contains subdirectory '%s': %s" % (
                 folder, entry))

        for root, dirs, files in os.walk(path, topdown=False):
            for entry in files:
                os.remove(os.path.join(root, entry))

            for entry in dirs:
                os.rmdir(os.path.join(root, entry))

        os.rmdir(path)

    def clean(self):
        now = time.time()
        for entry in os.listdir(os.path.join(self._path, 'tmp')):
            path = os.path.join(self._path, 'tmp', entry)
            if now - os.path.getatime(path) > 129600:
                os.remove(path)

    _count = 1

    def _create_tmp(self):
        now = time.time()
        hostname = socket.gethostname()
        if '/' in hostname:
            hostname = hostname.replace('/', '\\057')
        if ':' in hostname:
            hostname = hostname.replace(':', '\\072')
        uniq = '%s.M%sP%sQ%s.%s' % (int(now), int(now % 1 * 1000000.0), os.getpid(),
         Maildir._count, hostname)
        path = os.path.join(self._path, 'tmp', uniq)
        try:
            os.stat(path)
        except FileNotFoundError:
            Maildir._count += 1
            try:
                return _create_carefully(path)
            except FileExistsError:
                pass

        raise ExternalClashError('Name clash prevented file creation: %s' % path)

    def _refresh(self):
        if time.time() - self._last_read > 2 + self._skewfactor:
            refresh = False
            for subdir in self._toc_mtimes:
                mtime = os.path.getmtime(self._paths[subdir])
                if mtime > self._toc_mtimes[subdir]:
                    refresh = True
                self._toc_mtimes[subdir] = mtime

            if not refresh:
                return
        self._toc = {}
        for subdir in self._toc_mtimes:
            path = self._paths[subdir]
            for entry in os.listdir(path):
                p = os.path.join(path, entry)
                if os.path.isdir(p):
                    continue
                uniq = entry.split(self.colon)[0]
                self._toc[uniq] = os.path.join(subdir, entry)

        self._last_read = time.time()

    def _lookup(self, key):
        try:
            if os.path.exists(os.path.join(self._path, self._toc[key])):
                return self._toc[key]
        except KeyError:
            pass

        self._refresh()
        try:
            return self._toc[key]
        except KeyError:
            raise KeyError('No message with key: %s' % key) from None

    def next(self):
        if not hasattr(self, '_onetime_keys'):
            self._onetime_keys = self.iterkeys()
        while True:
            try:
                return self[next(self._onetime_keys)]
            except StopIteration:
                return
            except KeyError:
                continue


class _singlefileMailbox(Mailbox):

    def __init__(self, path, factory=None, create=True):
        Mailbox.__init__(self, path, factory, create)
        try:
            f = open(self._path, 'rb+')
        except OSError as e:
            try:
                if e.errno == errno.ENOENT:
                    if create:
                        f = open(self._path, 'wb+')
                    else:
                        raise NoSuchMailboxError(self._path)
                elif e.errno in (errno.EACCES, errno.EROFS):
                    f = open(self._path, 'rb')
                else:
                    raise
            finally:
                e = None
                del e

        self._file = f
        self._toc = None
        self._next_key = 0
        self._pending = False
        self._pending_sync = False
        self._locked = False
        self._file_length = None

    def add(self, message):
        self._lookup()
        self._toc[self._next_key] = self._append_message(message)
        self._next_key += 1
        self._pending_sync = True
        return self._next_key - 1

    def remove(self, key):
        self._lookup(key)
        del self._toc[key]
        self._pending = True

    def __setitem__(self, key, message):
        self._lookup(key)
        self._toc[key] = self._append_message(message)
        self._pending = True

    def iterkeys(self):
        self._lookup()
        yield from self._toc.keys()
        if False:
            yield None

    def __contains__(self, key):
        self._lookup()
        return key in self._toc

    def __len__(self):
        self._lookup()
        return len(self._toc)

    def lock(self):
        if not self._locked:
            _lock_file(self._file)
            self._locked = True

    def unlock(self):
        if self._locked:
            _unlock_file(self._file)
            self._locked = False

    def flush(self):
        if not self._pending:
            if self._pending_sync:
                _sync_flush(self._file)
                self._pending_sync = False
            return
            self._file.seek(0, 2)
            cur_len = self._file.tell()
            if cur_len != self._file_length:
                raise ExternalClashError('Size of mailbox file changed (expected %i, found %i)' % (
                 self._file_length, cur_len))
        else:
            new_file = _create_temporary(self._path)
            try:
                new_toc = {}
                self._pre_mailbox_hook(new_file)
                for key in sorted(self._toc.keys()):
                    start, stop = self._toc[key]
                    self._file.seek(start)
                    self._pre_message_hook(new_file)
                    new_start = new_file.tell()
                    while True:
                        buffer = self._file.read(min(4096, stop - self._file.tell()))
                        if not buffer:
                            break
                        new_file.write(buffer)

                    new_toc[key] = (
                     new_start, new_file.tell())
                    self._post_message_hook(new_file)

                self._file_length = new_file.tell()
            except:
                new_file.close()
                os.remove(new_file.name)
                raise

        _sync_close(new_file)
        self._file.close()
        mode = os.stat(self._path).st_mode
        os.chmod(new_file.name, mode)
        try:
            os.rename(new_file.name, self._path)
        except FileExistsError:
            os.remove(self._path)
            os.rename(new_file.name, self._path)

        self._file = open(self._path, 'rb+')
        self._toc = new_toc
        self._pending = False
        self._pending_sync = False
        if self._locked:
            _lock_file((self._file), dotlock=False)

    def _pre_mailbox_hook(self, f):
        pass

    def _pre_message_hook(self, f):
        pass

    def _post_message_hook(self, f):
        pass

    def close(self):
        try:
            self.flush()
        finally:
            try:
                if self._locked:
                    self.unlock()
            finally:
                self._file.close()

    def _lookup(self, key=None):
        if self._toc is None:
            self._generate_toc()
        if key is not None:
            try:
                return self._toc[key]
            except KeyError:
                raise KeyError('No message with key: %s' % key) from None

    def _append_message(self, message):
        self._file.seek(0, 2)
        before = self._file.tell()
        if len(self._toc) == 0:
            if not self._pending:
                self._pre_mailbox_hook(self._file)
        try:
            self._pre_message_hook(self._file)
            offsets = self._install_message(message)
            self._post_message_hook(self._file)
        except BaseException:
            self._file.truncate(before)
            raise

        self._file.flush()
        self._file_length = self._file.tell()
        return offsets


class _mboxMMDF(_singlefileMailbox):
    _mangle_from_ = True

    def get_message(self, key):
        start, stop = self._lookup(key)
        self._file.seek(start)
        from_line = self._file.readline().replace(linesep, b'')
        string = self._file.read(stop - self._file.tell())
        msg = self._message_factory(string.replace(linesep, b'\n'))
        msg.set_from(from_line[5:].decode('ascii'))
        return msg

    def get_string(self, key, from_=False):
        return email.message_from_bytes(self.get_bytes(key)).as_string(unixfrom=from_)

    def get_bytes(self, key, from_=False):
        start, stop = self._lookup(key)
        self._file.seek(start)
        if not from_:
            self._file.readline()
        string = self._file.read(stop - self._file.tell())
        return string.replace(linesep, b'\n')

    def get_file(self, key, from_=False):
        start, stop = self._lookup(key)
        self._file.seek(start)
        if not from_:
            self._file.readline()
        return _PartialFile(self._file, self._file.tell(), stop)

    def _install_message(self, message):
        from_line = None
        if isinstance(message, str):
            message = self._string_to_bytes(message)
        if isinstance(message, bytes):
            if message.startswith(b'From '):
                newline = message.find(b'\n')
                if newline != -1:
                    from_line = message[:newline]
                    message = message[newline + 1:]
            else:
                from_line = message
                message = b''
        elif isinstance(message, _mboxMMDFMessage):
            author = message.get_from().encode('ascii')
            from_line = b'From ' + author
        else:
            if isinstance(message, email.message.Message):
                from_line = message.get_unixfrom()
                if from_line is not None:
                    from_line = from_line.encode('ascii')
        if from_line is None:
            from_line = b'From MAILER-DAEMON ' + time.asctime(time.gmtime()).encode()
        start = self._file.tell()
        self._file.write(from_line + linesep)
        self._dump_message(message, self._file, self._mangle_from_)
        stop = self._file.tell()
        return (start, stop)


class mbox(_mboxMMDF):
    _mangle_from_ = True
    _append_newline = True

    def __init__(self, path, factory=None, create=True):
        self._message_factory = mboxMessage
        _mboxMMDF.__init__(self, path, factory, create)

    def _post_message_hook(self, f):
        f.write(linesep)

    def _generate_toc(self):
        starts, stops = [], []
        last_was_empty = False
        self._file.seek(0)
        while True:
            line_pos = self._file.tell()
            line = self._file.readline()
            if line.startswith(b'From '):
                if len(stops) < len(starts):
                    if last_was_empty:
                        stops.append(line_pos - len(linesep))
                    else:
                        stops.append(line_pos)
                starts.append(line_pos)
                last_was_empty = False
            elif not line:
                if last_was_empty:
                    stops.append(line_pos - len(linesep))
                else:
                    stops.append(line_pos)
                break
            elif line == linesep:
                last_was_empty = True
            else:
                last_was_empty = False

        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()


class MMDF(_mboxMMDF):

    def __init__(self, path, factory=None, create=True):
        self._message_factory = MMDFMessage
        _mboxMMDF.__init__(self, path, factory, create)

    def _pre_message_hook(self, f):
        f.write(b'\x01\x01\x01\x01' + linesep)

    def _post_message_hook(self, f):
        f.write(linesep + b'\x01\x01\x01\x01' + linesep)

    def _generate_toc--- This code section failed: ---

 L. 905         0  BUILD_LIST_0          0 
                2  BUILD_LIST_0          0 
                4  ROT_TWO          
                6  STORE_FAST               'starts'
                8  STORE_FAST               'stops'

 L. 906        10  LOAD_FAST                'self'
               12  LOAD_ATTR                _file
               14  LOAD_METHOD              seek
               16  LOAD_CONST               0
               18  CALL_METHOD_1         1  '1 positional argument'
               20  POP_TOP          

 L. 907        22  LOAD_CONST               0
               24  STORE_FAST               'next_pos'

 L. 908        26  SETUP_LOOP          168  'to 168'
             28_0  COME_FROM           160  '160'

 L. 909        28  LOAD_FAST                'next_pos'
               30  STORE_FAST               'line_pos'

 L. 910        32  LOAD_FAST                'self'
               34  LOAD_ATTR                _file
               36  LOAD_METHOD              readline
               38  CALL_METHOD_0         0  '0 positional arguments'
               40  STORE_FAST               'line'

 L. 911        42  LOAD_FAST                'self'
               44  LOAD_ATTR                _file
               46  LOAD_METHOD              tell
               48  CALL_METHOD_0         0  '0 positional arguments'
               50  STORE_FAST               'next_pos'

 L. 912        52  LOAD_FAST                'line'
               54  LOAD_METHOD              startswith
               56  LOAD_CONST               b'\x01\x01\x01\x01'
               58  LOAD_GLOBAL              linesep
               60  BINARY_ADD       
               62  CALL_METHOD_1         1  '1 positional argument'
               64  POP_JUMP_IF_FALSE   158  'to 158'

 L. 913        66  LOAD_FAST                'starts'
               68  LOAD_METHOD              append
               70  LOAD_FAST                'next_pos'
               72  CALL_METHOD_1         1  '1 positional argument'
               74  POP_TOP          

 L. 914        76  SETUP_LOOP          164  'to 164'
             78_0  COME_FROM           138  '138'

 L. 915        78  LOAD_FAST                'next_pos'
               80  STORE_FAST               'line_pos'

 L. 916        82  LOAD_FAST                'self'
               84  LOAD_ATTR                _file
               86  LOAD_METHOD              readline
               88  CALL_METHOD_0         0  '0 positional arguments'
               90  STORE_FAST               'line'

 L. 917        92  LOAD_FAST                'self'
               94  LOAD_ATTR                _file
               96  LOAD_METHOD              tell
               98  CALL_METHOD_0         0  '0 positional arguments'
              100  STORE_FAST               'next_pos'

 L. 918       102  LOAD_FAST                'line'
              104  LOAD_CONST               b'\x01\x01\x01\x01'
              106  LOAD_GLOBAL              linesep
              108  BINARY_ADD       
              110  COMPARE_OP               ==
              112  POP_JUMP_IF_FALSE   136  'to 136'

 L. 919       114  LOAD_FAST                'stops'
              116  LOAD_METHOD              append
              118  LOAD_FAST                'line_pos'
              120  LOAD_GLOBAL              len
              122  LOAD_GLOBAL              linesep
              124  CALL_FUNCTION_1       1  '1 positional argument'
              126  BINARY_SUBTRACT  
              128  CALL_METHOD_1         1  '1 positional argument'
              130  POP_TOP          

 L. 920       132  BREAK_LOOP       
              134  JUMP_BACK            78  'to 78'
            136_0  COME_FROM           112  '112'

 L. 921       136  LOAD_FAST                'line'
              138  POP_JUMP_IF_TRUE     78  'to 78'

 L. 922       140  LOAD_FAST                'stops'
              142  LOAD_METHOD              append
              144  LOAD_FAST                'line_pos'
              146  CALL_METHOD_1         1  '1 positional argument'
              148  POP_TOP          

 L. 923       150  BREAK_LOOP       
              152  JUMP_BACK            78  'to 78'
              154  POP_BLOCK        
              156  JUMP_BACK            28  'to 28'
            158_0  COME_FROM            64  '64'

 L. 924       158  LOAD_FAST                'line'
              160  POP_JUMP_IF_TRUE     28  'to 28'

 L. 925       162  BREAK_LOOP       
            164_0  COME_FROM_LOOP       76  '76'
              164  JUMP_BACK            28  'to 28'
              166  POP_BLOCK        
            168_0  COME_FROM_LOOP       26  '26'

 L. 926       168  LOAD_GLOBAL              dict
              170  LOAD_GLOBAL              enumerate
              172  LOAD_GLOBAL              zip
              174  LOAD_FAST                'starts'
              176  LOAD_FAST                'stops'
              178  CALL_FUNCTION_2       2  '2 positional arguments'
              180  CALL_FUNCTION_1       1  '1 positional argument'
              182  CALL_FUNCTION_1       1  '1 positional argument'
              184  LOAD_FAST                'self'
              186  STORE_ATTR               _toc

 L. 927       188  LOAD_GLOBAL              len
              190  LOAD_FAST                'self'
              192  LOAD_ATTR                _toc
              194  CALL_FUNCTION_1       1  '1 positional argument'
              196  LOAD_FAST                'self'
              198  STORE_ATTR               _next_key

 L. 928       200  LOAD_FAST                'self'
              202  LOAD_ATTR                _file
              204  LOAD_METHOD              seek
              206  LOAD_CONST               0
              208  LOAD_CONST               2
              210  CALL_METHOD_2         2  '2 positional arguments'
              212  POP_TOP          

 L. 929       214  LOAD_FAST                'self'
              216  LOAD_ATTR                _file
              218  LOAD_METHOD              tell
              220  CALL_METHOD_0         0  '0 positional arguments'
              222  LOAD_FAST                'self'
              224  STORE_ATTR               _file_length

Parse error at or near `COME_FROM_LOOP' instruction at offset 164_0


class MH(Mailbox):

    def __init__(self, path, factory=None, create=True):
        Mailbox.__init__(self, path, factory, create)
        if not os.path.exists(self._path):
            if create:
                os.mkdir(self._path, 448)
                os.close(os.open(os.path.join(self._path, '.mh_sequences'), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 384))
            else:
                raise NoSuchMailboxError(self._path)
        self._locked = False

    def add(self, message):
        keys = self.keys()
        if len(keys) == 0:
            new_key = 1
        else:
            new_key = max(keys) + 1
        new_path = os.path.join(self._path, str(new_key))
        f = _create_carefully(new_path)
        closed = False
        try:
            if self._locked:
                _lock_file(f)
            try:
                try:
                    self._dump_message(message, f)
                except BaseException:
                    if self._locked:
                        _unlock_file(f)
                    _sync_close(f)
                    closed = True
                    os.remove(new_path)
                    raise

                if isinstance(message, MHMessage):
                    self._dump_sequences(message, new_key)
            finally:
                if self._locked:
                    _unlock_file(f)

        finally:
            if not closed:
                _sync_close(f)

        return new_key

    def remove(self, key):
        path = os.path.join(self._path, str(key))
        try:
            f = open(path, 'rb+')
        except OSError as e:
            try:
                if e.errno == errno.ENOENT:
                    raise KeyError('No message with key: %s' % key)
                else:
                    raise
            finally:
                e = None
                del e

        else:
            f.close()
            os.remove(path)

    def __setitem__(self, key, message):
        path = os.path.join(self._path, str(key))
        try:
            f = open(path, 'rb+')
        except OSError as e:
            try:
                if e.errno == errno.ENOENT:
                    raise KeyError('No message with key: %s' % key)
                else:
                    raise
            finally:
                e = None
                del e

        try:
            if self._locked:
                _lock_file(f)
            try:
                os.close(os.open(path, os.O_WRONLY | os.O_TRUNC))
                self._dump_message(message, f)
                if isinstance(message, MHMessage):
                    self._dump_sequences(message, key)
            finally:
                if self._locked:
                    _unlock_file(f)

        finally:
            _sync_close(f)

    def get_message(self, key):
        try:
            if self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            else:
                f = open(os.path.join(self._path, str(key)), 'rb')
        except OSError as e:
            try:
                if e.errno == errno.ENOENT:
                    raise KeyError('No message with key: %s' % key)
                else:
                    raise
            finally:
                e = None
                del e

        with f:
            if self._locked:
                _lock_file(f)
            try:
                msg = MHMessage(f)
            finally:
                if self._locked:
                    _unlock_file(f)

        for name, key_list in self.get_sequences().items():
            if key in key_list:
                msg.add_sequence(name)

        return msg

    def get_bytes(self, key):
        try:
            if self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            else:
                f = open(os.path.join(self._path, str(key)), 'rb')
        except OSError as e:
            try:
                if e.errno == errno.ENOENT:
                    raise KeyError('No message with key: %s' % key)
                else:
                    raise
            finally:
                e = None
                del e

        with f:
            if self._locked:
                _lock_file(f)
            try:
                return f.read().replace(linesep, b'\n')
            finally:
                if self._locked:
                    _unlock_file(f)

    def get_file(self, key):
        try:
            f = open(os.path.join(self._path, str(key)), 'rb')
        except OSError as e:
            try:
                if e.errno == errno.ENOENT:
                    raise KeyError('No message with key: %s' % key)
                else:
                    raise
            finally:
                e = None
                del e

        return _ProxyFile(f)

    def iterkeys(self):
        return iter(sorted((int(entry) for entry in os.listdir(self._path) if entry.isdigit())))

    def __contains__(self, key):
        return os.path.exists(os.path.join(self._path, str(key)))

    def __len__(self):
        return len(list(self.iterkeys()))

    def lock(self):
        if not self._locked:
            self._file = open(os.path.join(self._path, '.mh_sequences'), 'rb+')
            _lock_file(self._file)
            self._locked = True

    def unlock(self):
        if self._locked:
            _unlock_file(self._file)
            _sync_close(self._file)
            del self._file
            self._locked = False

    def flush(self):
        pass

    def close(self):
        if self._locked:
            self.unlock()

    def list_folders(self):
        result = []
        for entry in os.listdir(self._path):
            if os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry)

        return result

    def get_folder(self, folder):
        return MH((os.path.join(self._path, folder)), factory=(self._factory),
          create=False)

    def add_folder(self, folder):
        return MH((os.path.join(self._path, folder)), factory=(self._factory))

    def remove_folder(self, folder):
        path = os.path.join(self._path, folder)
        entries = os.listdir(path)
        if entries == ['.mh_sequences']:
            os.remove(os.path.join(path, '.mh_sequences'))
        else:
            if entries == []:
                pass
            else:
                raise NotEmptyError('Folder not empty: %s' % self._path)
            os.rmdir(path)

    def get_sequences(self):
        results = {}
        with open((os.path.join(self._path, '.mh_sequences')), 'r', encoding='ASCII') as (f):
            all_keys = set(self.keys())
            for line in f:
                try:
                    name, contents = line.split(':')
                    keys = set()
                    for spec in contents.split():
                        if spec.isdigit():
                            keys.add(int(spec))
                        else:
                            start, stop = (int(x) for x in spec.split('-'))
                            keys.update(range(start, stop + 1))

                    results[name] = [key for key in sorted(keys) if key in all_keys]
                    if len(results[name]) == 0:
                        del results[name]
                except ValueError:
                    raise FormatError('Invalid sequence specification: %s' % line.rstrip())

        return results

    def set_sequences(self, sequences):
        f = open((os.path.join(self._path, '.mh_sequences')), 'r+', encoding='ASCII')
        try:
            os.close(os.open(f.name, os.O_WRONLY | os.O_TRUNC))
            for name, keys in sequences.items():
                if len(keys) == 0:
                    continue
                f.write(name + ':')
                prev = None
                completing = False
                for key in sorted(set(keys)):
                    if key - 1 == prev:
                        completing = completing or True
                        f.write('-')
                    else:
                        if completing:
                            completing = False
                            f.write('%s %s' % (prev, key))
                        else:
                            f.write(' %s' % key)
                    prev = key

                if completing:
                    f.write(str(prev) + '\n')
                else:
                    f.write('\n')

        finally:
            _sync_close(f)

    def pack(self):
        sequences = self.get_sequences()
        prev = 0
        changes = []
        for key in self.iterkeys():
            if key - 1 != prev:
                changes.append((key, prev + 1))
                try:
                    os.link(os.path.join(self._path, str(key)), os.path.join(self._path, str(prev + 1)))
                except (AttributeError, PermissionError):
                    os.rename(os.path.join(self._path, str(key)), os.path.join(self._path, str(prev + 1)))
                else:
                    os.unlink(os.path.join(self._path, str(key)))
            prev += 1

        self._next_key = prev + 1
        if len(changes) == 0:
            return
        for name, key_list in sequences.items():
            for old, new in changes:
                if old in key_list:
                    key_list[key_list.index(old)] = new

        self.set_sequences(sequences)

    def _dump_sequences(self, message, key):
        pending_sequences = message.get_sequences()
        all_sequences = self.get_sequences()
        for name, key_list in all_sequences.items():
            if name in pending_sequences:
                key_list.append(key)

        for sequence in pending_sequences:
            if sequence not in all_sequences:
                all_sequences[sequence] = [
                 key]

        self.set_sequences(all_sequences)


class Babyl(_singlefileMailbox):
    _special_labels = frozenset({"'unseen'", "'deleted'", "'filed'", "'answered'", 
     "'forwarded'", 
     "'edited'", "'resent'"})

    def __init__(self, path, factory=None, create=True):
        _singlefileMailbox.__init__(self, path, factory, create)
        self._labels = {}

    def add(self, message):
        key = _singlefileMailbox.add(self, message)
        if isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()
        return key

    def remove(self, key):
        _singlefileMailbox.remove(self, key)
        if key in self._labels:
            del self._labels[key]

    def __setitem__(self, key, message):
        _singlefileMailbox.__setitem__(self, key, message)
        if isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()

    def get_message(self, key):
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()
        original_headers = io.BytesIO()
        while 1:
            line = self._file.readline()
            if not line == b'*** EOOH ***' + linesep:
                if not line:
                    break
                original_headers.write(line.replace(linesep, b'\n'))

        visible_headers = io.BytesIO()
        while 1:
            line = self._file.readline()
            if not line == linesep:
                if not line:
                    break
                visible_headers.write(line.replace(linesep, b'\n'))

        n = stop - self._file.tell()
        body = self._file.read(n)
        body = body.replace(linesep, b'\n')
        msg = BabylMessage(original_headers.getvalue() + body)
        msg.set_visible(visible_headers.getvalue())
        if key in self._labels:
            msg.set_labels(self._labels[key])
        return msg

    def get_bytes--- This code section failed: ---

 L.1297         0  LOAD_FAST                'self'
                2  LOAD_METHOD              _lookup
                4  LOAD_FAST                'key'
                6  CALL_METHOD_1         1  '1 positional argument'
                8  UNPACK_SEQUENCE_2     2 
               10  STORE_FAST               'start'
               12  STORE_FAST               'stop'

 L.1298        14  LOAD_FAST                'self'
               16  LOAD_ATTR                _file
               18  LOAD_METHOD              seek
               20  LOAD_FAST                'start'
               22  CALL_METHOD_1         1  '1 positional argument'
               24  POP_TOP          

 L.1299        26  LOAD_FAST                'self'
               28  LOAD_ATTR                _file
               30  LOAD_METHOD              readline
               32  CALL_METHOD_0         0  '0 positional arguments'
               34  POP_TOP          

 L.1300        36  LOAD_GLOBAL              io
               38  LOAD_METHOD              BytesIO
               40  CALL_METHOD_0         0  '0 positional arguments'
               42  STORE_FAST               'original_headers'

 L.1301        44  SETUP_LOOP           96  'to 96'

 L.1302        46  LOAD_FAST                'self'
               48  LOAD_ATTR                _file
               50  LOAD_METHOD              readline
               52  CALL_METHOD_0         0  '0 positional arguments'
               54  STORE_FAST               'line'

 L.1303        56  LOAD_FAST                'line'
               58  LOAD_CONST               b'*** EOOH ***'
               60  LOAD_GLOBAL              linesep
               62  BINARY_ADD       
               64  COMPARE_OP               ==
               66  POP_JUMP_IF_TRUE     72  'to 72'
               68  LOAD_FAST                'line'
               70  POP_JUMP_IF_TRUE     74  'to 74'
             72_0  COME_FROM            66  '66'

 L.1304        72  BREAK_LOOP       
             74_0  COME_FROM            70  '70'

 L.1305        74  LOAD_FAST                'original_headers'
               76  LOAD_METHOD              write
               78  LOAD_FAST                'line'
               80  LOAD_METHOD              replace
               82  LOAD_GLOBAL              linesep
               84  LOAD_CONST               b'\n'
               86  CALL_METHOD_2         2  '2 positional arguments'
               88  CALL_METHOD_1         1  '1 positional argument'
               90  POP_TOP          
               92  JUMP_BACK            46  'to 46'
               94  POP_BLOCK        
             96_0  COME_FROM_LOOP       44  '44'

 L.1306        96  SETUP_LOOP          126  'to 126'
             98_0  COME_FROM           118  '118'

 L.1307        98  LOAD_FAST                'self'
              100  LOAD_ATTR                _file
              102  LOAD_METHOD              readline
              104  CALL_METHOD_0         0  '0 positional arguments'
              106  STORE_FAST               'line'

 L.1308       108  LOAD_FAST                'line'
              110  LOAD_GLOBAL              linesep
              112  COMPARE_OP               ==
              114  POP_JUMP_IF_TRUE    120  'to 120'
              116  LOAD_FAST                'line'
              118  POP_JUMP_IF_TRUE     98  'to 98'
            120_0  COME_FROM           114  '114'

 L.1309       120  BREAK_LOOP       
              122  JUMP_BACK            98  'to 98'
              124  POP_BLOCK        
            126_0  COME_FROM_LOOP       96  '96'

 L.1310       126  LOAD_FAST                'original_headers'
              128  LOAD_METHOD              getvalue
              130  CALL_METHOD_0         0  '0 positional arguments'
              132  STORE_FAST               'headers'

 L.1311       134  LOAD_FAST                'stop'
              136  LOAD_FAST                'self'
              138  LOAD_ATTR                _file
              140  LOAD_METHOD              tell
              142  CALL_METHOD_0         0  '0 positional arguments'
              144  BINARY_SUBTRACT  
              146  STORE_FAST               'n'

 L.1313       148  LOAD_FAST                'self'
              150  LOAD_ATTR                _file
              152  LOAD_METHOD              read
              154  LOAD_FAST                'n'
              156  CALL_METHOD_1         1  '1 positional argument'
              158  STORE_FAST               'data'

 L.1314       160  LOAD_FAST                'data'
              162  LOAD_METHOD              replace
              164  LOAD_GLOBAL              linesep
              166  LOAD_CONST               b'\n'
              168  CALL_METHOD_2         2  '2 positional arguments'
              170  STORE_FAST               'data'

 L.1315       172  LOAD_FAST                'headers'
              174  LOAD_FAST                'data'
              176  BINARY_ADD       
              178  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `BREAK_LOOP' instruction at offset 120

    def get_file(self, key):
        return io.BytesIO(self.get_bytes(key).replace(b'\n', linesep))

    def get_labels(self):
        self._lookup()
        labels = set()
        for label_list in self._labels.values():
            labels.update(label_list)

        labels.difference_update(self._special_labels)
        return list(labels)

    def _generate_toc(self):
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        label_lists = []
        while 1:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            if line == b'\x1f\x0c' + linesep:
                if len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
                starts.append(next_pos)
                labels = [label.strip() for label in self._file.readline()[1:].split(b',') if label.strip()]
                label_lists.append(labels)
            elif line == b'\x1f' or line == b'\x1f' + linesep:
                if len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
            else:
                line or stops.append(line_pos - len(linesep))
                break

        self._toc = dict(enumerate(zip(starts, stops)))
        self._labels = dict(enumerate(label_lists))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()

    def _pre_mailbox_hook(self, f):
        babyl = b'BABYL OPTIONS:' + linesep
        babyl += b'Version: 5' + linesep
        labels = self.get_labels()
        labels = (label.encode() for label in labels)
        babyl += b'Labels:' + (b',').join(labels) + linesep
        babyl += b'\x1f'
        f.write(babyl)

    def _pre_message_hook(self, f):
        f.write(b'\x0c' + linesep)

    def _post_message_hook(self, f):
        f.write(linesep + b'\x1f')

    def _install_message--- This code section failed: ---

 L.1380         0  LOAD_FAST                'self'
                2  LOAD_ATTR                _file
                4  LOAD_METHOD              tell
                6  CALL_METHOD_0         0  '0 positional arguments'
                8  STORE_FAST               'start'

 L.1381        10  LOAD_GLOBAL              isinstance
               12  LOAD_FAST                'message'
               14  LOAD_GLOBAL              BabylMessage
               16  CALL_FUNCTION_2       2  '2 positional arguments'
               18  POP_JUMP_IF_FALSE   188  'to 188'

 L.1382        20  BUILD_LIST_0          0 
               22  STORE_FAST               'special_labels'

 L.1383        24  BUILD_LIST_0          0 
               26  STORE_FAST               'labels'

 L.1384        28  SETUP_LOOP           78  'to 78'
               30  LOAD_FAST                'message'
               32  LOAD_METHOD              get_labels
               34  CALL_METHOD_0         0  '0 positional arguments'
               36  GET_ITER         
               38  FOR_ITER             76  'to 76'
               40  STORE_FAST               'label'

 L.1385        42  LOAD_FAST                'label'
               44  LOAD_FAST                'self'
               46  LOAD_ATTR                _special_labels
               48  COMPARE_OP               in
               50  POP_JUMP_IF_FALSE    64  'to 64'

 L.1386        52  LOAD_FAST                'special_labels'
               54  LOAD_METHOD              append
               56  LOAD_FAST                'label'
               58  CALL_METHOD_1         1  '1 positional argument'
               60  POP_TOP          
               62  JUMP_BACK            38  'to 38'
             64_0  COME_FROM            50  '50'

 L.1388        64  LOAD_FAST                'labels'
               66  LOAD_METHOD              append
               68  LOAD_FAST                'label'
               70  CALL_METHOD_1         1  '1 positional argument'
               72  POP_TOP          
               74  JUMP_BACK            38  'to 38'
               76  POP_BLOCK        
             78_0  COME_FROM_LOOP       28  '28'

 L.1389        78  LOAD_FAST                'self'
               80  LOAD_ATTR                _file
               82  LOAD_METHOD              write
               84  LOAD_CONST               b'1'
               86  CALL_METHOD_1         1  '1 positional argument'
               88  POP_TOP          

 L.1390        90  SETUP_LOOP          124  'to 124'
               92  LOAD_FAST                'special_labels'
               94  GET_ITER         
               96  FOR_ITER            122  'to 122'
               98  STORE_FAST               'label'

 L.1391       100  LOAD_FAST                'self'
              102  LOAD_ATTR                _file
              104  LOAD_METHOD              write
              106  LOAD_CONST               b', '
              108  LOAD_FAST                'label'
              110  LOAD_METHOD              encode
              112  CALL_METHOD_0         0  '0 positional arguments'
              114  BINARY_ADD       
              116  CALL_METHOD_1         1  '1 positional argument'
              118  POP_TOP          
              120  JUMP_BACK            96  'to 96'
              122  POP_BLOCK        
            124_0  COME_FROM_LOOP       90  '90'

 L.1392       124  LOAD_FAST                'self'
              126  LOAD_ATTR                _file
              128  LOAD_METHOD              write
              130  LOAD_CONST               b',,'
              132  CALL_METHOD_1         1  '1 positional argument'
              134  POP_TOP          

 L.1393       136  SETUP_LOOP          174  'to 174'
              138  LOAD_FAST                'labels'
              140  GET_ITER         
              142  FOR_ITER            172  'to 172'
              144  STORE_FAST               'label'

 L.1394       146  LOAD_FAST                'self'
              148  LOAD_ATTR                _file
              150  LOAD_METHOD              write
              152  LOAD_CONST               b' '
              154  LOAD_FAST                'label'
              156  LOAD_METHOD              encode
              158  CALL_METHOD_0         0  '0 positional arguments'
              160  BINARY_ADD       
              162  LOAD_CONST               b','
              164  BINARY_ADD       
              166  CALL_METHOD_1         1  '1 positional argument'
              168  POP_TOP          
              170  JUMP_BACK           142  'to 142'
              172  POP_BLOCK        
            174_0  COME_FROM_LOOP      136  '136'

 L.1395       174  LOAD_FAST                'self'
              176  LOAD_ATTR                _file
              178  LOAD_METHOD              write
              180  LOAD_GLOBAL              linesep
              182  CALL_METHOD_1         1  '1 positional argument'
              184  POP_TOP          
              186  JUMP_FORWARD        204  'to 204'
            188_0  COME_FROM            18  '18'

 L.1397       188  LOAD_FAST                'self'
              190  LOAD_ATTR                _file
              192  LOAD_METHOD              write
              194  LOAD_CONST               b'1,,'
              196  LOAD_GLOBAL              linesep
              198  BINARY_ADD       
              200  CALL_METHOD_1         1  '1 positional argument'
              202  POP_TOP          
            204_0  COME_FROM           186  '186'

 L.1398       204  LOAD_GLOBAL              isinstance
              206  LOAD_FAST                'message'
              208  LOAD_GLOBAL              email
              210  LOAD_ATTR                message
              212  LOAD_ATTR                Message
              214  CALL_FUNCTION_2       2  '2 positional arguments'
          216_218  POP_JUMP_IF_FALSE   554  'to 554'

 L.1399       220  LOAD_GLOBAL              io
              222  LOAD_METHOD              BytesIO
              224  CALL_METHOD_0         0  '0 positional arguments'
              226  STORE_FAST               'orig_buffer'

 L.1400       228  LOAD_GLOBAL              email
              230  LOAD_ATTR                generator
              232  LOAD_METHOD              BytesGenerator
              234  LOAD_FAST                'orig_buffer'
              236  LOAD_CONST               False
              238  LOAD_CONST               0
              240  CALL_METHOD_3         3  '3 positional arguments'
              242  STORE_FAST               'orig_generator'

 L.1401       244  LOAD_FAST                'orig_generator'
              246  LOAD_METHOD              flatten
              248  LOAD_FAST                'message'
              250  CALL_METHOD_1         1  '1 positional argument'
              252  POP_TOP          

 L.1402       254  LOAD_FAST                'orig_buffer'
              256  LOAD_METHOD              seek
              258  LOAD_CONST               0
              260  CALL_METHOD_1         1  '1 positional argument'
              262  POP_TOP          

 L.1403       264  SETUP_LOOP          318  'to 318'
            266_0  COME_FROM           306  '306'

 L.1404       266  LOAD_FAST                'orig_buffer'
              268  LOAD_METHOD              readline
              270  CALL_METHOD_0         0  '0 positional arguments'
              272  STORE_FAST               'line'

 L.1405       274  LOAD_FAST                'self'
              276  LOAD_ATTR                _file
              278  LOAD_METHOD              write
              280  LOAD_FAST                'line'
              282  LOAD_METHOD              replace
              284  LOAD_CONST               b'\n'
              286  LOAD_GLOBAL              linesep
              288  CALL_METHOD_2         2  '2 positional arguments'
              290  CALL_METHOD_1         1  '1 positional argument'
              292  POP_TOP          

 L.1406       294  LOAD_FAST                'line'
              296  LOAD_CONST               b'\n'
              298  COMPARE_OP               ==
          300_302  POP_JUMP_IF_TRUE    310  'to 310'
              304  LOAD_FAST                'line'
          306_308  POP_JUMP_IF_TRUE    266  'to 266'
            310_0  COME_FROM           300  '300'

 L.1407       310  BREAK_LOOP       
          312_314  JUMP_BACK           266  'to 266'
              316  POP_BLOCK        
            318_0  COME_FROM_LOOP      264  '264'

 L.1408       318  LOAD_FAST                'self'
              320  LOAD_ATTR                _file
              322  LOAD_METHOD              write
              324  LOAD_CONST               b'*** EOOH ***'
              326  LOAD_GLOBAL              linesep
              328  BINARY_ADD       
              330  CALL_METHOD_1         1  '1 positional argument'
              332  POP_TOP          

 L.1409       334  LOAD_GLOBAL              isinstance
              336  LOAD_FAST                'message'
              338  LOAD_GLOBAL              BabylMessage
              340  CALL_FUNCTION_2       2  '2 positional arguments'
          342_344  POP_JUMP_IF_FALSE   440  'to 440'

 L.1410       346  LOAD_GLOBAL              io
              348  LOAD_METHOD              BytesIO
              350  CALL_METHOD_0         0  '0 positional arguments'
              352  STORE_FAST               'vis_buffer'

 L.1411       354  LOAD_GLOBAL              email
              356  LOAD_ATTR                generator
              358  LOAD_METHOD              BytesGenerator
              360  LOAD_FAST                'vis_buffer'
              362  LOAD_CONST               False
              364  LOAD_CONST               0
              366  CALL_METHOD_3         3  '3 positional arguments'
              368  STORE_FAST               'vis_generator'

 L.1412       370  LOAD_FAST                'vis_generator'
              372  LOAD_METHOD              flatten
              374  LOAD_FAST                'message'
              376  LOAD_METHOD              get_visible
              378  CALL_METHOD_0         0  '0 positional arguments'
              380  CALL_METHOD_1         1  '1 positional argument'
              382  POP_TOP          

 L.1413       384  SETUP_LOOP          504  'to 504'
            386_0  COME_FROM           426  '426'

 L.1414       386  LOAD_FAST                'vis_buffer'
              388  LOAD_METHOD              readline
              390  CALL_METHOD_0         0  '0 positional arguments'
              392  STORE_FAST               'line'

 L.1415       394  LOAD_FAST                'self'
              396  LOAD_ATTR                _file
              398  LOAD_METHOD              write
              400  LOAD_FAST                'line'
              402  LOAD_METHOD              replace
              404  LOAD_CONST               b'\n'
              406  LOAD_GLOBAL              linesep
              408  CALL_METHOD_2         2  '2 positional arguments'
              410  CALL_METHOD_1         1  '1 positional argument'
              412  POP_TOP          

 L.1416       414  LOAD_FAST                'line'
              416  LOAD_CONST               b'\n'
              418  COMPARE_OP               ==
          420_422  POP_JUMP_IF_TRUE    430  'to 430'
              424  LOAD_FAST                'line'
          426_428  POP_JUMP_IF_TRUE    386  'to 386'
            430_0  COME_FROM           420  '420'

 L.1417       430  BREAK_LOOP       
          432_434  JUMP_BACK           386  'to 386'
              436  POP_BLOCK        
              438  JUMP_FORWARD        504  'to 504'
            440_0  COME_FROM           342  '342'

 L.1419       440  LOAD_FAST                'orig_buffer'
              442  LOAD_METHOD              seek
              444  LOAD_CONST               0
              446  CALL_METHOD_1         1  '1 positional argument'
              448  POP_TOP          

 L.1420       450  SETUP_LOOP          504  'to 504'
            452_0  COME_FROM           492  '492'

 L.1421       452  LOAD_FAST                'orig_buffer'
              454  LOAD_METHOD              readline
              456  CALL_METHOD_0         0  '0 positional arguments'
              458  STORE_FAST               'line'

 L.1422       460  LOAD_FAST                'self'
              462  LOAD_ATTR                _file
              464  LOAD_METHOD              write
              466  LOAD_FAST                'line'
              468  LOAD_METHOD              replace
              470  LOAD_CONST               b'\n'
              472  LOAD_GLOBAL              linesep
              474  CALL_METHOD_2         2  '2 positional arguments'
              476  CALL_METHOD_1         1  '1 positional argument'
              478  POP_TOP          

 L.1423       480  LOAD_FAST                'line'
              482  LOAD_CONST               b'\n'
              484  COMPARE_OP               ==
          486_488  POP_JUMP_IF_TRUE    496  'to 496'
              490  LOAD_FAST                'line'
          492_494  POP_JUMP_IF_TRUE    452  'to 452'
            496_0  COME_FROM           486  '486'

 L.1424       496  BREAK_LOOP       
          498_500  JUMP_BACK           452  'to 452'
              502  POP_BLOCK        
            504_0  COME_FROM_LOOP      450  '450'
            504_1  COME_FROM           438  '438'
            504_2  COME_FROM_LOOP      384  '384'

 L.1425       504  SETUP_LOOP          550  'to 550'

 L.1426       506  LOAD_FAST                'orig_buffer'
              508  LOAD_METHOD              read
              510  LOAD_CONST               4096
              512  CALL_METHOD_1         1  '1 positional argument'
              514  STORE_FAST               'buffer'

 L.1427       516  LOAD_FAST                'buffer'
          518_520  POP_JUMP_IF_TRUE    524  'to 524'

 L.1428       522  BREAK_LOOP       
            524_0  COME_FROM           518  '518'

 L.1429       524  LOAD_FAST                'self'
              526  LOAD_ATTR                _file
              528  LOAD_METHOD              write
              530  LOAD_FAST                'buffer'
              532  LOAD_METHOD              replace
              534  LOAD_CONST               b'\n'
              536  LOAD_GLOBAL              linesep
              538  CALL_METHOD_2         2  '2 positional arguments'
              540  CALL_METHOD_1         1  '1 positional argument'
              542  POP_TOP          
          544_546  JUMP_BACK           506  'to 506'
              548  POP_BLOCK        
            550_0  COME_FROM_LOOP      504  '504'
          550_552  JUMP_FORWARD       1154  'to 1154'
            554_0  COME_FROM           216  '216'

 L.1430       554  LOAD_GLOBAL              isinstance
              556  LOAD_FAST                'message'
              558  LOAD_GLOBAL              bytes
              560  LOAD_GLOBAL              str
              562  LOAD_GLOBAL              io
              564  LOAD_ATTR                StringIO
              566  BUILD_TUPLE_3         3 
              568  CALL_FUNCTION_2       2  '2 positional arguments'
          570_572  POP_JUMP_IF_FALSE   806  'to 806'

 L.1431       574  LOAD_GLOBAL              isinstance
              576  LOAD_FAST                'message'
              578  LOAD_GLOBAL              io
              580  LOAD_ATTR                StringIO
              582  CALL_FUNCTION_2       2  '2 positional arguments'
          584_586  POP_JUMP_IF_FALSE   610  'to 610'

 L.1432       588  LOAD_GLOBAL              warnings
              590  LOAD_METHOD              warn
              592  LOAD_STR                 'Use of StringIO input is deprecated, use BytesIO instead'

 L.1433       594  LOAD_GLOBAL              DeprecationWarning
              596  LOAD_CONST               3
              598  CALL_METHOD_3         3  '3 positional arguments'
              600  POP_TOP          

 L.1434       602  LOAD_FAST                'message'
              604  LOAD_METHOD              getvalue
              606  CALL_METHOD_0         0  '0 positional arguments'
              608  STORE_FAST               'message'
            610_0  COME_FROM           584  '584'

 L.1435       610  LOAD_GLOBAL              isinstance
              612  LOAD_FAST                'message'
              614  LOAD_GLOBAL              str
              616  CALL_FUNCTION_2       2  '2 positional arguments'
          618_620  POP_JUMP_IF_FALSE   632  'to 632'

 L.1436       622  LOAD_FAST                'self'
              624  LOAD_METHOD              _string_to_bytes
              626  LOAD_FAST                'message'
              628  CALL_METHOD_1         1  '1 positional argument'
              630  STORE_FAST               'message'
            632_0  COME_FROM           618  '618'

 L.1437       632  LOAD_FAST                'message'
              634  LOAD_METHOD              find
              636  LOAD_CONST               b'\n\n'
              638  CALL_METHOD_1         1  '1 positional argument'
              640  LOAD_CONST               2
              642  BINARY_ADD       
              644  STORE_FAST               'body_start'

 L.1438       646  LOAD_FAST                'body_start'
              648  LOAD_CONST               2
              650  BINARY_SUBTRACT  
              652  LOAD_CONST               -1
              654  COMPARE_OP               !=
          656_658  POP_JUMP_IF_FALSE   762  'to 762'

 L.1439       660  LOAD_FAST                'self'
              662  LOAD_ATTR                _file
              664  LOAD_METHOD              write
              666  LOAD_FAST                'message'
              668  LOAD_CONST               None
              670  LOAD_FAST                'body_start'
              672  BUILD_SLICE_2         2 
              674  BINARY_SUBSCR    
              676  LOAD_METHOD              replace
              678  LOAD_CONST               b'\n'
              680  LOAD_GLOBAL              linesep
              682  CALL_METHOD_2         2  '2 positional arguments'
              684  CALL_METHOD_1         1  '1 positional argument'
              686  POP_TOP          

 L.1440       688  LOAD_FAST                'self'
              690  LOAD_ATTR                _file
              692  LOAD_METHOD              write
              694  LOAD_CONST               b'*** EOOH ***'
              696  LOAD_GLOBAL              linesep
              698  BINARY_ADD       
              700  CALL_METHOD_1         1  '1 positional argument'
              702  POP_TOP          

 L.1441       704  LOAD_FAST                'self'
              706  LOAD_ATTR                _file
              708  LOAD_METHOD              write
              710  LOAD_FAST                'message'
              712  LOAD_CONST               None
              714  LOAD_FAST                'body_start'
              716  BUILD_SLICE_2         2 
              718  BINARY_SUBSCR    
              720  LOAD_METHOD              replace
              722  LOAD_CONST               b'\n'
              724  LOAD_GLOBAL              linesep
              726  CALL_METHOD_2         2  '2 positional arguments'
              728  CALL_METHOD_1         1  '1 positional argument'
              730  POP_TOP          

 L.1442       732  LOAD_FAST                'self'
              734  LOAD_ATTR                _file
              736  LOAD_METHOD              write
              738  LOAD_FAST                'message'
              740  LOAD_FAST                'body_start'
              742  LOAD_CONST               None
              744  BUILD_SLICE_2         2 
              746  BINARY_SUBSCR    
              748  LOAD_METHOD              replace
              750  LOAD_CONST               b'\n'
              752  LOAD_GLOBAL              linesep
              754  CALL_METHOD_2         2  '2 positional arguments'
              756  CALL_METHOD_1         1  '1 positional argument'
              758  POP_TOP          
              760  JUMP_FORWARD       1154  'to 1154'
            762_0  COME_FROM           656  '656'

 L.1444       762  LOAD_FAST                'self'
              764  LOAD_ATTR                _file
              766  LOAD_METHOD              write
              768  LOAD_CONST               b'*** EOOH ***'
              770  LOAD_GLOBAL              linesep
              772  BINARY_ADD       
              774  LOAD_GLOBAL              linesep
              776  BINARY_ADD       
              778  CALL_METHOD_1         1  '1 positional argument'
              780  POP_TOP          

 L.1445       782  LOAD_FAST                'self'
              784  LOAD_ATTR                _file
              786  LOAD_METHOD              write
              788  LOAD_FAST                'message'
              790  LOAD_METHOD              replace
              792  LOAD_CONST               b'\n'
              794  LOAD_GLOBAL              linesep
              796  CALL_METHOD_2         2  '2 positional arguments'
              798  CALL_METHOD_1         1  '1 positional argument'
              800  POP_TOP          
          802_804  JUMP_FORWARD       1154  'to 1154'
            806_0  COME_FROM           570  '570'

 L.1446       806  LOAD_GLOBAL              hasattr
              808  LOAD_FAST                'message'
              810  LOAD_STR                 'readline'
              812  CALL_FUNCTION_2       2  '2 positional arguments'
          814_816  POP_JUMP_IF_FALSE  1138  'to 1138'

 L.1447       818  LOAD_GLOBAL              hasattr
              820  LOAD_FAST                'message'
              822  LOAD_STR                 'buffer'
              824  CALL_FUNCTION_2       2  '2 positional arguments'
          826_828  POP_JUMP_IF_FALSE   850  'to 850'

 L.1448       830  LOAD_GLOBAL              warnings
              832  LOAD_METHOD              warn
              834  LOAD_STR                 'Use of text mode files is deprecated, use a binary mode file instead'

 L.1449       836  LOAD_GLOBAL              DeprecationWarning
              838  LOAD_CONST               3
              840  CALL_METHOD_3         3  '3 positional arguments'
              842  POP_TOP          

 L.1450       844  LOAD_FAST                'message'
              846  LOAD_ATTR                buffer
              848  STORE_FAST               'message'
            850_0  COME_FROM           826  '826'

 L.1451       850  LOAD_FAST                'message'
              852  LOAD_METHOD              tell
              854  CALL_METHOD_0         0  '0 positional arguments'
              856  STORE_FAST               'original_pos'

 L.1452       858  LOAD_CONST               True
              860  STORE_FAST               'first_pass'

 L.1453       862  SETUP_LOOP         1012  'to 1012'
            864_0  COME_FROM           962  '962'

 L.1454       864  LOAD_FAST                'message'
              866  LOAD_METHOD              readline
              868  CALL_METHOD_0         0  '0 positional arguments'
              870  STORE_FAST               'line'

 L.1456       872  LOAD_FAST                'line'
              874  LOAD_METHOD              endswith
              876  LOAD_CONST               b'\r\n'
              878  CALL_METHOD_1         1  '1 positional argument'
          880_882  POP_JUMP_IF_FALSE   902  'to 902'

 L.1457       884  LOAD_FAST                'line'
              886  LOAD_CONST               None
              888  LOAD_CONST               -2
              890  BUILD_SLICE_2         2 
              892  BINARY_SUBSCR    
              894  LOAD_CONST               b'\n'
              896  BINARY_ADD       
              898  STORE_FAST               'line'
              900  JUMP_FORWARD        930  'to 930'
            902_0  COME_FROM           880  '880'

 L.1458       902  LOAD_FAST                'line'
              904  LOAD_METHOD              endswith
              906  LOAD_CONST               b'\r'
              908  CALL_METHOD_1         1  '1 positional argument'
          910_912  POP_JUMP_IF_FALSE   930  'to 930'

 L.1459       914  LOAD_FAST                'line'
              916  LOAD_CONST               None
              918  LOAD_CONST               -1
              920  BUILD_SLICE_2         2 
              922  BINARY_SUBSCR    
              924  LOAD_CONST               b'\n'
              926  BINARY_ADD       
              928  STORE_FAST               'line'
            930_0  COME_FROM           910  '910'
            930_1  COME_FROM           900  '900'

 L.1460       930  LOAD_FAST                'self'
              932  LOAD_ATTR                _file
              934  LOAD_METHOD              write
              936  LOAD_FAST                'line'
              938  LOAD_METHOD              replace
              940  LOAD_CONST               b'\n'
              942  LOAD_GLOBAL              linesep
              944  CALL_METHOD_2         2  '2 positional arguments'
              946  CALL_METHOD_1         1  '1 positional argument'
              948  POP_TOP          

 L.1461       950  LOAD_FAST                'line'
              952  LOAD_CONST               b'\n'
              954  COMPARE_OP               ==
          956_958  POP_JUMP_IF_TRUE    966  'to 966'
              960  LOAD_FAST                'line'
          962_964  POP_JUMP_IF_TRUE    864  'to 864'
            966_0  COME_FROM           956  '956'

 L.1462       966  LOAD_FAST                'first_pass'
          968_970  POP_JUMP_IF_FALSE  1004  'to 1004'

 L.1463       972  LOAD_CONST               False
              974  STORE_FAST               'first_pass'

 L.1464       976  LOAD_FAST                'self'
              978  LOAD_ATTR                _file
              980  LOAD_METHOD              write
              982  LOAD_CONST               b'*** EOOH ***'
              984  LOAD_GLOBAL              linesep
              986  BINARY_ADD       
              988  CALL_METHOD_1         1  '1 positional argument'
              990  POP_TOP          

 L.1465       992  LOAD_FAST                'message'
              994  LOAD_METHOD              seek
              996  LOAD_FAST                'original_pos'
              998  CALL_METHOD_1         1  '1 positional argument'
             1000  POP_TOP          
             1002  JUMP_BACK           864  'to 864'
           1004_0  COME_FROM           968  '968'

 L.1467      1004  BREAK_LOOP       
         1006_1008  JUMP_BACK           864  'to 864'
             1010  POP_BLOCK        
           1012_0  COME_FROM_LOOP      862  '862'

 L.1468      1012  SETUP_LOOP         1154  'to 1154'

 L.1469      1014  LOAD_FAST                'message'
             1016  LOAD_METHOD              readline
             1018  CALL_METHOD_0         0  '0 positional arguments'
             1020  STORE_FAST               'line'

 L.1470      1022  LOAD_FAST                'line'
         1024_1026  POP_JUMP_IF_TRUE   1030  'to 1030'

 L.1471      1028  BREAK_LOOP       
           1030_0  COME_FROM          1024  '1024'

 L.1473      1030  LOAD_FAST                'line'
             1032  LOAD_METHOD              endswith
             1034  LOAD_CONST               b'\r\n'
             1036  CALL_METHOD_1         1  '1 positional argument'
         1038_1040  POP_JUMP_IF_FALSE  1060  'to 1060'

 L.1474      1042  LOAD_FAST                'line'
             1044  LOAD_CONST               None
             1046  LOAD_CONST               -2
             1048  BUILD_SLICE_2         2 
             1050  BINARY_SUBSCR    
             1052  LOAD_GLOBAL              linesep
             1054  BINARY_ADD       
             1056  STORE_FAST               'line'
             1058  JUMP_FORWARD       1118  'to 1118'
           1060_0  COME_FROM          1038  '1038'

 L.1475      1060  LOAD_FAST                'line'
             1062  LOAD_METHOD              endswith
             1064  LOAD_CONST               b'\r'
             1066  CALL_METHOD_1         1  '1 positional argument'
         1068_1070  POP_JUMP_IF_FALSE  1090  'to 1090'

 L.1476      1072  LOAD_FAST                'line'
             1074  LOAD_CONST               None
             1076  LOAD_CONST               -1
             1078  BUILD_SLICE_2         2 
             1080  BINARY_SUBSCR    
             1082  LOAD_GLOBAL              linesep
             1084  BINARY_ADD       
             1086  STORE_FAST               'line'
             1088  JUMP_FORWARD       1118  'to 1118'
           1090_0  COME_FROM          1068  '1068'

 L.1477      1090  LOAD_FAST                'line'
             1092  LOAD_METHOD              endswith
             1094  LOAD_CONST               b'\n'
             1096  CALL_METHOD_1         1  '1 positional argument'
         1098_1100  POP_JUMP_IF_FALSE  1118  'to 1118'

 L.1478      1102  LOAD_FAST                'line'
             1104  LOAD_CONST               None
             1106  LOAD_CONST               -1
             1108  BUILD_SLICE_2         2 
           1110_0  COME_FROM           760  '760'
             1110  BINARY_SUBSCR    
             1112  LOAD_GLOBAL              linesep
             1114  BINARY_ADD       
             1116  STORE_FAST               'line'
           1118_0  COME_FROM          1098  '1098'
           1118_1  COME_FROM          1088  '1088'
           1118_2  COME_FROM          1058  '1058'

 L.1479      1118  LOAD_FAST                'self'
             1120  LOAD_ATTR                _file
             1122  LOAD_METHOD              write
             1124  LOAD_FAST                'line'
             1126  CALL_METHOD_1         1  '1 positional argument'
             1128  POP_TOP          
         1130_1132  JUMP_BACK          1014  'to 1014'
             1134  POP_BLOCK        
             1136  JUMP_FORWARD       1154  'to 1154'
           1138_0  COME_FROM           814  '814'

 L.1481      1138  LOAD_GLOBAL              TypeError
             1140  LOAD_STR                 'Invalid message type: %s'
             1142  LOAD_GLOBAL              type
             1144  LOAD_FAST                'message'
             1146  CALL_FUNCTION_1       1  '1 positional argument'
             1148  BINARY_MODULO    
             1150  CALL_FUNCTION_1       1  '1 positional argument'
             1152  RAISE_VARARGS_1       1  'exception instance'
           1154_0  COME_FROM          1136  '1136'
           1154_1  COME_FROM_LOOP     1012  '1012'
           1154_2  COME_FROM           802  '802'
           1154_3  COME_FROM           550  '550'

 L.1482      1154  LOAD_FAST                'self'
             1156  LOAD_ATTR                _file
             1158  LOAD_METHOD              tell
             1160  CALL_METHOD_0         0  '0 positional arguments'
             1162  STORE_FAST               'stop'

 L.1483      1164  LOAD_FAST                'start'
             1166  LOAD_FAST                'stop'
             1168  BUILD_TUPLE_2         2 
             1170  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `BREAK_LOOP' instruction at offset 310


class Message(email.message.Message):

    def __init__(self, message=None):
        if isinstance(message, email.message.Message):
            self._become_message(copy.deepcopy(message))
            if isinstance(message, Message):
                message._explain_to(self)
        elif isinstance(message, bytes):
            self._become_message(email.message_from_bytes(message))
        else:
            if isinstance(message, str):
                self._become_message(email.message_from_string(message))
            else:
                if isinstance(message, io.TextIOWrapper):
                    self._become_message(email.message_from_file(message))
                else:
                    if hasattr(message, 'read'):
                        self._become_message(email.message_from_binary_file(message))
                    else:
                        if message is None:
                            email.message.Message.__init__(self)
                        else:
                            raise TypeError('Invalid message type: %s' % type(message))

    def _become_message(self, message):
        type_specific = getattr(message, '_type_specific_attributes', [])
        for name in message.__dict__:
            if name not in type_specific:
                self.__dict__[name] = message.__dict__[name]

    def _explain_to(self, message):
        if isinstance(message, Message):
            return
        raise TypeError('Cannot convert to specified type')


class MaildirMessage(Message):
    _type_specific_attributes = [
     '_subdir', '_info', '_date']

    def __init__(self, message=None):
        self._subdir = 'new'
        self._info = ''
        self._date = time.time()
        Message.__init__(self, message)

    def get_subdir(self):
        return self._subdir

    def set_subdir(self, subdir):
        if subdir == 'new' or subdir == 'cur':
            self._subdir = subdir
        else:
            raise ValueError("subdir must be 'new' or 'cur': %s" % subdir)

    def get_flags(self):
        if self._info.startswith('2,'):
            return self._info[2:]
        return ''

    def set_flags(self, flags):
        self._info = '2,' + ''.join(sorted(flags))

    def add_flag(self, flag):
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    def remove_flag(self, flag):
        if self.get_flags():
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    def get_date(self):
        return self._date

    def set_date(self, date):
        try:
            self._date = float(date)
        except ValueError:
            raise TypeError("can't convert to float: %s" % date) from None

    def get_info(self):
        return self._info

    def set_info(self, info):
        if isinstance(info, str):
            self._info = info
        else:
            raise TypeError('info must be a string: %s' % type(info))

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            message.set_flags(self.get_flags())
            message.set_subdir(self.get_subdir())
            message.set_date(self.get_date())
        else:
            if isinstance(message, _mboxMMDFMessage):
                flags = set(self.get_flags())
                if 'S' in flags:
                    message.add_flag('R')
                if self.get_subdir() == 'cur':
                    message.add_flag('O')
                if 'T' in flags:
                    message.add_flag('D')
                if 'F' in flags:
                    message.add_flag('F')
                if 'R' in flags:
                    message.add_flag('A')
                message.set_from('MAILER-DAEMON', time.gmtime(self.get_date()))
            else:
                if isinstance(message, MHMessage):
                    flags = set(self.get_flags())
                    if 'S' not in flags:
                        message.add_sequence('unseen')
                    if 'R' in flags:
                        message.add_sequence('replied')
                    if 'F' in flags:
                        message.add_sequence('flagged')
                elif isinstance(message, BabylMessage):
                    flags = set(self.get_flags())
                    if 'S' not in flags:
                        message.add_label('unseen')
                    if 'T' in flags:
                        message.add_label('deleted')
                    if 'R' in flags:
                        message.add_label('answered')
                    if 'P' in flags:
                        message.add_label('forwarded')
                elif isinstance(message, Message):
                    pass
                else:
                    raise TypeError('Cannot convert to specified type: %s' % type(message))


class _mboxMMDFMessage(Message):
    _type_specific_attributes = [
     '_from']

    def __init__(self, message=None):
        self.set_from('MAILER-DAEMON', True)
        if isinstance(message, email.message.Message):
            unixfrom = message.get_unixfrom()
            if unixfrom is not None:
                if unixfrom.startswith('From '):
                    self.set_from(unixfrom[5:])
        Message.__init__(self, message)

    def get_from(self):
        return self._from

    def set_from(self, from_, time_=None):
        if time_ is not None:
            if time_ is True:
                time_ = time.gmtime()
            from_ += ' ' + time.asctime(time_)
        self._from = from_

    def get_flags(self):
        return self.get('Status', '') + self.get('X-Status', '')

    def set_flags(self, flags):
        flags = set(flags)
        status_flags, xstatus_flags = ('', '')
        for flag in ('R', 'O'):
            if flag in flags:
                status_flags += flag
                flags.remove(flag)

        for flag in ('D', 'F', 'A'):
            if flag in flags:
                xstatus_flags += flag
                flags.remove(flag)

        xstatus_flags += ''.join(sorted(flags))
        try:
            self.replace_header('Status', status_flags)
        except KeyError:
            self.add_header('Status', status_flags)

        try:
            self.replace_header('X-Status', xstatus_flags)
        except KeyError:
            self.add_header('X-Status', xstatus_flags)

    def add_flag(self, flag):
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    def remove_flag(self, flag):
        if 'Status' in self or 'X-Status' in self:
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    def _explain_to--- This code section failed: ---

 L.1695         0  LOAD_GLOBAL              isinstance
                2  LOAD_FAST                'message'
                4  LOAD_GLOBAL              MaildirMessage
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  POP_JUMP_IF_FALSE   208  'to 208'

 L.1696        10  LOAD_GLOBAL              set
               12  LOAD_FAST                'self'
               14  LOAD_METHOD              get_flags
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  CALL_FUNCTION_1       1  '1 positional argument'
               20  STORE_FAST               'flags'

 L.1697        22  LOAD_STR                 'O'
               24  LOAD_FAST                'flags'
               26  COMPARE_OP               in
               28  POP_JUMP_IF_FALSE    40  'to 40'

 L.1698        30  LOAD_FAST                'message'
               32  LOAD_METHOD              set_subdir
               34  LOAD_STR                 'cur'
               36  CALL_METHOD_1         1  '1 positional argument'
               38  POP_TOP          
             40_0  COME_FROM            28  '28'

 L.1699        40  LOAD_STR                 'F'
               42  LOAD_FAST                'flags'
               44  COMPARE_OP               in
               46  POP_JUMP_IF_FALSE    58  'to 58'

 L.1700        48  LOAD_FAST                'message'
               50  LOAD_METHOD              add_flag
               52  LOAD_STR                 'F'
               54  CALL_METHOD_1         1  '1 positional argument'
               56  POP_TOP          
             58_0  COME_FROM            46  '46'

 L.1701        58  LOAD_STR                 'A'
               60  LOAD_FAST                'flags'
               62  COMPARE_OP               in
               64  POP_JUMP_IF_FALSE    76  'to 76'

 L.1702        66  LOAD_FAST                'message'
               68  LOAD_METHOD              add_flag
               70  LOAD_STR                 'R'
               72  CALL_METHOD_1         1  '1 positional argument'
               74  POP_TOP          
             76_0  COME_FROM            64  '64'

 L.1703        76  LOAD_STR                 'R'
               78  LOAD_FAST                'flags'
               80  COMPARE_OP               in
               82  POP_JUMP_IF_FALSE    94  'to 94'

 L.1704        84  LOAD_FAST                'message'
               86  LOAD_METHOD              add_flag
               88  LOAD_STR                 'S'
               90  CALL_METHOD_1         1  '1 positional argument'
               92  POP_TOP          
             94_0  COME_FROM            82  '82'

 L.1705        94  LOAD_STR                 'D'
               96  LOAD_FAST                'flags'
               98  COMPARE_OP               in
              100  POP_JUMP_IF_FALSE   112  'to 112'

 L.1706       102  LOAD_FAST                'message'
              104  LOAD_METHOD              add_flag
              106  LOAD_STR                 'T'
              108  CALL_METHOD_1         1  '1 positional argument'
              110  POP_TOP          
            112_0  COME_FROM           100  '100'

 L.1707       112  LOAD_FAST                'message'
              114  LOAD_STR                 'status'
              116  DELETE_SUBSCR    

 L.1708       118  LOAD_FAST                'message'
              120  LOAD_STR                 'x-status'
              122  DELETE_SUBSCR    

 L.1709       124  LOAD_STR                 ' '
              126  LOAD_METHOD              join
              128  LOAD_FAST                'self'
              130  LOAD_METHOD              get_from
              132  CALL_METHOD_0         0  '0 positional arguments'
              134  LOAD_METHOD              split
              136  CALL_METHOD_0         0  '0 positional arguments'
              138  LOAD_CONST               -5
              140  LOAD_CONST               None
              142  BUILD_SLICE_2         2 
              144  BINARY_SUBSCR    
              146  CALL_METHOD_1         1  '1 positional argument'
              148  STORE_FAST               'maybe_date'

 L.1710       150  SETUP_EXCEPT        180  'to 180'

 L.1711       152  LOAD_FAST                'message'
              154  LOAD_METHOD              set_date
              156  LOAD_GLOBAL              calendar
              158  LOAD_METHOD              timegm
              160  LOAD_GLOBAL              time
              162  LOAD_METHOD              strptime
              164  LOAD_FAST                'maybe_date'

 L.1712       166  LOAD_STR                 '%a %b %d %H:%M:%S %Y'
              168  CALL_METHOD_2         2  '2 positional arguments'
              170  CALL_METHOD_1         1  '1 positional argument'
              172  CALL_METHOD_1         1  '1 positional argument'
              174  POP_TOP          
              176  POP_BLOCK        
              178  JUMP_FORWARD        474  'to 474'
            180_0  COME_FROM_EXCEPT    150  '150'

 L.1713       180  DUP_TOP          
              182  LOAD_GLOBAL              ValueError
              184  LOAD_GLOBAL              OverflowError
              186  BUILD_TUPLE_2         2 
              188  COMPARE_OP               exception-match
              190  POP_JUMP_IF_FALSE   202  'to 202'
              192  POP_TOP          
              194  POP_TOP          
              196  POP_TOP          

 L.1714       198  POP_EXCEPT       
              200  JUMP_FORWARD        474  'to 474'
            202_0  COME_FROM           190  '190'
              202  END_FINALLY      
          204_206  JUMP_FORWARD        474  'to 474'
            208_0  COME_FROM             8  '8'

 L.1715       208  LOAD_GLOBAL              isinstance
              210  LOAD_FAST                'message'
              212  LOAD_GLOBAL              _mboxMMDFMessage
              214  CALL_FUNCTION_2       2  '2 positional arguments'
              216  POP_JUMP_IF_FALSE   248  'to 248'

 L.1716       218  LOAD_FAST                'message'
              220  LOAD_METHOD              set_flags
              222  LOAD_FAST                'self'
              224  LOAD_METHOD              get_flags
              226  CALL_METHOD_0         0  '0 positional arguments'
              228  CALL_METHOD_1         1  '1 positional argument'
              230  POP_TOP          

 L.1717       232  LOAD_FAST                'message'
              234  LOAD_METHOD              set_from
              236  LOAD_FAST                'self'
              238  LOAD_METHOD              get_from
              240  CALL_METHOD_0         0  '0 positional arguments'
              242  CALL_METHOD_1         1  '1 positional argument'
              244  POP_TOP          
              246  JUMP_FORWARD        474  'to 474'
            248_0  COME_FROM           216  '216'

 L.1718       248  LOAD_GLOBAL              isinstance
              250  LOAD_FAST                'message'
              252  LOAD_GLOBAL              MHMessage
              254  CALL_FUNCTION_2       2  '2 positional arguments'
          256_258  POP_JUMP_IF_FALSE   346  'to 346'

 L.1719       260  LOAD_GLOBAL              set
              262  LOAD_FAST                'self'
              264  LOAD_METHOD              get_flags
              266  CALL_METHOD_0         0  '0 positional arguments'
              268  CALL_FUNCTION_1       1  '1 positional argument'
              270  STORE_FAST               'flags'

 L.1720       272  LOAD_STR                 'R'
              274  LOAD_FAST                'flags'
              276  COMPARE_OP               not-in
          278_280  POP_JUMP_IF_FALSE   292  'to 292'

 L.1721       282  LOAD_FAST                'message'
              284  LOAD_METHOD              add_sequence
              286  LOAD_STR                 'unseen'
              288  CALL_METHOD_1         1  '1 positional argument'
              290  POP_TOP          
            292_0  COME_FROM           278  '278'

 L.1722       292  LOAD_STR                 'A'
              294  LOAD_FAST                'flags'
              296  COMPARE_OP               in
          298_300  POP_JUMP_IF_FALSE   312  'to 312'

 L.1723       302  LOAD_FAST                'message'
              304  LOAD_METHOD              add_sequence
              306  LOAD_STR                 'replied'
              308  CALL_METHOD_1         1  '1 positional argument'
              310  POP_TOP          
            312_0  COME_FROM           298  '298'

 L.1724       312  LOAD_STR                 'F'
              314  LOAD_FAST                'flags'
              316  COMPARE_OP               in
          318_320  POP_JUMP_IF_FALSE   332  'to 332'

 L.1725       322  LOAD_FAST                'message'
              324  LOAD_METHOD              add_sequence
              326  LOAD_STR                 'flagged'
              328  CALL_METHOD_1         1  '1 positional argument'
              330  POP_TOP          
            332_0  COME_FROM           318  '318'

 L.1726       332  LOAD_FAST                'message'
              334  LOAD_STR                 'status'
              336  DELETE_SUBSCR    

 L.1727       338  LOAD_FAST                'message'
              340  LOAD_STR                 'x-status'
              342  DELETE_SUBSCR    
              344  JUMP_FORWARD        474  'to 474'
            346_0  COME_FROM           256  '256'

 L.1728       346  LOAD_GLOBAL              isinstance
              348  LOAD_FAST                'message'
              350  LOAD_GLOBAL              BabylMessage
              352  CALL_FUNCTION_2       2  '2 positional arguments'
          354_356  POP_JUMP_IF_FALSE   444  'to 444'

 L.1729       358  LOAD_GLOBAL              set
              360  LOAD_FAST                'self'
              362  LOAD_METHOD              get_flags
              364  CALL_METHOD_0         0  '0 positional arguments'
              366  CALL_FUNCTION_1       1  '1 positional argument'
              368  STORE_FAST               'flags'

 L.1730       370  LOAD_STR                 'R'
              372  LOAD_FAST                'flags'
              374  COMPARE_OP               not-in
          376_378  POP_JUMP_IF_FALSE   390  'to 390'

 L.1731       380  LOAD_FAST                'message'
              382  LOAD_METHOD              add_label
              384  LOAD_STR                 'unseen'
              386  CALL_METHOD_1         1  '1 positional argument'
              388  POP_TOP          
            390_0  COME_FROM           376  '376'

 L.1732       390  LOAD_STR                 'D'
              392  LOAD_FAST                'flags'
              394  COMPARE_OP               in
          396_398  POP_JUMP_IF_FALSE   410  'to 410'

 L.1733       400  LOAD_FAST                'message'
              402  LOAD_METHOD              add_label
              404  LOAD_STR                 'deleted'
              406  CALL_METHOD_1         1  '1 positional argument'
              408  POP_TOP          
            410_0  COME_FROM           396  '396'

 L.1734       410  LOAD_STR                 'A'
              412  LOAD_FAST                'flags'
              414  COMPARE_OP               in
          416_418  POP_JUMP_IF_FALSE   430  'to 430'

 L.1735       420  LOAD_FAST                'message'
              422  LOAD_METHOD              add_label
              424  LOAD_STR                 'answered'
              426  CALL_METHOD_1         1  '1 positional argument'
              428  POP_TOP          
            430_0  COME_FROM           416  '416'

 L.1736       430  LOAD_FAST                'message'
              432  LOAD_STR                 'status'
              434  DELETE_SUBSCR    

 L.1737       436  LOAD_FAST                'message'
              438  LOAD_STR                 'x-status'
              440  DELETE_SUBSCR    
              442  JUMP_FORWARD        474  'to 474'
            444_0  COME_FROM           354  '354'

 L.1738       444  LOAD_GLOBAL              isinstance
            446_0  COME_FROM           178  '178'
              446  LOAD_FAST                'message'
              448  LOAD_GLOBAL              Message
              450  CALL_FUNCTION_2       2  '2 positional arguments'
          452_454  POP_JUMP_IF_FALSE   458  'to 458'

 L.1739       456  JUMP_FORWARD        474  'to 474'
            458_0  COME_FROM           452  '452'

 L.1741       458  LOAD_GLOBAL              TypeError
              460  LOAD_STR                 'Cannot convert to specified type: %s'

 L.1742       462  LOAD_GLOBAL              type
              464  LOAD_FAST                'message'
              466  CALL_FUNCTION_1       1  '1 positional argument'
            468_0  COME_FROM           200  '200'
              468  BINARY_MODULO    
              470  CALL_FUNCTION_1       1  '1 positional argument'
              472  RAISE_VARARGS_1       1  'exception instance'
            474_0  COME_FROM           456  '456'
            474_1  COME_FROM           442  '442'
            474_2  COME_FROM           344  '344'
            474_3  COME_FROM           246  '246'
            474_4  COME_FROM           204  '204'

Parse error at or near `COME_FROM' instruction at offset 446_0


class mboxMessage(_mboxMMDFMessage):
    pass


class MHMessage(Message):
    _type_specific_attributes = [
     '_sequences']

    def __init__(self, message=None):
        self._sequences = []
        Message.__init__(self, message)

    def get_sequences(self):
        return self._sequences[:]

    def set_sequences(self, sequences):
        self._sequences = list(sequences)

    def add_sequence(self, sequence):
        if isinstance(sequence, str):
            if sequence not in self._sequences:
                self._sequences.append(sequence)
        else:
            raise TypeError('sequence type must be str: %s' % type(sequence))

    def remove_sequence(self, sequence):
        try:
            self._sequences.remove(sequence)
        except ValueError:
            pass

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            sequences = set(self.get_sequences())
            if 'unseen' in sequences:
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
            if 'flagged' in sequences:
                message.add_flag('F')
            if 'replied' in sequences:
                message.add_flag('R')
        else:
            if isinstance(message, _mboxMMDFMessage):
                sequences = set(self.get_sequences())
                if 'unseen' not in sequences:
                    message.add_flag('RO')
                else:
                    message.add_flag('O')
                if 'flagged' in sequences:
                    message.add_flag('F')
                if 'replied' in sequences:
                    message.add_flag('A')
            else:
                if isinstance(message, MHMessage):
                    for sequence in self.get_sequences():
                        message.add_sequence(sequence)

                else:
                    if isinstance(message, BabylMessage):
                        sequences = set(self.get_sequences())
                        if 'unseen' in sequences:
                            message.add_label('unseen')
                        if 'replied' in sequences:
                            message.add_label('answered')
                    elif isinstance(message, Message):
                        pass
                    else:
                        raise TypeError('Cannot convert to specified type: %s' % type(message))


class BabylMessage(Message):
    _type_specific_attributes = [
     '_labels', '_visible']

    def __init__(self, message=None):
        self._labels = []
        self._visible = Message()
        Message.__init__(self, message)

    def get_labels(self):
        return self._labels[:]

    def set_labels(self, labels):
        self._labels = list(labels)

    def add_label(self, label):
        if isinstance(label, str):
            if label not in self._labels:
                self._labels.append(label)
        else:
            raise TypeError('label must be a string: %s' % type(label))

    def remove_label(self, label):
        try:
            self._labels.remove(label)
        except ValueError:
            pass

    def get_visible(self):
        return Message(self._visible)

    def set_visible(self, visible):
        self._visible = Message(visible)

    def update_visible(self):
        for header in self._visible.keys():
            if header in self:
                self._visible.replace_header(header, self[header])
            else:
                del self._visible[header]

        for header in ('Date', 'From', 'Reply-To', 'To', 'CC', 'Subject'):
            if header in self and header not in self._visible:
                self._visible[header] = self[header]

    def _explain_to(self, message):
        if isinstance(message, MaildirMessage):
            labels = set(self.get_labels())
            if 'unseen' in labels:
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
            if not 'forwarded' in labels:
                if 'resent' in labels:
                    message.add_flag('P')
                if 'answered' in labels:
                    message.add_flag('R')
                if 'deleted' in labels:
                    message.add_flag('T')
            else:
                pass
        if isinstance(message, _mboxMMDFMessage):
            labels = set(self.get_labels())
            if 'unseen' not in labels:
                message.add_flag('RO')
            else:
                message.add_flag('O')
            if 'deleted' in labels:
                message.add_flag('D')
            if 'answered' in labels:
                message.add_flag('A')
        else:
            if isinstance(message, MHMessage):
                labels = set(self.get_labels())
                if 'unseen' in labels:
                    message.add_sequence('unseen')
                if 'answered' in labels:
                    message.add_sequence('replied')
            elif isinstance(message, BabylMessage):
                message.set_visible(self.get_visible())
                for label in self.get_labels():
                    message.add_label(label)

            else:
                if isinstance(message, Message):
                    pass
                else:
                    raise TypeError('Cannot convert to specified type: %s' % type(message))


class MMDFMessage(_mboxMMDFMessage):
    pass


class _ProxyFile:

    def __init__(self, f, pos=None):
        self._file = f
        if pos is None:
            self._pos = f.tell()
        else:
            self._pos = pos

    def read(self, size=None):
        return self._read(size, self._file.read)

    def read1(self, size=None):
        return self._read(size, self._file.read1)

    def readline(self, size=None):
        return self._read(size, self._file.readline)

    def readlines(self, sizehint=None):
        result = []
        for line in self:
            result.append(line)
            if sizehint is not None:
                sizehint -= len(line)
                if sizehint <= 0:
                    break

        return result

    def __iter__(self):
        while 1:
            line = self.readline()
            if not line:
                return
                yield line

    def tell(self):
        return self._pos

    def seek(self, offset, whence=0):
        if whence == 1:
            self._file.seek(self._pos)
        self._file.seek(offset, whence)
        self._pos = self._file.tell()

    def close(self):
        if hasattr(self, '_file'):
            try:
                if hasattr(self._file, 'close'):
                    self._file.close()
            finally:
                del self._file

    def _read(self, size, read_method):
        if size is None:
            size = -1
        self._file.seek(self._pos)
        result = read_method(size)
        self._pos = self._file.tell()
        return result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def readable(self):
        return self._file.readable()

    def writable(self):
        return self._file.writable()

    def seekable(self):
        return self._file.seekable()

    def flush(self):
        return self._file.flush()

    @property
    def closed(self):
        if not hasattr(self, '_file'):
            return True
        else:
            return hasattr(self._file, 'closed') or False
        return self._file.closed


class _PartialFile(_ProxyFile):

    def __init__(self, f, start=None, stop=None):
        _ProxyFile.__init__(self, f, start)
        self._start = start
        self._stop = stop

    def tell(self):
        return _ProxyFile.tell(self) - self._start

    def seek(self, offset, whence=0):
        if whence == 0:
            self._pos = self._start
            whence = 1
        else:
            if whence == 2:
                self._pos = self._stop
                whence = 1
        _ProxyFile.seek(self, offset, whence)

    def _read(self, size, read_method):
        remaining = self._stop - self._pos
        if remaining <= 0:
            return b''
        if size is None or size < 0 or size > remaining:
            size = remaining
        return _ProxyFile._read(self, size, read_method)

    def close(self):
        if hasattr(self, '_file'):
            del self._file


def _lock_file(f, dotlock=True):
    dotlock_done = False
    try:
        if fcntl:
            try:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as e:
                try:
                    if e.errno in (errno.EAGAIN, errno.EACCES, errno.EROFS):
                        raise ExternalClashError('lockf: lock unavailable: %s' % f.name)
                    else:
                        raise
                finally:
                    e = None
                    del e

        if dotlock:
            try:
                pre_lock = _create_temporary(f.name + '.lock')
                pre_lock.close()
            except OSError as e:
                try:
                    if e.errno in (errno.EACCES, errno.EROFS):
                        return
                    raise
                finally:
                    e = None
                    del e

            try:
                try:
                    os.link(pre_lock.name, f.name + '.lock')
                    dotlock_done = True
                except (AttributeError, PermissionError):
                    os.rename(pre_lock.name, f.name + '.lock')
                    dotlock_done = True
                else:
                    os.unlink(pre_lock.name)
            except FileExistsError:
                os.remove(pre_lock.name)
                raise ExternalClashError('dot lock unavailable: %s' % f.name)

    except:
        if fcntl:
            fcntl.lockf(f, fcntl.LOCK_UN)
        if dotlock_done:
            os.remove(f.name + '.lock')
        raise


def _unlock_file(f):
    if fcntl:
        fcntl.lockf(f, fcntl.LOCK_UN)
    if os.path.exists(f.name + '.lock'):
        os.remove(f.name + '.lock')


def _create_carefully(path):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 438)
    try:
        return open(path, 'rb+')
    finally:
        os.close(fd)


def _create_temporary(path):
    return _create_carefully('%s.%s.%s.%s' % (path, int(time.time()),
     socket.gethostname(),
     os.getpid()))


def _sync_flush(f):
    f.flush()
    if hasattr(os, 'fsync'):
        os.fsync(f.fileno())


def _sync_close(f):
    _sync_flush(f)
    f.close()


class Error(Exception):
    pass


class NoSuchMailboxError(Error):
    pass


class NotEmptyError(Error):
    pass


class ExternalClashError(Error):
    pass


class FormatError(Error):
    pass