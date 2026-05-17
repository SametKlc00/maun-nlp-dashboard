import os
import json
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

from nlp_service import analyze_comment
from database import comment_exists
from config_service import load_config

load_dotenv()

INSTAGRAM_API_VERSION = os.getenv("INSTAGRAM_API_VERSION", "v21.0")
INSTAGRAM_COMMENTS_LIMIT = int(os.getenv("INSTAGRAM_COMMENTS_LIMIT", "50"))
INSTAGRAM_MEDIA_LIMIT = int(os.getenv("INSTAGRAM_MEDIA_LIMIT", "10"))

GRAPH_BASE_URL = f"https://graph.facebook.com/{INSTAGRAM_API_VERSION}"


def get_access_token(config):
    token = config.get("instagram_access_token", "")

    if token and str(token).strip() != "":
        return token.strip()

    return os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()


def get_media_ids(config):
    media_ids_text = config.get("instagram_media_ids", "")

    if not media_ids_text:
        media_ids_text = os.getenv("INSTAGRAM_MEDIA_IDS", "")

    return [
        media_id.strip()
        for media_id in media_ids_text.split(",")
        if media_id.strip() != "" and "BURAYA" not in media_id
    ]


def get_ig_user_id():
    return os.getenv("INSTAGRAM_IG_USER_ID", "").strip()


def is_instagram_configured():
    config = load_config()
    token = get_access_token(config)
    media_ids = get_media_ids(config)
    ig_user_id = get_ig_user_id()

    has_token = (
        token is not None
        and token.strip() != ""
        and "BURAYA" not in token
    )

    has_media_source = len(media_ids) > 0 or ig_user_id != ""

    return has_token and has_media_source


def hash_author(author_username):
    return hashlib.sha256(author_username.encode("utf-8")).hexdigest()


def fetch_recent_media_ids(access_token, ig_user_id):
    if not ig_user_id:
        return []

    url = f"{GRAPH_BASE_URL}/{ig_user_id}/media"

    params = {
        "access_token": access_token,
        "fields": "id,caption,timestamp,permalink,media_type",
        "limit": INSTAGRAM_MEDIA_LIMIT
    }

    try:
        response = requests.get(url, params=params, timeout=20)

        if response.status_code != 200:
            print("Instagram media listesi hata kodu:", response.status_code)
            print("Instagram media listesi cevap:", response.text)
            return []

        data = response.json()
        items = data.get("data", [])

        media_ids = []

        for item in items:
            media_id = item.get("id")
            if media_id:
                media_ids.append(media_id)

        print(f"Instagram IG User ID {ig_user_id} için {len(media_ids)} media ID alındı.")
        return media_ids

    except Exception as e:
        print("Instagram media listesi bağlantı hatası:", str(e))
        return []


def fetch_media_permalink(media_id, access_token):
    url = f"{GRAPH_BASE_URL}/{media_id}"

    params = {
        "access_token": access_token,
        "fields": "permalink"
    }

    try:
        response = requests.get(url, params=params, timeout=20)

        if response.status_code != 200:
            return ""

        data = response.json()
        return data.get("permalink", "")

    except Exception:
        return ""


def collect_instagram_comments():
    config = load_config()
    access_token = get_access_token(config)

    if not access_token or "BURAYA" in access_token:
        print("Instagram Access Token bulunamadı. Arayüzden veya .env dosyasından kontrol et.")
        return []

    media_ids = get_media_ids(config)

    if len(media_ids) == 0:
        ig_user_id = get_ig_user_id()
        media_ids = fetch_recent_media_ids(access_token, ig_user_id)

    if len(media_ids) == 0:
        print("Instagram Media ID listesi boş. Arayüzden Media ID gir veya .env içine INSTAGRAM_IG_USER_ID ekle.")
        return []

    all_comments = []

    for media_id in media_ids:
        comments = collect_comments_for_media(
            media_id=media_id,
            access_token=access_token
        )

        all_comments.extend(comments)

    print(f"Instagram API'den toplam {len(all_comments)} yeni yorum alındı.")
    return all_comments


def collect_comments_for_media(media_id, access_token):
    url = f"{GRAPH_BASE_URL}/{media_id}/comments"

    params = {
        "access_token": access_token,
        "fields": "id,text,username,timestamp,like_count",
        "limit": INSTAGRAM_COMMENTS_LIMIT
    }

    try:
        response = requests.get(url, params=params, timeout=20)

        if response.status_code != 200:
            print("Instagram API hata kodu:", response.status_code)
            print("Instagram API cevap:", response.text)
            return []

        data = response.json()
        items = data.get("data", [])
        media_permalink = fetch_media_permalink(media_id, access_token)

        collected_comments = []

        for item in items:
            comment_id = item.get("id", "")
            external_id = f"instagram_{media_id}_{comment_id}"

            if not comment_id:
                continue

            if comment_exists(external_id):
                continue

            comment_text = item.get("text", "")
            author_username = item.get("username", "instagram_user")
            created_at = item.get("timestamp", "")

            analysis = analyze_comment(comment_text)

            collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            comment = {
                "platform": "Instagram",
                "external_id": external_id,
                "author_username": author_username,
                "author_hash": hash_author(author_username),
                "comment_text": comment_text,
                "sentiment": analysis["sentiment"],
                "risk_level": analysis["risk_level"],
                "risk_score": analysis["risk_score"],
                "tags": json.dumps(analysis["tags"], ensure_ascii=False),
                "source_url": media_permalink,
                "created_at": created_at,
                "collected_at": collected_at
            }

            collected_comments.append(comment)

        print(f"Instagram Media ID {media_id} için {len(collected_comments)} yeni yorum alındı.")
        return collected_comments

    except Exception as e:
        print("Instagram yorum bağlantı hatası:", str(e))
        return []