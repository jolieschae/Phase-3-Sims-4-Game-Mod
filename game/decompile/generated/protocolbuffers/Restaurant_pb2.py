# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: /Users/sims4builder/build/Beta/_deploy/Client/MacRelease/The Sims 4.app/Contents/Python/Generated/protocolbuffers/Restaurant_pb2.py
# Compiled at: 2023-04-20 22:46:30
# Size of source mod 2**32: 17682 bytes
from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
import protocolbuffers.Venue_pb2 as Venue_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Restaurant.proto',
  package='EA.Sims4.Network',
  serialized_pb='\n\x10Restaurant.proto\x12\x10EA.Sims4.Network\x1a\x0bVenue.proto"\x96\x01\n\nRecipeItem\x12\x11\n\trecipe_id\x18\x01 \x02(\x04\x128\n\titem_type\x18\x02 \x01(\x0e2%.EA.Sims4.Network.RecipeItem.ItemType\x12\x16\n\x0eprice_override\x18\x03 \x01(\x05"#\n\x08ItemType\x12\n\n\x06NORMAL\x10\x00\x12\x0b\n\x07SPECIAL\x10\x01"I\n\x06Course\x12+\n\x05items\x18\x01 \x03(\x0b2\x1c.EA.Sims4.Network.RecipeItem\x12\x12\n\ncourse_tag\x18\x02 \x01(\r"1\n\x04Menu\x12)\n\x07courses\x18\x01 \x03(\x0b2\x18.EA.Sims4.Network.Course"i\n\tSimOrders\x12.\n\nsim_orders\x18\x01 \x03(\x0b2\x1a.EA.Sims4.Network.SimOrder\x12\x11\n\tmeal_cost\x18\x02 \x01(\r\x12\x19\n\x11is_recommendation\x18\x03 \x01(\x08"Q\n\x08SimOrder\x12\x0e\n\x06sim_id\x18\x01 \x02(\x04\x12\x11\n\trecipe_id\x18\x02 \x01(\x04\x12\x0e\n\x06locked\x18\x03 \x01(\x08\x12\x12\n\ncourse_tag\x18\x04 \x01(\r"¾\x01\n\x08ShowMenu\x12$\n\x04menu\x18\x01 \x02(\x0b2\x16.EA.Sims4.Network.Menu\x12.\n\nsim_orders\x18\x02 \x03(\x0b2\x1a.EA.Sims4.Network.SimOrder\x12\x13\n\x07sim_ids\x18\x03 \x03(\x04B\x02\x10\x01\x12\x12\n\nchef_order\x18\x04 \x01(\x08\x12\x1a\n\x12running_bill_total\x18\x05 \x01(\r\x12\x17\n\x0frecommend_order\x18\x06 \x01(\x08"7\n\x05Order\x12.\n\nsim_orders\x18\x01 \x03(\x0b2\x1a.EA.Sims4.Network.SimOrder"\x99\x02\n\x17RestaurantConfiguration\x12\x11\n\tattire_id\x18\x01 \x01(\r\x12\x11\n\tpreset_id\x18\x02 \x01(\x04\x12+\n\x0bcustom_menu\x18\x03 \x01(\x0b2\x16.EA.Sims4.Network.Menu\x12/\n\x07outfits\x18\x04 \x03(\x0b2\x1e.EA.Sims4.Network.CareerOutfit"z\n\x14RestaurantOutfitType\x12\r\n\tMALE_CHEF\x10\x00\x12\x0f\n\x0bFEMALE_CHEF\x10\x01\x12\x0f\n\x0bMALE_WAITER\x10\x02\x12\x11\n\rFEMALE_WAITER\x10\x03\x12\r\n\tMALE_HOST\x10\x04\x12\x0f\n\x0bFEMALE_HOST\x10\x05')
_RECIPEITEM_ITEMTYPE = descriptor.EnumDescriptor(name='ItemType',
  full_name='EA.Sims4.Network.RecipeItem.ItemType',
  filename=None,
  file=DESCRIPTOR,
  values=[
 descriptor.EnumValueDescriptor(name='NORMAL',
   index=0,
   number=0,
   options=None,
   type=None),
 descriptor.EnumValueDescriptor(name='SPECIAL',
   index=1,
   number=1,
   options=None,
   type=None)],
  containing_type=None,
  options=None,
  serialized_start=167,
  serialized_end=202)
_RESTAURANTCONFIGURATION_RESTAURANTOUTFITTYPE = descriptor.EnumDescriptor(name='RestaurantOutfitType',
  full_name='EA.Sims4.Network.RestaurantConfiguration.RestaurantOutfitType',
  filename=None,
  file=DESCRIPTOR,
  values=[
 descriptor.EnumValueDescriptor(name='MALE_CHEF',
   index=0,
   number=0,
   options=None,
   type=None),
 descriptor.EnumValueDescriptor(name='FEMALE_CHEF',
   index=1,
   number=1,
   options=None,
   type=None),
 descriptor.EnumValueDescriptor(name='MALE_WAITER',
   index=2,
   number=2,
   options=None,
   type=None),
 descriptor.EnumValueDescriptor(name='FEMALE_WAITER',
   index=3,
   number=3,
   options=None,
   type=None),
 descriptor.EnumValueDescriptor(name='MALE_HOST',
   index=4,
   number=4,
   options=None,
   type=None),
 descriptor.EnumValueDescriptor(name='FEMALE_HOST',
   index=5,
   number=5,
   options=None,
   type=None)],
  containing_type=None,
  options=None,
  serialized_start=930,
  serialized_end=1052)
_RECIPEITEM = descriptor.Descriptor(name='RecipeItem',
  full_name='EA.Sims4.Network.RecipeItem',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='recipe_id',
   full_name='EA.Sims4.Network.RecipeItem.recipe_id',
   index=0,
   number=1,
   type=4,
   cpp_type=4,
   label=2,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='item_type',
   full_name='EA.Sims4.Network.RecipeItem.item_type',
   index=1,
   number=2,
   type=14,
   cpp_type=8,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='price_override',
   full_name='EA.Sims4.Network.RecipeItem.price_override',
   index=2,
   number=3,
   type=5,
   cpp_type=1,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[
 _RECIPEITEM_ITEMTYPE],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=52,
  serialized_end=202)
_COURSE = descriptor.Descriptor(name='Course',
  full_name='EA.Sims4.Network.Course',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='items',
   full_name='EA.Sims4.Network.Course.items',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='course_tag',
   full_name='EA.Sims4.Network.Course.course_tag',
   index=1,
   number=2,
   type=13,
   cpp_type=3,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=204,
  serialized_end=277)
_MENU = descriptor.Descriptor(name='Menu',
  full_name='EA.Sims4.Network.Menu',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='courses',
   full_name='EA.Sims4.Network.Menu.courses',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=279,
  serialized_end=328)
_SIMORDERS = descriptor.Descriptor(name='SimOrders',
  full_name='EA.Sims4.Network.SimOrders',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='sim_orders',
   full_name='EA.Sims4.Network.SimOrders.sim_orders',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='meal_cost',
   full_name='EA.Sims4.Network.SimOrders.meal_cost',
   index=1,
   number=2,
   type=13,
   cpp_type=3,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='is_recommendation',
   full_name='EA.Sims4.Network.SimOrders.is_recommendation',
   index=2,
   number=3,
   type=8,
   cpp_type=7,
   label=1,
   has_default_value=False,
   default_value=False,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=330,
  serialized_end=435)
_SIMORDER = descriptor.Descriptor(name='SimOrder',
  full_name='EA.Sims4.Network.SimOrder',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='sim_id',
   full_name='EA.Sims4.Network.SimOrder.sim_id',
   index=0,
   number=1,
   type=4,
   cpp_type=4,
   label=2,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='recipe_id',
   full_name='EA.Sims4.Network.SimOrder.recipe_id',
   index=1,
   number=2,
   type=4,
   cpp_type=4,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='locked',
   full_name='EA.Sims4.Network.SimOrder.locked',
   index=2,
   number=3,
   type=8,
   cpp_type=7,
   label=1,
   has_default_value=False,
   default_value=False,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='course_tag',
   full_name='EA.Sims4.Network.SimOrder.course_tag',
   index=3,
   number=4,
   type=13,
   cpp_type=3,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=437,
  serialized_end=518)
_SHOWMENU = descriptor.Descriptor(name='ShowMenu',
  full_name='EA.Sims4.Network.ShowMenu',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='menu',
   full_name='EA.Sims4.Network.ShowMenu.menu',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=2,
   has_default_value=False,
   default_value=None,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='sim_orders',
   full_name='EA.Sims4.Network.ShowMenu.sim_orders',
   index=1,
   number=2,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='sim_ids',
   full_name='EA.Sims4.Network.ShowMenu.sim_ids',
   index=2,
   number=3,
   type=4,
   cpp_type=4,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=(descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01'))),
 descriptor.FieldDescriptor(name='chef_order',
   full_name='EA.Sims4.Network.ShowMenu.chef_order',
   index=3,
   number=4,
   type=8,
   cpp_type=7,
   label=1,
   has_default_value=False,
   default_value=False,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='running_bill_total',
   full_name='EA.Sims4.Network.ShowMenu.running_bill_total',
   index=4,
   number=5,
   type=13,
   cpp_type=3,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='recommend_order',
   full_name='EA.Sims4.Network.ShowMenu.recommend_order',
   index=5,
   number=6,
   type=8,
   cpp_type=7,
   label=1,
   has_default_value=False,
   default_value=False,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=521,
  serialized_end=711)
_ORDER = descriptor.Descriptor(name='Order',
  full_name='EA.Sims4.Network.Order',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='sim_orders',
   full_name='EA.Sims4.Network.Order.sim_orders',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=713,
  serialized_end=768)
_RESTAURANTCONFIGURATION = descriptor.Descriptor(name='RestaurantConfiguration',
  full_name='EA.Sims4.Network.RestaurantConfiguration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='attire_id',
   full_name='EA.Sims4.Network.RestaurantConfiguration.attire_id',
   index=0,
   number=1,
   type=13,
   cpp_type=3,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='preset_id',
   full_name='EA.Sims4.Network.RestaurantConfiguration.preset_id',
   index=1,
   number=2,
   type=4,
   cpp_type=4,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='custom_menu',
   full_name='EA.Sims4.Network.RestaurantConfiguration.custom_menu',
   index=2,
   number=3,
   type=11,
   cpp_type=10,
   label=1,
   has_default_value=False,
   default_value=None,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='outfits',
   full_name='EA.Sims4.Network.RestaurantConfiguration.outfits',
   index=3,
   number=4,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[
 _RESTAURANTCONFIGURATION_RESTAURANTOUTFITTYPE],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=771,
  serialized_end=1052)
_RECIPEITEM.fields_by_name['item_type'].enum_type = _RECIPEITEM_ITEMTYPE
_RECIPEITEM_ITEMTYPE.containing_type = _RECIPEITEM
_COURSE.fields_by_name['items'].message_type = _RECIPEITEM
_MENU.fields_by_name['courses'].message_type = _COURSE
_SIMORDERS.fields_by_name['sim_orders'].message_type = _SIMORDER
_SHOWMENU.fields_by_name['menu'].message_type = _MENU
_SHOWMENU.fields_by_name['sim_orders'].message_type = _SIMORDER
_ORDER.fields_by_name['sim_orders'].message_type = _SIMORDER
_RESTAURANTCONFIGURATION.fields_by_name['custom_menu'].message_type = _MENU
_RESTAURANTCONFIGURATION.fields_by_name['outfits'].message_type = Venue_pb2._CAREEROUTFIT
_RESTAURANTCONFIGURATION_RESTAURANTOUTFITTYPE.containing_type = _RESTAURANTCONFIGURATION
DESCRIPTOR.message_types_by_name['RecipeItem'] = _RECIPEITEM
DESCRIPTOR.message_types_by_name['Course'] = _COURSE
DESCRIPTOR.message_types_by_name['Menu'] = _MENU
DESCRIPTOR.message_types_by_name['SimOrders'] = _SIMORDERS
DESCRIPTOR.message_types_by_name['SimOrder'] = _SIMORDER
DESCRIPTOR.message_types_by_name['ShowMenu'] = _SHOWMENU
DESCRIPTOR.message_types_by_name['Order'] = _ORDER
DESCRIPTOR.message_types_by_name['RestaurantConfiguration'] = _RESTAURANTCONFIGURATION

class RecipeItem(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _RECIPEITEM


class Course(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _COURSE


class Menu(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _MENU


class SimOrders(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SIMORDERS


class SimOrder(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SIMORDER


class ShowMenu(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SHOWMENU


class Order(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _ORDER


class RestaurantConfiguration(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _RESTAURANTCONFIGURATION