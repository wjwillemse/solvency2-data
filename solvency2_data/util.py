"""
Common utilities shared across modules
"""
import os
import configparser


def get_config():
    """
    Returns the config file as a dictionary

    Args:
        None

    Returns:
        configuration sections

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


def set_config(new_value: str, existing_key: str = 'data_folder'):
    """
    Exposed via API to allow users to adjust the config without digging into install folder

    Args:
        None

    Returns:
        configuration sections

    """
    config = configparser.ConfigParser()
    fname = "solvency2_data.cfg"
    fpath = os.path.join(os.path.dirname(__file__), fname)
    config.read(fpath)

    if existing_key == 'data_folder':
        for k in config['Directories']:
            # print(k)
            config['Directories'][k] = new_value

    with open(fpath, 'w') as configfile:
        config.write(configfile)
    print('Download paths updated')
    return 0

