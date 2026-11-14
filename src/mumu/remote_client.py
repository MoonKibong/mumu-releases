"""Authenticated Streamable HTTP client for the hosted mumu service."""

import asyncio
import json
import os
from typing import Any

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

API_KEY_ENV_VAR = "MUMU_API_KEY"


class RemoteClientError(Exception):
    """A remote tool call could not be completed."""


def _require_api_key() -> str:
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        raise RemoteClientError(f"{API_KEY_ENV_VAR} environment variable is required")
    return api_key


async def _call_tool_async(server_url: str, api_key: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    mcp_url = server_url.rstrip("/") + "/mcp"
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {api_key}"}) as http_client:
        async with streamable_http_client(mcp_url, http_client=http_client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                if result.is_error:
                    raise RemoteClientError(result.content[0].text if result.content else "remote tool error")
                return json.loads(result.content[0].text)


def call_remote_tool(server_url: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call one tool on a remote mumu server. Synchronous wrapper for CLI use."""
    api_key = _require_api_key()
    try:
        return asyncio.run(_call_tool_async(server_url, api_key, tool_name, arguments))
    except (httpx2.HTTPError, OSError, ExceptionGroup) as error:
        message = _connection_error(error)
        if message is None:
            raise
        raise RemoteClientError(message) from None


def _connection_error(error: Exception) -> str | None:
    errors = []
    pending = [error]
    while pending:
        current = pending.pop()
        if isinstance(current, ExceptionGroup):
            pending.extend(current.exceptions)
        elif isinstance(current, (httpx2.HTTPError, OSError)):
            errors.append(current)
        else:
            return None
    statuses = {getattr(getattr(item, "response", None), "status_code", None) for item in errors}
    if 401 in statuses:
        return "Authentication failed (401). Re-enter the session key privately and retry."
    if 429 in statuses:
        return "Quota exceeded (429). Wait for the supplied reset time before retrying."
    if 400 in statuses or 421 in statuses:
        return "Host rejected. Compare the base URL with the URL supplied privately by your administrator."
    if any(isinstance(item, (httpx2.TimeoutException, TimeoutError)) for item in errors):
        return "Connection timed out. Check approved network access and retry once."
    return "Connection failed. Check the private base URL and network access; contact your administrator if it persists."
