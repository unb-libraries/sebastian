"""Provides access to the configuration file and its contents."""
from os.path import join as path_join

from .yaml import load_yaml

def get_config_as_dict() -> dict:
    """Gets the configuration file as a dictionary.

    Returns:
        dict: The configuration file as a dictionary.
    """
    return load_yaml("config.yml")

def get_client_user_agent() -> str:
    """Gets the HTTP user agent from the configuration file.

    Returns:
        str: The HTTP user agent.
    """
    return get_config_as_dict()['client']['user_agent']

def get_data_dir() -> str:
    """Gets the data directory from the configuration file.

    Returns:
        str: The data directory.
    """
    return get_config_as_dict()['api']['data_dir']

def get_api_port() -> int:
    """Gets the API port from the configuration file.

    Returns:
        int: The API port.
    """
    return int(get_config_as_dict()['api']['port'])

def get_api_host() -> str:
    """Gets the API hostname from the configuration file.

    Returns:
        str: The API host.
    """
    return get_config_as_dict()['api']['host']

def get_gpu_lockfile() -> str:
    """Gets the GPU lockfile from the configuration file.

    Returns:
        str: The GPU lockfile.
    """
    data_dir = get_data_dir()
    lockfile = get_config_as_dict()['api']['gpu_lock_file']
    return path_join(data_dir, lockfile)

def get_client_uri() -> str:
    """Gets the client URI from the configuration file.

    Returns:
        str: The client URI.
    """
    return get_config_as_dict()['client']['uri']

def get_client_timeout() -> int:
    """Gets the client timeout from the configuration file.

    Returns:
        int: The client timeout.
    """
    return int(get_config_as_dict()['client']['timeout'])

def get_client_keypair() -> tuple:
    """Gets the client keypair from the configuration file.

    Returns:
        tuple: The client keypair.
    """
    return get_config_as_dict()['client']['pub_key'], get_config_as_dict()['client']['priv_key']

def get_api_path() -> str:
    """Gets the API path from the configuration file.

    Returns:
        str: The API path.
    """
    return get_config_as_dict()['api']['path']

def get_huggingface_token() -> str:
    """Gets the Hugging Face token from the configuration file.

    Returns:
        str: The Hugging Face token.
    """
    return get_config_as_dict()['api']['huggingface_token']
