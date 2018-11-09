# -*- coding: utf-8 -*-

"""
███████╗ ██████╗  ██████╗██╗  ██╗███████╗███████╗    ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗
██╔════╝██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝
███████╗██║   ██║██║     █████╔╝ ███████╗███████╗    ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝
╚════██║██║   ██║██║     ██╔═██╗ ╚════██║╚════██║    ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝
███████║╚██████╔╝╚██████╗██║  ██╗███████║███████║    ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║
╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝

A flexible, asynchronous SOCKS 4/4A/5/5H proxy server written in pure Python

Copyright (c) 2018 UltrafunkAmsterdam <https://github.com/UltrafunkAmsterdam>

"""

__author__ = "UltrafunkAmsterdam"
__copyright__ = "Copyright (C) 2018 %s" % __author__
__license__ = "MIT"
__version__ = "1.0"
__description__ = 'A flexible, asynchronous SOCKS 4/4A/5/5H proxy server written in pure Python'

__all__ = ['run_proxy','log', 'Socks4', 'Socks5']

from ._util import log
from ._socks4 import Socks4
from ._socks5 import Socks5
from ._util import run_proxy
