import inspect

def get_class_location(class_object: type |  object):
    try:
        if not isinstance(class_object, type):
            class_object = type(class_object)

        file = inspect.getfile(class_object)
        class_name = class_object.__name__
    except:
        file = "not found"
        class_name = "not found"

    return {
        "file": file,
        "class_name": class_name
    }
