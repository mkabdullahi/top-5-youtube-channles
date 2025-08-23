def generate_dummy_data(category):
    return [
        {
            "name": f"{category} Channel {i+1}",
            "thumbnail": f"https://dummyimage.com/120x90/000/fff&text={category}+{i+1}",
            "subscribers": f"{((i+1)*0.2):.1f}M",
            "recent_video": f"Latest {category} Video {i+1}"
        } for i in range(5)
    ]



import requests
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
from pathlib import Path
import json
import time

# Simple file cache directory (project root/.cache)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / '.cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
# TTL in seconds (default 1 hour)
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Standardized message for quota fallback
QUOTA_EXCEEDED_MSG = "Quota exceeded — using offline/demo data"

# Common YouTube Data API endpoints
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
VIDEO_SEARCH_URL = SEARCH_URL

# In-memory cache: { category: { 'ts': int, 'channels': [...] } }
_memory_cache = {}
from threading import Lock
_cache_lock = Lock()

def get_top_5_channels_by_category(category_keyword):
    """Return (channels_list, error_message).
    If error_message is None the call succeeded.
    """
    if not category_keyword:
        return [], "Category keyword is required"
    # check in-memory cache first
    with _cache_lock:
        mem = _memory_cache.get(category_keyword)
        if mem and (time.time() - mem['ts']) <= CACHE_TTL:
            return mem['channels'], None

    try:
        search_url = SEARCH_URL
        channel_url = CHANNELS_URL
        video_url = VIDEO_SEARCH_URL

        # Step 1: Search for channels
        # Only request the minimal fields we need from search.list to reduce payload
        search_params = {
            "part": "snippet",
            "q": category_keyword,
            "type": "channel",
            "maxResults": 10,
            # request only the id.channelId and the snippet thumbnails/title
            "fields": "items(id/channelId,snippet/title,snippet/thumbnails/default)",
            "key": YOUTUBE_API_KEY
        }
        search_resp = requests.get(search_url, params=search_params, timeout=10)
        try:
            search_data = search_resp.json()
        except Exception:
            search_data = None

        # Handle API error payloads; treat 403 (quota) specially so we can show cached/dummy data
        if search_resp.status_code != 200:
            logger.error('YouTube search API returned %s: %s', search_resp.status_code, search_resp.text)
            if search_resp.status_code == 403:
                # quota exceeded: try file cache then fallback to dummy
                cached = _load_cache(category_keyword)
                if cached:
                    age = int(time.time() - cached['ts'])
                    return cached['channels'], f"Quota exceeded — showing cached results ({age}s old)"
                return generate_dummy_data(category_keyword), "Quota exceeded — using offline/demo data"
            raise RuntimeError(f"YouTube search API error: status={search_resp.status_code}")
        if search_data and 'error' in search_data:
            logger.error('YouTube search API error payload: %s', search_data)
            err = search_data.get('error')
            # if API reports quota problems inside the payload
            if isinstance(err, dict) and err.get('code') == 403:
                cached = _load_cache(category_keyword)
                if cached:
                    age = int(time.time() - cached['ts'])
                    return cached['channels'], f"Quota exceeded — showing cached results ({age}s old)"
                return generate_dummy_data(category_keyword), QUOTA_EXCEEDED_MSG
            raise RuntimeError(f"YouTube search API error: {err}")

        # channelId for search results is in item['id']['channelId'] when type=channel
        channel_ids = [item.get('id', {}).get('channelId') for item in search_data.get("items", [])]
        # filter out any None values
        channel_ids = [cid for cid in channel_ids if cid]
        if not channel_ids:
            # no ids found — fallback to dummy data
            return generate_dummy_data(category_keyword), "No channels found; using dummy data"

        # Step 2: Get channel statistics
        # Limit the fields returned from channels.list to only what we need
        channel_params = {
            "part": "snippet,statistics",
            "id": ",".join(channel_ids),
            # request only title, thumbnails and subscriberCount
            "fields": "items(id,snippet(title,thumbnails/default,description),statistics/subscriberCount)",
            "key": YOUTUBE_API_KEY
        }
        channel_resp = requests.get(channel_url, params=channel_params, timeout=10)
        try:
            channel_data = channel_resp.json()
        except Exception:
            channel_data = None

        if channel_resp.status_code != 200:
            logger.error('YouTube channels API returned %s: %s', channel_resp.status_code, channel_resp.text)
            if channel_resp.status_code == 403:
                cached = _load_cache(category_keyword)
                if cached:
                    age = int(time.time() - cached['ts'])
                    return cached['channels'], f"Quota exceeded — showing cached results ({age}s old)"
                return generate_dummy_data(category_keyword), QUOTA_EXCEEDED_MSG
            raise RuntimeError(f"YouTube channels API error: status={channel_resp.status_code}")
        if channel_data and 'error' in channel_data:
            logger.error('YouTube channels API error payload: %s', channel_data)
            err = channel_data.get('error')
            if isinstance(err, dict) and err.get('code') == 403:
                cached = _load_cache(category_keyword)
                if cached:
                    age = int(time.time() - cached['ts'])
                    return cached['channels'], f"Quota exceeded — showing cached results ({age}s old)"
                return generate_dummy_data(category_keyword), QUOTA_EXCEEDED_MSG
            raise RuntimeError(f"YouTube channels API error: {err}")

        channels = []
        for item in channel_data.get("items", []):
            channel_id = item["id"]
            # Get recent video title
            # Fetch only the most recent video title; limit returned fields
            video_params = {
                "part": "snippet",
                "channelId": channel_id,
                "order": "date",
                "maxResults": 1,
                "type": "video",
                "fields": "items(snippet/title)",
                "key": YOUTUBE_API_KEY
            }
            video_resp = requests.get(video_url, params=video_params, timeout=10)
            try:
                video_data = video_resp.json()
            except Exception:
                video_data = None
            recent_video_title = ""
            if video_data.get("items"):
                recent_video_title = video_data["items"][0]["snippet"]["title"]

            channels.append({
                "name": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                "subscribers": int(item["statistics"].get("subscriberCount", 0)),
                "channel_id": channel_id,
                "recent_video_title": recent_video_title
            })

    # Step 3: Sort and return top 5
        top_channels = sorted(channels, key=lambda x: x["subscribers"], reverse=True)[:5]
        try:
            _save_cache(category_keyword, top_channels)
        except Exception:
            logger.exception('Failed to save cache')
        # update in-memory cache
        with _cache_lock:
            _memory_cache[category_keyword] = {'ts': int(time.time()), 'channels': top_channels}
        return top_channels, None
    except Exception as exc:
        # If quota exceeded, try to return cached results
        msg = str(exc)
        logger.exception('Failed to fetch channels: %s', msg)
        if 'quota' in msg.lower() or '403' in msg:
            # attempt to load cache
            cached = _load_cache(category_keyword)
            if cached:
                age = int(time.time() - cached['ts'])
                return cached['channels'], f"Quota exceeded — showing cached results ({age}s old)"
            return generate_dummy_data(category_keyword), "Quota exceeded — using offline/demo data"
        # no cache or other error -> fallback to dummy data for demo
        return generate_dummy_data(category_keyword), f"Failed to fetch channel data from YouTube API: {exc}; using dummy data"


def _cache_path(category_keyword: str) -> Path:
    safe = category_keyword.replace('/', '_')
    return CACHE_DIR / f"channels_{safe}.json"


def _save_cache(category_keyword: str, channels: list):
    path = _cache_path(category_keyword)
    payload = {'ts': int(time.time()), 'channels': channels}
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
    except Exception:
        logger.exception('Failed to write cache %s', path)


def _load_cache(category_keyword: str):
    path = _cache_path(category_keyword)
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        # check TTL
        if int(time.time()) - int(payload.get('ts', 0)) > CACHE_TTL:
            return None
        return payload
    except Exception:
        logger.exception('Failed to load cache %s', path)
        return None


def get_top_5_channels_broad(category_keyword, max_search_results=50):
    """
    Do a single (larger) search.list for the category_keyword (up to max_search_results),
    then call channels.list once to get snippet,statistics and topicDetails.
    Filter channels that mention the category_keyword in title/description or keep all if none match.
    Returns (channels, error)
    """
    if not category_keyword:
        return [], "Category keyword is required"

    # check in-memory cache first
    cache_key = f"broad::{category_keyword}::{max_search_results}"
    with _cache_lock:
        mem = _memory_cache.get(cache_key)
        if mem and (time.time() - mem['ts']) <= CACHE_TTL:
            return mem['channels'], None

    search_url = "https://www.googleapis.com/youtube/v3/search"
    channel_url = "https://www.googleapis.com/youtube/v3/channels"
    search_params = {
        'part': 'snippet',
        'q': category_keyword,
        'type': 'channel',
        'maxResults': max_search_results,
        'key': YOUTUBE_API_KEY
    }
    try:
        r = requests.get(search_url, params=search_params, timeout=10)
        if r.status_code != 200:
            logger.error('search failed %s: %s', r.status_code, r.text)
            return [], f"YouTube search API error: status={r.status_code}"
        data = r.json()
        ids = [it.get('id', {}).get('channelId') for it in data.get('items', [])]
        ids = [i for i in ids if i]
        if not ids:
            return [], None

        # call channels.list once
        parts = 'snippet,statistics,topicDetails'
        # use fields to limit payload
        fields = 'items(id,snippet(title,thumbnails/default,description),statistics/subscriberCount,topicDetails/topicIds)'
        ch_params = {
            'part': parts,
            'id': ','.join(ids),
            'fields': fields,
            'key': YOUTUBE_API_KEY
        }
        ch_r = requests.get(channel_url, params=ch_params, timeout=10)
        if ch_r.status_code != 200:
            logger.error('channels.list failed %s: %s', ch_r.status_code, ch_r.text)
            return [], f"YouTube channels API error: status={ch_r.status_code}"
        ch_data = ch_r.json()

        channels = []
        keyword = category_keyword.lower()
        matched = []
        for item in ch_data.get('items', []):
            sub = int(item.get('statistics', {}).get('subscriberCount', 0))
            title = item.get('snippet', {}).get('title', '')
            desc = item.get('snippet', {}).get('description', '') or ''
            thumb = item.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url', '')
            cid = item.get('id')
            entry = {
                'name': title,
                'thumbnail': thumb,
                'subscribers': sub,
                'channel_id': cid,
                'recent_video_title': ''
            }
            channels.append(entry)
            # basic filtering
            if keyword in title.lower() or keyword in desc.lower():
                matched.append(entry)

        use_list = matched if matched else channels
        top = sorted(use_list, key=lambda x: x['subscribers'], reverse=True)[:5]

        # cache results
        try:
            _save_cache(category_keyword, top)
        except Exception:
            logger.exception('Failed to save cache')
        with _cache_lock:
            _memory_cache[cache_key] = {'ts': int(time.time()), 'channels': top}

        return top, None
    except Exception as exc:
        logger.exception('Broad search failed')
        # fallback to file cache
        cached = _load_cache(category_keyword)
        if cached:
            age = int(time.time() - cached['ts'])
            return cached['channels'], f"Error fetching fresh data — showing cached results ({age}s old)"
        return [], f"Failed to fetch channel data: {exc}"


def batch_search_and_get_channels(categories):
    """
    Optional: batch multiple search.list calls using google-api-python-client.
    Returns a dict: { category: [channels...] } or None if the google client is not available.

    Notes:
    - This reduces HTTP overhead but does not reduce YouTube quota costs.
    - Requires `google-api-python-client` to be installed. If it's not installed the function returns None.
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except Exception:
        logger.debug('googleapiclient not available; skipping batch helper')
        return None

    if not YOUTUBE_API_KEY:
        logger.error('YOUTUBE_API_KEY not set; cannot use google client')
        return None

    service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    responses = {}

    def _callback(request_id, response, exception):
        if exception:
            responses[request_id] = {'error': str(exception)}
        else:
            responses[request_id] = response

    batch = service.new_batch_http_request(callback=_callback)
    for cat in categories:
        req = service.search().list(part='snippet', q=cat, type='channel', maxResults=10)
        batch.add(req, request_id=cat)

    try:
        batch.execute()
    except HttpError as he:
        logger.exception('Batch execute failed: %s', he)
        return None

    # collect unique channel ids
    cat_to_ids = {}
    all_ids = set()
    for cat, payload in responses.items():
        ids = []
        if payload and isinstance(payload, dict) and payload.get('items'):
            for it in payload.get('items', []):
                cid = it.get('id', {}).get('channelId')
                if cid:
                    ids.append(cid)
                    all_ids.add(cid)
        cat_to_ids[cat] = ids

    if not all_ids:
        return {cat: [] for cat in categories}

    # get channel details in one call
    try:
        channel_resp = service.channels().list(part='snippet,statistics', id=','.join(list(all_ids)), maxResults=50).execute()
    except HttpError as he:
        logger.exception('channels.list failed: %s', he)
        return None

    id_to_channel = {item['id']: item for item in channel_resp.get('items', [])}

    result = {}
    for cat, ids in cat_to_ids.items():
        channels = []
        for cid in ids:
            item = id_to_channel.get(cid)
            if not item:
                continue
            channels.append({
                'name': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'subscribers': int(item.get('statistics', {}).get('subscriberCount', 0)),
                'channel_id': cid,
                'recent_video_title': ''  # optional: fetch via extra call per channel
            })
        # sort and take top 5
        result[cat] = sorted(channels, key=lambda x: x['subscribers'], reverse=True)[:5]

    return result
