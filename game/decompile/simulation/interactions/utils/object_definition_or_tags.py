# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\object_definition_or_tags.py
# Compiled at: 2015-05-06 17:55:56
# Size of source mod 2**32: 5198 bytes
from sims4.tuning.tunable import AutoFactoryInit, TunableVariant, TunableList, TunableReference, TunableEnumEntry, TunableSet, HasTunableSingletonFactory
import services, tag
OBJECT_DEFINITION_FILTER = 0
OBJECT_TAG_FILTER = 1

class TunableObjectFilter(HasTunableSingletonFactory, AutoFactoryInit):

    def get_filter_type(self):
        raise NotImplementedError

    def _intersect_similar(self, other):
        raise NotImplementedError

    def _intersect_dissimilar(self, other):
        raise NotImplementedError

    def matches(self, obj):
        raise NotImplementedError

    def intersect(self, other):
        if self.get_filter_type() == other.get_filter_type():
            return self._intersect_similar(other)
        return self._intersect_dissimilar(other)

    @staticmethod
    def intersect_definitions_with_flags(definitions, tags):
        intersected_items = []
        for definition in definitions:
            for tag in tags:
                if definition.has_build_buy_tag(tag):
                    intersected_items.append(definition)
                    break

        return intersected_items


class ObjectDefinitionsFilter(TunableObjectFilter):
    FACTORY_TUNABLES = {'items_to_check': TunableList(description='\n             A List of the definitions that can be matched to fulfill the filter.\n             This list is considered a Match Any requirement.\n             ',
                         tunable=TunableReference(description='\n                 A reference to a definiton that can be matched as part of the \n                 filter.\n                 ',
                         manager=(services.definition_manager())))}

    def get_filter_type(self):
        return OBJECT_DEFINITION_FILTER

    def get_item_set(self):
        return set(self.items_to_check)

    def _intersect_similar(self, other):
        return ObjectDefinitionsFilter(items_to_check=(self.get_item_set().intersection(other.get_item_set())))

    def _intersect_dissimilar(self, other):
        new_set = self.intersect_definitions_with_flags(self.items_to_check, other.tag_set)
        return ObjectDefinitionsFilter(items_to_check=new_set)

    def matches(self, obj):
        return obj.definition in self.items_to_check


class ObjectTagsFilter(TunableObjectFilter):
    FACTORY_TUNABLES = {'tag_set': TunableSet(description='\n            A Set of tags that can be matched to fulfill the filter. The set\n            is considered a Match Any requirement.\n            ',
                  tunable=TunableEnumEntry(description='\n                A reference to a tag that can be matched as part of the filter.\n                ',
                  tunable_type=(tag.Tag),
                  default=(tag.Tag.INVALID)))}

    def get_filter_type(self):
        return OBJECT_TAG_FILTER

    def get_item_set(self):
        return self.tag_set

    def _intersect_similar(self, other):
        return ObjectTagsFilter(tag_set=(self.get_item_set().intersection(other.get_item_set())))

    def _intersect_dissimilar(self, other):
        new_set = self.intersect_definitions_with_flags(other.items_to_check, self.tag_set)
        return ObjectDefinitionsFilter(items_to_check=new_set)

    def matches(self, obj):
        return any([obj.definition.has_build_buy_tag(tag) for tag in self.tag_set])


class ObjectDefinitonsOrTagsVariant(TunableVariant):
    __slots__ = ()

    def __init__(self, **kwargs):
        (super().__init__)(object_definitions=ObjectDefinitionsFilter.TunableFactory(), 
         object_tags=ObjectTagsFilter.TunableFactory(), 
         default='object_tags', **kwargs)