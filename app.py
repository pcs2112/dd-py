import sys
import importlib
from src.utils import close_db_connections


arg_count = len(sys.argv)


def main(args):
	if len(args) == 1:
		print("Please enter a command.")
		exit()

	try:
		module = importlib.import_module('src.commands')
		cmd = getattr(module, args[1])
	except AttributeError:
		print(f"\"{args[1]}\" is an invalid command.")
		exit()
		
	try:
		if len(args) > 2:
			cmd(*args[2:len(args)])
		else:
			cmd()
		close_db_connections()
	except KeyboardInterrupt as e:
		close_db_connections()
	except Exception as e:
		close_db_connections()
		raise e
	

if __name__ == '__main__':
	main(sys.argv)
