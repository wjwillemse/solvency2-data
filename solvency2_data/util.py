"""
Common utilities shared across modules
"""

import os
import configparser


def get_config():
    """
    Reads the configuration from the solvency2_data.cfg file.

    Returns:
        dict: A dictionary containing the configuration settings.

    Example:
        >>> get_config()
        {'[Section1]': {'key1': 'value1', 'key2': 'value2'}, '[Section2]': {'key3': 'value3'}}
    """
    # look in current directory for .cfg file
    # if not exists then take the .cfg file in the package directory
    config = configparser.ConfigParser()
    fname = "solvency2_data.cfg"
    if os.path.isfile(fname):
        config.read(fname)
    else:
        config.read(os.path.join(os.path.dirname(__file__), fname))
    return config._sections


def set_config(new_value: str, existing_key: str = "data_folder"):
    """
    Sets a new value for the specified key in the configuration file solvency2_data.cfg.

    Args:
        new_value (str): The new value to set for the specified key.
        existing_key (str): The key whose value needs to be updated. Default is "data_folder".

    Returns:
        int: Returns 0 upon successful completion.

    Example:
        >>> set_config("/new/data/folder", "data_folder")
        Download paths updated
        0
    """
    config = configparser.ConfigParser()
    fname = "solvency2_data.cfg"
    fpath = os.path.join(os.path.dirname(__file__), fname)
    config.read(fpath)

    if existing_key == "data_folder":
        for k in config["Directories"]:
            # print(k)
            config["Directories"][k] = new_value

    with open(fpath, "w") as configfile:
        config.write(configfile)
    print("Download paths updated")
    return 0
