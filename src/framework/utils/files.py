import pathlib


def get_framework_path() -> pathlib.Path:
    """Get the path of the framework directory.

    Returns:
        str: path of the framework directory.
    """
    return pathlib.Path(__file__).parent.parent.absolute()


def get_framework_data_path() -> pathlib.Path:
    """Get the path of the data directory in the framework.

    Returns:
        str: path of the data directory in the framework.
    """
    return get_framework_path() / "data"
