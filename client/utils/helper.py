# Desc: Helper functions
def is_valid_instance(object, class_component_name):
    return (hasattr(object, 'component')
            and object.component == class_component_name)