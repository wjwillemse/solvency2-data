"""
Common utilities shared across modules
"""
import os
import configparser


def get_config():
    """ Returns the config file as a dictionary """
    # look in current directory for .cfg file
    # if not exists then take the .cfg file in the package directory
    config = configparser.RawConfigParser()
    fname = 'solvency2_data.cfg'
    if os.path.isfile(fname):
        config.read(fname)
    else:
        config.read(os.path.join(os.path.dirname(__file__), fname))
    return config._sections


def set_config(existing_key, new_value):
    """
    Exposed via API to allow users to adjust the config without digging into install folder
    """
    # TODO: Implement set_config

