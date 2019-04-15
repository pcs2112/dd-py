import sys
import importlib
from src.db import close_db_connections

arg_count = len(sys.argv)


def _exit(_exit=True):
    close_db_connections()
    if _exit:
        exit()


def main(args):
    if len(args) == 1:
        print("Please enter a command.")
        _exit()

    cmd = None
    
    try:
        module = importlib.import_module('src.commands')
        cmd = getattr(module, args[1])
    except AttributeError:
        print(f"\"{args[1]}\" is an invalid command.")
        _exit()
    
    try:
        if len(args) > 2:
            cmd(*args[2:len(args)])
        else:
            cmd()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        _exit(False)
        raise e
    
    _exit()


if __name__ == '__main__':
    main(sys.argv)
