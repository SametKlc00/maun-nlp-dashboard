import os
import json
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = "data/config.json"

SECRET_FIELDS = {
    "youtube_api_key",
    "x_bearer_token",
    "instagram_access_token"
}


DEFAULT_CONFIG = {
    # =========================
    # GENEL
    # =========================
    "use_fake": False,

    # =========================
    # YOUTUBE
    # =========================
    "use_youtube": True,
    "youtube_api_key": "",
    "youtube_video_ids": "",
    "youtube_poll_seconds": 60,
    "youtube_max_results": 100,

    # YouTube kanalından otomatik video ID çekme
    "youtube_auto_fetch_channel_videos": True,
    "youtube_channel_input": "@maunmedya",
    "youtube_channel_video_limit": 40,

    # =========================
    # X
    # =========================
    "use_x": False,
    "x_bearer_token": "",
    "x_search_query": "(to:musalparslanuni OR @musalparslanuni OR \"Muş Alparslan Üniversitesi\" OR \"Muş Alparslan\" OR MAUN OR MŞÜ) lang:tr is:reply -is:retweet",
    "x_poll_seconds": 60,

    # =========================
    # INSTAGRAM
    # =========================
    "use_instagram": False,
    "instagram_access_token": "",
    "instagram_media_ids": "",
    "instagram_poll_seconds": 60
}


def env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return str(value).lower() == "true"


def safe_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def get_env_default_config():
    config = DEFAULT_CONFIG.copy()

    # =========================
    # GENEL
    # =========================
    config["use_fake"] = env_bool("USE_FAKE", False)

    # =========================
    # YOUTUBE
    # =========================
    config["use_youtube"] = env_bool("USE_YOUTUBE", True)
    config["youtube_api_key"] = os.getenv("YOUTUBE_API_KEY", "")
    config["youtube_video_ids"] = os.getenv("YOUTUBE_VIDEO_IDS", "")
    config["youtube_poll_seconds"] = safe_int(os.getenv("YOUTUBE_POLL_SECONDS", "60"), 60)
    config["youtube_max_results"] = safe_int(os.getenv("YOUTUBE_MAX_RESULTS", "100"), 100)

    config["youtube_auto_fetch_channel_videos"] = env_bool(
        "YOUTUBE_AUTO_FETCH_CHANNEL_VIDEOS",
        True
    )
    config["youtube_channel_input"] = os.getenv("YOUTUBE_CHANNEL_INPUT", "@maunmedya")
    config["youtube_channel_video_limit"] = safe_int(
        os.getenv("YOUTUBE_CHANNEL_VIDEO_LIMIT", "40"),
        40
    )

    # =========================
    # X
    # =========================
    config["use_x"] = env_bool("USE_X", False)
    config["x_bearer_token"] = os.getenv("X_BEARER_TOKEN", "")
    config["x_search_query"] = os.getenv(
        "X_SEARCH_QUERY",
        DEFAULT_CONFIG["x_search_query"]
    )
    config["x_poll_seconds"] = safe_int(os.getenv("X_POLL_SECONDS", "60"), 60)

    # =========================
    # INSTAGRAM
    # =========================
    config["use_instagram"] = env_bool("USE_INSTAGRAM", False)
    config["instagram_access_token"] = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    config["instagram_media_ids"] = os.getenv("INSTAGRAM_MEDIA_IDS", "")
    config["instagram_poll_seconds"] = safe_int(
        os.getenv("INSTAGRAM_POLL_SECONDS", "60"),
        60
    )

    return config


def normalize_config(config):
    normalized = DEFAULT_CONFIG.copy()

    for key, value in config.items():
        if key in DEFAULT_CONFIG:
            normalized[key] = value

    bool_fields = [
        "use_fake",
        "use_youtube",
        "use_x",
        "use_instagram",
        "youtube_auto_fetch_channel_videos"
    ]

    int_fields = [
        "youtube_poll_seconds",
        "youtube_max_results",
        "youtube_channel_video_limit",
        "x_poll_seconds",
        "instagram_poll_seconds"
    ]

    for field in bool_fields:
        value = normalized.get(field, DEFAULT_CONFIG[field])

        if isinstance(value, str):
            normalized[field] = value.lower() == "true"
        else:
            normalized[field] = bool(value)

    for field in int_fields:
        normalized[field] = safe_int(
            normalized.get(field, DEFAULT_CONFIG[field]),
            DEFAULT_CONFIG[field]
        )

    # =========================
    # SINIRLAMALAR
    # =========================

    if normalized["youtube_poll_seconds"] < 5:
        normalized["youtube_poll_seconds"] = 5

    if normalized["youtube_max_results"] < 1:
        normalized["youtube_max_results"] = 1

    if normalized["youtube_max_results"] > 100:
        normalized["youtube_max_results"] = 100

    if normalized["youtube_channel_video_limit"] < 1:
        normalized["youtube_channel_video_limit"] = 1

    if normalized["youtube_channel_video_limit"] > 50:
        normalized["youtube_channel_video_limit"] = 50

    if normalized["x_poll_seconds"] < 5:
        normalized["x_poll_seconds"] = 5

    if normalized["instagram_poll_seconds"] < 5:
        normalized["instagram_poll_seconds"] = 5

    return normalized


def load_config():
    os.makedirs("data", exist_ok=True)

    config = get_env_default_config()

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                saved_config = json.load(file)

            if isinstance(saved_config, dict):
                config.update(saved_config)

        except Exception as e:
            print("Config dosyası okunurken hata oluştu:", str(e))

    return normalize_config(config)


def write_config(config):
    os.makedirs("data", exist_ok=True)

    clean_config = normalize_config(config)

    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(clean_config, file, ensure_ascii=False, indent=4)


def save_config(new_config):
    current_config = load_config()

    for key, value in new_config.items():
        if key not in DEFAULT_CONFIG:
            continue

        if key in SECRET_FIELDS:
            if value is None or str(value).strip() == "":
                continue

        current_config[key] = value

    current_config = normalize_config(current_config)
    write_config(current_config)

    return get_public_config(current_config)


def is_secret_configured(value):
    return (
        value is not None
        and str(value).strip() != ""
        and "BURAYA" not in str(value)
    )


def get_public_config(config=None):
    if config is None:
        config = load_config()

    public_config = normalize_config(config)

    public_config["youtube_configured"] = is_secret_configured(
        config.get("youtube_api_key", "")
    )
    public_config["x_configured"] = is_secret_configured(
        config.get("x_bearer_token", "")
    )
    public_config["instagram_configured"] = is_secret_configured(
        config.get("instagram_access_token", "")
    )

    public_config["youtube_api_key"] = ""
    public_config["x_bearer_token"] = ""
    public_config["instagram_access_token"] = ""

    return public_config