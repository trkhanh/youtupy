# -*- coding: utf-8 -*-
"""
This module contains a container for stream manifest data.

A container object for the media stream (video only / audio only / video+audio combined).
This was referred t oas ``Video`` in the legacy pytybe version,
but has been renamed to accommodate  (which serves the audio and video separately).
"""
import logging
import os
from datetime import datetime
from typing import BinaryIO
from typing import Dict
from typing import Optional
from typing import Tuple

from urllib.error import HTTPError
from urllib.parse import parse_qs