try:
    from modules import errors
    from modules import locals
    from modules import progressbar
    from modules import sorting
    from modules import consts

except (ImportError, ModuleNotFoundError):
    from .modules import errors
    from .modules import locals
    from .modules import progressbar
    from .modules import sorting
    from .modules import consts
