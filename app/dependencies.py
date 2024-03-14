from app import get_logger


def inject_logger(name):
    """
    Logger object, can be injected directly to router methods.
    """
    return get_logger(name=name)
