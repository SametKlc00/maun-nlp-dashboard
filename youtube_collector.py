import json
import hashlib
import time
from datetime import datetime
from urllib.parse import quote, urlparse

import requests

from nlp_service import analyze_comment
from database import comment_exists
from config_service import load_config


YOUTUBE_COMMENT_THREADS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"
YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
YOUTUBE_PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

# Kanal video ID listesini her döngüde tekrar çekip kotayı tüketmemek için basit cache
_channel_video_cache = {
    "cache_key": "",
    "timestamp": 0,
    "video_ids": []
}


def is_youtube_configured():
    config = load_config()
    api_key = config.get("youtube_api_key", "")

    return (
        api_key is not None
        and api_key.strip() != ""
        and "BURAYA" not in api_key
    )


def hash_author(author_name):
    return hashlib.sha256(author_name.encode("utf-8")).hexdigest()


def normalize_channel_input(channel_input):
    value = str(channel_input or "").strip()

    if value == "":
        return ""

    if "youtube.com" in value:
        parsed = urlparse(value)
        path = parsed.path.strip("/")

        if path.startswith("channel/"):
            return path.replace("channel/", "").strip()

        parts = path.split("/")

        for part in parts:
            if part.startswith("@"):
                return part.strip()

        return path

    return value


def get_manual_video_ids(config):
    video_ids_text = config.get("youtube_video_ids", "")

    if not video_ids_text:
        return []

    return [
        video_id.strip()
        for video_id in video_ids_text.split(",")
        if video_id.strip() != ""
    ]


def request_youtube_channels(api_key, params):
    try:
        response = requests.get(
            YOUTUBE_CHANNELS_URL,
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            print("YouTube channels.list hata kodu:", response.status_code)
            print("YouTube channels.list cevap:", response.text)
            return None

        return response.json()

    except Exception as e:
        print("YouTube kanal bilgisi alınırken bağlantı hatası:", str(e))
        return None


def get_uploads_playlist_id(api_key, channel_input):
    channel_input = normalize_channel_input(channel_input)

    if channel_input == "":
        print("YouTube kanal bilgisi boş.")
        return ""

    # Direkt UC... kanal ID verilmişse
    if channel_input.startswith("UC"):
        params = {
            "part": "contentDetails,snippet",
            "id": channel_input,
            "key": api_key
        }

        data = request_youtube_channels(api_key, params)

    else:
        # @maunmedya veya maunmedya handle desteği
        handle_value = channel_input[1:] if channel_input.startswith("@") else channel_input

        params = {
            "part": "contentDetails,snippet",
            "forHandle": handle_value,
            "key": api_key
        }

        data = request_youtube_channels(api_key, params)

    if not data:
        return ""

    items = data.get("items", [])

    if len(items) == 0:
        print("YouTube kanalı bulunamadı:", channel_input)
        print("Not: @handle veya UC ile başlayan kanal ID kullan.")
        return ""

    channel = items[0]
    snippet = channel.get("snippet", {})
    channel_title = snippet.get("title", "Bilinmeyen Kanal")

    content_details = channel.get("contentDetails", {})
    related_playlists = content_details.get("relatedPlaylists", {})
    uploads_playlist_id = related_playlists.get("uploads", "")

    if uploads_playlist_id == "":
        print("Uploads playlist ID alınamadı.")
        return ""

    print(f"YouTube kanalı bulundu: {channel_title}")
    print(f"Uploads playlist ID: {uploads_playlist_id}")

    return uploads_playlist_id


def fetch_channel_videos(api_key, channel_input, limit=40):
    limit = int(limit or 40)

    if limit < 1:
        limit = 1

    if limit > 50:
        limit = 50

    uploads_playlist_id = get_uploads_playlist_id(api_key, channel_input)

    if uploads_playlist_id == "":
        return []

    videos = []
    next_page_token = None

    try:
        while len(videos) < limit:
            remaining = limit - len(videos)

            params = {
                "part": "snippet,contentDetails",
                "playlistId": uploads_playlist_id,
                "key": api_key,
                "maxResults": min(50, remaining)
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            response = requests.get(
                YOUTUBE_PLAYLIST_ITEMS_URL,
                params=params,
                timeout=20
            )

            if response.status_code != 200:
                print("YouTube playlistItems.list hata kodu:", response.status_code)
                print("YouTube playlistItems.list cevap:", response.text)
                break

            data = response.json()
            items = data.get("items", [])

            for item in items:
                content_details = item.get("contentDetails", {})
                snippet = item.get("snippet", {})

                video_id = content_details.get("videoId", "")

                if not video_id:
                    continue

                videos.append({
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "published_at": content_details.get("videoPublishedAt", "")
                })

                if len(videos) >= limit:
                    break

            next_page_token = data.get("nextPageToken")

            if not next_page_token:
                break

        print(f"YouTube kanalından {len(videos)} video ID çekildi.")
        return videos

    except Exception as e:
        print("YouTube kanal video listesi alınırken hata:", str(e))
        return []


def fetch_channel_video_ids(api_key, channel_input, limit=40):
    cache_key = f"{channel_input}_{limit}"
    now = time.time()

    # 10 dakika cache
    if (
        _channel_video_cache["cache_key"] == cache_key
        and now - _channel_video_cache["timestamp"] < 600
        and len(_channel_video_cache["video_ids"]) > 0
    ):
        print("YouTube kanal video ID listesi cache üzerinden kullanıldı.")
        return _channel_video_cache["video_ids"]

    videos = fetch_channel_videos(
        api_key=api_key,
        channel_input=channel_input,
        limit=limit
    )

    video_ids = [video["video_id"] for video in videos]

    _channel_video_cache["cache_key"] = cache_key
    _channel_video_cache["timestamp"] = now
    _channel_video_cache["video_ids"] = video_ids

    return video_ids


def get_effective_video_ids(config):
    manual_video_ids = get_manual_video_ids(config)

    use_auto_channel = config.get("youtube_auto_fetch_channel_videos", False)

    if not use_auto_channel:
        return manual_video_ids

    api_key = config.get("youtube_api_key", "")
    channel_input = config.get("youtube_channel_input", "@maunmedya")
    limit = int(config.get("youtube_channel_video_limit", 40))

    auto_video_ids = fetch_channel_video_ids(
        api_key=api_key,
        channel_input=channel_input,
        limit=limit
    )

    merged = []

    for video_id in manual_video_ids + auto_video_ids:
        if video_id not in merged:
            merged.append(video_id)

    return merged


def collect_youtube_comments():
    config = load_config()

    if not is_youtube_configured():
        print("YouTube API Key bulunamadı. Arayüzden veya .env dosyasından kontrol et.")
        return []

    api_key = config.get("youtube_api_key", "")
    video_ids = get_effective_video_ids(config)
    max_results = int(config.get("youtube_max_results", 100))

    if max_results < 1:
        max_results = 1

    if max_results > 100:
        max_results = 100

    if len(video_ids) == 0:
        print("YouTube video ID listesi boş.")
        return []

    all_collected_comments = []

    for video_id in video_ids:
        comments = collect_comments_for_video(
            video_id=video_id,
            api_key=api_key,
            max_results=max_results
        )

        all_collected_comments.extend(comments)

    print(f"YouTube API'den toplam {len(all_collected_comments)} yeni yorum alındı.")
    return all_collected_comments


def parse_youtube_error(response):
    try:
        error_data = response.json()
        error = error_data.get("error", {})
        errors = error.get("errors", [])

        reason = ""
        message = error.get("message", "")

        if len(errors) > 0:
            reason = errors[0].get("reason", "")

        return reason, message

    except Exception:
        return "", response.text


def collect_comments_for_video(video_id, api_key, max_results):
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": api_key,
        "maxResults": max_results,
        "order": "time",
        "textFormat": "plainText"
    }

    try:
        response = requests.get(
            YOUTUBE_COMMENT_THREADS_URL,
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            error_reason, error_message = parse_youtube_error(response)

            if error_reason == "commentsDisabled":
                print(f"Video ID {video_id} için yorumlar kapalı. Bu video atlandı.")
                return []

            if error_reason == "videoNotFound":
                print(f"Video ID {video_id} bulunamadı. Bu video atlandı.")
                return []

            if error_reason == "quotaExceeded":
                print("YouTube API kota limiti dolmuş olabilir.")
                print("YouTube API cevap:", error_message)
                return []

            if error_reason == "forbidden":
                print(f"Video ID {video_id} için yorumlara erişim izni yok. Bu video atlandı.")
                return []

            print("YouTube API hata kodu:", response.status_code)
            print("YouTube API hata sebebi:", error_reason)
            print("YouTube API cevap:", error_message)
            return []

        data = response.json()
        items = data.get("items", [])

        collected_comments = []

        for item in items:
            snippet = item.get("snippet", {})
            top_comment = snippet.get("topLevelComment", {})
            top_comment_snippet = top_comment.get("snippet", {})

            comment_id = top_comment.get("id", "")
            external_id = f"youtube_{video_id}_{comment_id}"

            if not comment_id:
                continue

            if comment_exists(external_id):
                continue

            comment_text = top_comment_snippet.get("textOriginal", "")

            if not comment_text:
                comment_text = top_comment_snippet.get("textDisplay", "")

            if not comment_text:
                continue

            author_name = top_comment_snippet.get("authorDisplayName", "unknown_user")
            published_at = top_comment_snippet.get("publishedAt", "")

            analysis = analyze_comment(comment_text)

            collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encoded_comment_id = quote(comment_id, safe="")

            comment = {
                "platform": "YouTube",
                "external_id": external_id,
                "author_username": author_name,
                "author_hash": hash_author(author_name),
                "comment_text": comment_text,
                "sentiment": analysis["sentiment"],
                "risk_level": analysis["risk_level"],
                "risk_score": analysis["risk_score"],
                "tags": json.dumps(analysis["tags"], ensure_ascii=False),
                "source_url": f"https://www.youtube.com/watch?v={video_id}&lc={encoded_comment_id}",
                "created_at": published_at,
                "collected_at": collected_at
            }

            collected_comments.append(comment)

        print(f"Video ID {video_id} için {len(collected_comments)} yeni yorum alındı.")
        return collected_comments

    except Exception as e:
        print(f"Video ID {video_id} için YouTube API bağlantı hatası:", str(e))
        return []