from functools import wraps
import services
import sims4.resources
from sims4.tuning.instance_manager import InstanceManager
from sims4.resources import Types

def inject(target_function, new_function):
    @wraps(target_function)
    def _inject(*args, **kwargs):
        return new_function(target_function, *args, **kwargs)
    return _inject

def inject_to(target_object, target_function_name):
    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function
    return _inject_to

phase-3_test_ObjectIds_Phone = (14965,)
phase-3_test_InteractionIds_Phone = (2631691969,)
@inject_to(InstanceManager, 'load_data_into_class_instances')
def phase-3_test_AddSuperAffordances_Phone(original, self):
    original(self)
    if self.TYPE == Types.OBJECT:
        affordance_manager = services.affordance_manager()
        sa_list = []
        for sa_id in phase-3_test_InteractionIds_Phone:
            key = sims4.resources.get_resource_key(sa_id, Types.INTERACTION)
            sa_tuning = affordance_manager.get(key)
            if not sa_tuning is None:
                sa_list.append(sa_tuning)
        sa_tuple = tuple(sa_list)
        for obj_id in phase-3_test_ObjectIds_Phone:
            key = sims4.resources.get_resource_key(obj_id, Types.OBJECT)
            obj_tuning = self._tuned_classes.get(key)
            if not obj_tuning is None:
                obj_tuning._phone_affordances = obj_tuning._phone_affordances + sa_tuple

