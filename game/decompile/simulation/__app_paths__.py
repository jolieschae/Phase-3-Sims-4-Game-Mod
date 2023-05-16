# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\__app_paths__.py
# Compiled at: 2014-07-09 18:52:13
# Size of source mod 2**32: 1085 bytes
import os

def configure_app_paths(pathroot, from_archive, user_script_roots, layers):
    if not from_archive:
        server_path = os.path.join(pathroot, 'Scripts', 'Server')
    else:
        server_path = os.path.join(pathroot, 'Gameplay', 'simulation.zip')
    user_script_roots.append(server_path)
    layers.append(server_path)