def with_context(handler_func, context):
    def wrapper(message):
        return handler_func(message, context)
    return wrapper

def with_callback_context(handler_func, context):
    def wrapper(call):
        return handler_func(call, context)
    return wrapper
