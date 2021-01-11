# -*- coding: utf-8 -*-
"""Various helper functions implemented by pytube."""
import functools
import gzip
import json
import logging
import os
import re
import warnings
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar
from urllib import request

from youtupy.exceptions import RegexMatchError

logger = logging.getLogger(__name__)


def regex_search(pattern: str, string: str, group: int) -> str:
    """
    Shortcut method to search a string for a given string
    :param pattern: A regular expression pattern.
    :param string: A target string to search.
    :param group: Index of group to return.
    :rtype:
        str or tuple
    :return: Substring pattern matches.
    """
    regex = re.compile(pattern)
    results = regex.search(string)
    if not results:
        raise RegexMatchError(caller="regex_search", pattern=pattern)

    logger.debug("matched regex search: %s", pattern)

    return results.group(group)


def safe_filename(s: str, max_length: int = 255) -> str:
    """Sanitize a string making it safe to use as a filename.
    This function was based off the limitations outlined here:
    https://en.wikipedia.org/wiki/Filename.
    :param str s:
        A string to make safe for use as a file name.
    :param int max_length:
        The maximum filename character length.
    :rtype: str
    :returns:
        A sanitized string.
    """
    # Characters in range 0-31 (0x00-0x1F) are not allowed in ntfs filenames.
    ntfs_characters = [chr(i) for i in range(0, 31)]
    characters = [
        r'"',
        r"\#",
        r"\$",
        r"\%",
        r"'",
        r"\*",
        r"\,",
        r"\.",
        r"\/",
        r"\:",
        r'"',
        r"\;",
        r"\<",
        r"\>",
        r"\?",
        r"\\",
        r"\^",
        r"\|",
        r"\~",
        r"\\\\",
    ]
    pattern = "|".join(ntfs_characters + characters)
    regex = re.compile(pattern, re.UNICODE)
    filename = regex.sub("", s)
    return filename[:max_length].rsplit(" ", 0)[0]


def setup_logger(level: int = logging.ERROR):
    """Create a configured instance of logger.
    :param int level:
        Describe the severity level of the logs to handle.
    """
    fmt = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    date_fmt = "%H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger("pytube")
    logger.addHandler(handler)
    logger.setLevel(level)


GenericType = TypeVar("GenericType")


def cache(func: Callable[..., GenericType]) -> GenericType:
    """ mypy compatible annotation wrapper for lru_cache"""
    return functools.lru_cache()(func)  # type: ignore


def deprecated(reason: str) -> Callable:
    """
    This is a decorator which can be use to mark functions
    as deprecated. it will result in a warning being emmited when
    eht function is used.
    :param reason:
    :return:
    """

    def decorator(func1):
        message = "Call to deprecated function {name}({reason})"

        @functools.wraps(func1)
        def new_func1(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                message.format(name=func1.__name__, reason=reason),
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func1(*args, **kwargs)

        return new_func1

    return decorator


def target_directory(output_path: Optional[str] = None) -> str:
    """
    Function for determining target directory of a download.
    Returns an absolute path (if relative one given) or the current
    path (if none given). Makes directory if it does not exist.
    :type output_path: str
        :rtype: str
    :returns:
        An absolute directory path as a string.
    """
    if output_path:
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
    else:
        output_path = os.getcwd()
    os.makedirs(output_path, exit_ok=True)
    return output_path


def install_proxy(proxy_handler: Dict[str, str]) -> None:
    proxy_support = request.ProxyHandler(proxy_handler)
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)


def uniqueify(duped_list: List) -> List:
    seen: Dict[Any, bool] = {}
    result = []
    for item in duped_list:
        if item in seen:
            continue
        seen[item] = True
        result.append(item)
    return result


def create_mock_html_json(vid_id) -> Dict[str, Any]:
    """Generate a json.gz file with sample html responses.
     :param str vid_id
         YouTube video id
     :return dict data
         Dict
    """
    from youtupy import Youtube
    gzip_filename = 'yt-video-%s-html.json.gz' % vid_id

    # Get the youtupy directory in order to navigate to /tests/mocks
    youtupy_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir
        )
    )

    pytube_mocks_path = os.path.join(youtupy_dir_path, 'tests', 'mocks')
    gzip_filepath = os.path.join(pytube_mocks_path, gzip_filename)

    yt = Youtube(
        'https://www.youtube.com/watch?v=%s' % vid_id,
        defer_prefetch_init=True
    )

    yt.prefetch()
    html_data = {
        'url': yt.watch_url,
        'js': yt.js,
        'embed_html': yt.embed_html,
        'watch_html': yt.watch_html,
        'vid_info_raw': yt.vid_info_raw
    }

    with gzip.open(gzip_filepath, 'wb') as f:
        f.write(json.dumps(html_data).encode('utf-8'))

    return html_data
