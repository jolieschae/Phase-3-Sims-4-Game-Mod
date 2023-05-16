# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\group_anchored.py
# Compiled at: 2018-02-20 14:14:23
# Size of source mod 2**32: 2496 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import flexmethod
from socials.group import SocialGroup
import sims4.log
logger = sims4.log.Logger('Social Group')

class SocialGroupAnchored(SocialGroup):

    @classmethod
    def _get_social_anchor_object(cls, si, target_sim):
        if si.picked_object is None:
            logger.error('{} is being created with no picked object. Are you sure {} was pushed from a picker?', cls, si)
        return si.picked_object

    @classmethod
    def can_get_close_and_wait(cls, sim, target):
        return False

    @flexmethod
    def make_constraint_default(cls, inst, sim, target, position, routing_surface, *, picked_object=None, **kwargs):
        picked_object = inst.anchor if inst is not None else picked_object
        if picked_object is None:
            logger.error('{} is not being provided a picked object in make_constraint_default(). That is not supported.')
        else:
            position = picked_object.position
            routing_surface = picked_object.routing_surface
        return (super(__class__, inst if inst is not None else cls).make_constraint_default)(sim, target, position, routing_surface, picked_object=picked_object, **kwargs)


lock_instance_tunables(SocialGroupAnchored, adjust_sim_positions_dynamically=False,
  social_anchor_object=None)