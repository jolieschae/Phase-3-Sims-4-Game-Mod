# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\keyword.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 2341 bytes
__all__ = [
 'iskeyword', 'kwlist']
kwlist = [
 "'False'", 
 "'None'", 
 "'True'", 
 "'and'", 
 "'as'", 
 "'assert'", 
 "'async'", 
 "'await'", 
 "'break'", 
 "'class'", 
 "'continue'", 
 "'def'", 
 "'del'", 
 "'elif'", 
 "'else'", 
 "'except'", 
 "'finally'", 
 "'for'", 
 "'from'", 
 "'global'", 
 "'if'", 
 "'import'", 
 "'in'", 
 "'is'", 
 "'lambda'", 
 "'nonlocal'", 
 "'not'", 
 "'or'", 
 "'pass'", 
 "'raise'", 
 "'return'", 
 "'try'", 
 "'while'", 
 "'with'", 
 "'yield'"]
iskeyword = frozenset(kwlist).__contains__

def main():
    import sys, re
    args = sys.argv[1:]
    iptfile = args and args[0] or 'Python/graminit.c'
    if len(args) > 1:
        optfile = args[1]
    else:
        optfile = 'Lib/keyword.py'
    with open(optfile, newline='') as (fp):
        format = fp.readlines()
    nl = format[0][len(format[0].strip()):] if format else '\n'
    with open(iptfile) as (fp):
        strprog = re.compile('"([^"]+)"')
        lines = []
        for line in fp:
            if '{1, "' in line:
                match = strprog.search(line)
                if match:
                    lines.append("        '" + match.group(1) + "'," + nl)

    lines.sort()
    try:
        start = format.index('#--start keywords--' + nl) + 1
        end = format.index('#--end keywords--' + nl)
        format[start:end] = lines
    except ValueError:
        sys.stderr.write('target does not contain format markers\n')
        sys.exit(1)

    with open(optfile, 'w', newline='') as (fp):
        fp.writelines(format)


if __name__ == '__main__':
    main()