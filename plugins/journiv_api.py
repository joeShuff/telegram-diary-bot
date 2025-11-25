import json

import aiohttp
from datetime import datetime, timezone
from typing import Optional, List, Dict


def format_title_for_today() -> str:
    now = datetime.now()

    day = now.day
    suffix = "th"
    if day % 10 == 1 and day != 11:
        suffix = "st"
    elif day % 10 == 2 and day != 12:
        suffix = "nd"
    elif day % 10 == 3 and day != 13:
        suffix = "rd"

    return now.strftime(f"%A {day}{suffix} %B")


async def upload_journiv_entry(
        base_url: str,
        access_token: str,
        journal_id: str,
        content: str,
        title: Optional[str] = None,
        prompt_id: Optional[str] = None,
        location: Optional[str] = None,
        weather: Optional[str] = None,
) -> dict:
    """
    Upload a journaling entry to Journiv.
    """

    if title is None:
        title = format_title_for_today()

    now = datetime.now()
    now_utc = datetime.now(timezone.utc)

    payload = {
        "title": title,
        "content": content,
        "entry_date": now.strftime("%Y-%m-%d"),
        "entry_datetime_utc": now_utc.isoformat(),
        "entry_timezone": str(now.astimezone().tzinfo),
        "location": location or "",
        "weather": weather or "",
        "journal_id": journal_id,
        "prompt_id": prompt_id,
    }

    url = f"{base_url.rstrip('/')}/api/v1/entries/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise RuntimeError(
                    f"Failed to upload entry: {resp.status} - {text}"
                )
            return await resp.json()


async def load_journals(base_url: str, access_token: str) -> List[Dict]:
    """
    Fetch the list of journals for the current user from Journiv.

    Args:
        base_url (str): Base URL of the server
        access_token (str): Access token to use to load journals

    Returns:
        List[Dict]: List of journal objects, e.g. [{"id": "123", "name": "Work"}, ...]

    Raises:
        RuntimeError: If the request fails or returns unexpected data
    """

    url = f"{base_url.rstrip('/')}/api/v1/journals/?include_archived=false"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 401:
                    raise ValueError("Invalid or expired access token.")
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"Failed to fetch journals: {resp.status}, {text}")

                data = await resp.json()

        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error contacting Journiv: {e}")

    # Ensure data is a list
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response from Journiv API: {data}")

    return data


async def journiv_refresh(base_url: str, refresh_token: str):
    """
    Refresh the access token using the given refresh token.

    Returns:
        {
            "access_token": "...",
            "refresh_token": "..."
        }
    """
    url = f"{base_url.rstrip('/')}/api/v1/auth/refresh"

    payload = {
        "refresh_token": refresh_token
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            # Unauthorized / invalid refresh token
            if resp.status == 401:
                raise ValueError("Refresh token is invalid or expired.")

            if resp.status >= 400:
                text = await resp.text()
                raise RuntimeError(f"Token refresh failed: {resp.status} - {text}")

            data = await resp.json()

    if "access_token" not in data:
        raise RuntimeError(f"Unexpected refresh token response: {data}")

    return data


async def journiv_login(base_url: str, email: str, password: str):
    """
    Attempt to log into Journiv and return tokens.
    Raises ValueError on invalid credentials.
    Raises RuntimeError on unexpected server errors.
    """

    url = f"{base_url.rstrip('/')}/api/v1/auth/login"
    payload = {
        "email": email,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                # If journiv returns 401 / 403 on invalid login:
                if resp.status in (401, 403):
                    raise ValueError("Invalid email or password.")

                if resp.status >= 500:
                    raise RuntimeError("Journiv server error.")

                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(
                        f"Unexpected response from Journiv ({resp.status}): {text}"
                    )

                data = await resp.json()

        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error contacting Journiv: {e}")

    # Validate JSON structure
    if "access_token" not in data or "refresh_token" not in data:
        raise RuntimeError("Journiv login succeeded but tokens are missing.")

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"]
    }


async def upload_media(
    base_url: str,
    access_token: str,
    file_path: str,
    entry_id: Optional[str] = None,
    alt_text: Optional[str] = None
) -> dict:
    """
    Asynchronously upload a media file to Journiv using aiohttp.
    """

    url = f"{base_url.rstrip('/')}/api/v1/media/upload"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    data = {}
    if entry_id is not None:
        data["entry_id"] = entry_id
    if alt_text is not None:
        data["alt_text"] = alt_text

    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field(
                name="file",
                value=f,
                filename=file_path.split("/")[-1],
                content_type="application/octet-stream"
            )
            for k, v in data.items():
                form.add_field(k, v)

            async with session.post(url, headers=headers, data=form) as resp:
                resp.raise_for_status()
                return await resp.json()