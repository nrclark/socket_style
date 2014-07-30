"""Utility package containing multicast and point-to-point clients and
servers."""

__author__ = 'Nick Clark'
__version__ = '0.1'

from socketstyle_common import TimeoutError

from multicast import MulticastServer
from multicast import MulticastClient

from point_to_point import PointToPointServer
from point_to_point import PointToPointClient

__all__ = ['TimeoutError']
__all__ += ['MulticastServer', 'MulticastClient']
__all__ += ['PointToPointServer', 'PointToPointClient']
