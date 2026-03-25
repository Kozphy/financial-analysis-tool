from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .io import ensure_parent_directory


LOGGER = logging.getLogger(__name__)


def request_text(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
    retries: int = 2,
    backoff_seconds: float = 0.5,
    cache_dir: Path | None = None,
    cache_namespace: str,
    error_cls: type[Exception],
    source_label: str,
) -> str:
    cache_path = _build_cache_path(
        cache_dir,
        cache_namespace=cache_namespace,
        request_fingerprint=_fingerprint_request(url, method=method, data=data),
    )
    if cache_path is not None and cache_path.exists():
        LOGGER.debug("cache_hit source=%s path=%s", source_label, cache_path)
        return cache_path.read_text(encoding="utf-8")

    request = Request(url, data=data, headers=headers or {}, method=method)
    attempts = max(retries, 0) + 1
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8", errors="replace")
            if cache_path is not None:
                ensure_parent_directory(cache_path)
                cache_path.write_text(payload, encoding="utf-8")
            return payload
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = error_cls(
                f"{source_label} request failed with HTTP {exc.code}: {body}"
            )
        except URLError as exc:
            last_error = error_cls(f"Unable to reach {source_label}: {exc.reason}")

        if attempt >= attempts:
            break

        delay = backoff_seconds * (2 ** (attempt - 1))
        LOGGER.warning(
            "request_retry source=%s attempt=%s/%s delay_seconds=%.2f url=%s",
            source_label,
            attempt,
            attempts,
            delay,
            url,
        )
        time.sleep(delay)

    assert last_error is not None
    raise last_error


def request_json(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
    retries: int = 2,
    backoff_seconds: float = 0.5,
    cache_dir: Path | None = None,
    cache_namespace: str,
    error_cls: type[Exception],
    source_label: str,
) -> object:
    raw_text = request_text(
        url,
        method=method,
        data=data,
        headers=headers,
        timeout=timeout,
        retries=retries,
        backoff_seconds=backoff_seconds,
        cache_dir=cache_dir,
        cache_namespace=cache_namespace,
        error_cls=error_cls,
        source_label=source_label,
    )
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise error_cls(f"{source_label} returned invalid JSON.") from exc


def _build_cache_path(
    cache_dir: Path | None,
    *,
    cache_namespace: str,
    request_fingerprint: str,
) -> Path | None:
    if cache_dir is None:
        return None
    return Path(cache_dir) / cache_namespace / f"{request_fingerprint}.cache"


def _fingerprint_request(
    url: str,
    *,
    method: str,
    data: bytes | None,
) -> str:
    payload = {
        "url": url,
        "method": method,
        "data": data.decode("utf-8", errors="replace") if data is not None else None,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
