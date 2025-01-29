try:
    from clishelf.cli import main
except ModuleNotFoundError:
    import os
    import sys

    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    sys.path.insert(0, parent_dir_path)

    from clishelf.cli import main


if __name__ == "__main__":
    main()
