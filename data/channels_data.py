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

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_top_5_channels_by_category(category_keyword):
    if not category_keyword:
        raise ValueError("Category keyword is required")
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        channel_url = "https://www.googleapis.com/youtube/v3/channels"
        video_url = "https://www.googleapis.com/youtube/v3/search"

        # Step 1: Search for channels
        search_params = {
            "part": "snippet",
            "q": category_keyword,
            "type": "channel",
            "maxResults": 10,
            "key": YOUTUBE_API_KEY
        }
        search_resp = requests.get(search_url, params=search_params)
        search_data = search_resp.json()
        channel_ids = [item["snippet"]["channelId"] for item in search_data.get("items", [])]
        if not channel_ids:
            return []

        # Step 2: Get channel statistics
        channel_params = {
            "part": "snippet,statistics",
            "id": ",".join(channel_ids),
            "key": YOUTUBE_API_KEY
        }
        channel_resp = requests.get(channel_url, params=channel_params)
        channel_data = channel_resp.json()

        channels = []
        for item in channel_data.get("items", []):
            channel_id = item["id"]
            # Get recent video title
            video_params = {
                "part": "snippet",
                "channelId": channel_id,
                "order": "date",
                "maxResults": 1,
                "type": "video",
                "key": YOUTUBE_API_KEY
            }
            video_resp = requests.get(video_url, params=video_params)
            video_data = video_resp.json()
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
        return top_channels
    except Exception as exc:
        raise RuntimeError("Failed to fetch channel data from YouTube API: " + str(exc))
