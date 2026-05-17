import json
import hashlib
import requests
from datetime import datetime

from nlp_service import analyze_comment
from database import comment_exists
from config_service import load_config


X_RECENT_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"

last_seen_id = None


def hash_author(author_username):
    return hashlib.sha256(author_username.encode("utf-8")).hexdigest()


def is_x_configured():
    config = load_config()
    token = config.get("x_bearer_token", "")

    return (
        token is not None
        and token.strip() != ""
        and "BURAYA" not in token
    )


def create_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def collect_x_posts():
    global last_seen_id

    config = load_config()

    if not is_x_configured():
        print("X Bearer Token bulunamadı. Arayüzden veya .env dosyasından kontrol et.")
        return []

    token = config.get("x_bearer_token", "")
    search_query = config.get("x_search_query", "üniversite lang:tr -is:retweet")

    params = {
        "query": search_query,
        "max_results": 10,
        "sort_order": "recency",
        "tweet.fields": "created_at,author_id,lang,conversation_id,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name"
    }

    if last_seen_id:
        params["since_id"] = last_seen_id

    try:
        response = requests.get(
            X_RECENT_SEARCH_URL,
            headers=create_headers(token),
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            print("X API hata kodu:", response.status_code)
            print("X API cevap:", response.text)
            return []

        data = response.json()

        tweets = data.get("data", [])
        includes = data.get("includes", {})
        users = includes.get("users", [])

        user_map = {}

        for user in users:
            user_map[user["id"]] = user

        meta = data.get("meta", {})
        newest_id = meta.get("newest_id")

        if newest_id:
            last_seen_id = newest_id

        collected_comments = []

        for tweet in tweets:
            tweet_id = tweet.get("id")
            external_id = f"x_{tweet_id}"

            if comment_exists(external_id):
                continue

            text = tweet.get("text", "")
            author_id = tweet.get("author_id", "")

            user = user_map.get(author_id, {})
            username = user.get("username", f"user_{author_id}")

            analysis = analyze_comment(text)

            created_at = tweet.get("created_at", "")
            collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            comment = {
                "platform": "X",
                "external_id": external_id,
                "author_username": username,
                "author_hash": hash_author(username),
                "comment_text": text,
                "sentiment": analysis["sentiment"],
                "risk_level": analysis["risk_level"],
                "risk_score": analysis["risk_score"],
                "tags": json.dumps(analysis["tags"], ensure_ascii=False),
                "source_url": f"https://x.com/{username}/status/{tweet_id}",
                "created_at": created_at,
                "collected_at": collected_at
            }

            collected_comments.append(comment)

        print(f"X API'den {len(collected_comments)} yeni kayıt alındı.")
        return collected_comments

    except Exception as e:
        print("X API bağlantı hatası:", str(e))
        return []