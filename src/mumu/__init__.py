"""Thin remote client for the hosted mumu service."""

from mumu.remote_client import RemoteClientError, call_remote_tool

__version__ = "0.1.0"
__all__ = [
    "RemoteClientError",
    "call_remote_tool",
]
