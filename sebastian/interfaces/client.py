"""Provides a sample command to transcribe an audio file."""
import os
import sys

import requests
from logging import Logger

from sebastian.core.config import get_client_uri, get_client_timeout, get_client_keypair, get_client_user_agent
from sebastian.core import get_logger
from sebastian.interfaces.api import check_api_server_exit
from sebastian.core import json_dumper

CMD_STRING = 'transcribe'

def transcribe(args: list=sys.argv) -> None:
    """Transcribes the provided audio file.

    Args:
        args (list, optional): The arguments for the summary. Defaults to sys.argv.
    """
    log = get_logger()
    check_api_server_exit(log)
    validate_args(args, log)

    uri = get_client_uri()
    log.info("Querying %s...", uri)

    keypair = get_client_keypair()

    headers = {
        "x-pub-key": keypair[0],
        "x-api-key": keypair[1],
        'Accept':'application/json'
    }

    file_path = args[1]
    file_name = os.path.basename(file_path)

    with open(file_path, 'rb') as file:
        files = {
            'file': (file_name, file)
        }

        data = {
            "client": get_client_user_agent()
        }

        r = requests.post(
            uri,
            files=files,
            headers=headers,
            timeout=get_client_timeout()
        )

        if r.status_code != 200:
            log.error("Failed to transcribe document:")
            log.error(r.text)
            sys.exit(1)

        print(
            json_dumper(r.json())
        )

def validate_args(args: list, log: Logger) -> None:
    """Validates the arguments for the command and exits if invalid.

    Args:
        args (list): The arguments to validate.
        log (Logger): The logger to use.
    """
    if len(args) < 1:
        log_usage(log)
        sys.exit(1)

    try:
        if args[1] == "":
            raise ValueError
    except Exception:
        log.warning("File Path cannot be empty")
        log_usage(log)
        sys.exit(1)
    
    # does the file exist at the provided path?
    if not os.path.exists(args[1]):
        log.warning("File does not exist")
        log_usage(log)
        sys.exit(1)

def log_usage(log: Logger) -> None:
    """Outputs the usage for the command.

    Args:
        log (Logger): The logger to use.
    """
    log.warning("Usage: poetry run %s <filepath>", CMD_STRING)
