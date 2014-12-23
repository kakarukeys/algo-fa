import logging
import requests


logger = logging.getLogger(__name__)

def lenient_get(url):
    """ Sends GET request to <url> and returns the response text if okay, returns blank string otherwise. """
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return ''
    else:
        if r.status_code == 200:
            return r.text
        else:
            logger.warning("GET {0} {1} {2}".format(r.url, r.status_code, r.reason))
            return ''
