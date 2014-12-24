import logging

import requests

from fa.miner.exceptions import GetError


logger = logging.getLogger(__name__)

def strict_get(url):
    """ Sends GET request to <url> and returns the response text if okay, raises GetError otherwise. """
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        raise GetError() from e
    else:
        if r.status_code == 200:
            return r.text
        else:
            logger.error("GET {0} {1} {2}".format(r.url, r.status_code, r.reason))
            raise GetError()
