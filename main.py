import asyncio

from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import (
    create_tables,
    insert_comment,
    get_all_comments,
    get_risky_comments,
    get_stats,
    clear_comments,
    get_analysis_summary,
    get_tag_stats,
    get_risk_stats,
    get_user_risk_stats,
    get_word_stats,
    get_spam_analysis
)

from fake_stream import generate_fake_comment

from x_collector import collect_x_posts, is_x_configured

from youtube_collector import (
    collect_youtube_comments,
    is_youtube_configured,
    fetch_channel_videos
)

from instagram_collector import (
    collect_instagram_comments,
    is_instagram_configured
)

from config_service import load_config, save_config


app = FastAPI(
    title="Sosyal Medya Risk Dashboard",
    description="YouTube / X / Instagram yorumları için NLP tabanlı duygu ve risk analiz sistemi",
    version="1.0.0"
)


app.mount("/static", StaticFiles(directory="static"), name="static")


stream_running = True


@app.on_event("startup")
async def startup_event():
    create_tables()

    print("Sistem başlatıldı.")
    print("Ayarlar data/config.json ve .env üzerinden okunuyor.")

    asyncio.create_task(fake_comment_stream())
    asyncio.create_task(x_comment_stream())
    asyncio.create_task(youtube_comment_stream())
    asyncio.create_task(instagram_comment_stream())


async def fake_comment_stream():
    while stream_running:
        config = load_config()

        if config.get("use_fake", False):
            comment = generate_fake_comment()
            insert_comment(comment)
            await asyncio.sleep(4)
        else:
            await asyncio.sleep(2)


async def x_comment_stream():
    while stream_running:
        config = load_config()

        if config.get("use_x", False):
            comments = collect_x_posts()

            for comment in comments:
                insert_comment(comment)

            await asyncio.sleep(int(config.get("x_poll_seconds", 60)))
        else:
            await asyncio.sleep(2)


async def youtube_comment_stream():
    while stream_running:
        config = load_config()

        if config.get("use_youtube", False):
            comments = collect_youtube_comments()

            for comment in comments:
                insert_comment(comment)

            await asyncio.sleep(int(config.get("youtube_poll_seconds", 60)))
        else:
            await asyncio.sleep(2)


async def instagram_comment_stream():
    while stream_running:
        config = load_config()

        if config.get("use_instagram", False):
            comments = collect_instagram_comments()

            for comment in comments:
                insert_comment(comment)

            await asyncio.sleep(int(config.get("instagram_poll_seconds", 60)))
        else:
            await asyncio.sleep(2)


@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api/spam-analysis")
def api_spam_analysis():
    return get_spam_analysis(limit=10)

@app.get("/api/comments")
def api_comments():
    return get_all_comments(limit=500)

@app.get("/api/risky-comments")
def api_risky_comments():
    return get_risky_comments(limit=50)


@app.get("/api/stats")
def api_stats():
    return get_stats()


@app.get("/api/analysis-summary")
def api_analysis_summary():
    return get_analysis_summary()


@app.get("/api/tag-stats")
def api_tag_stats():
    return get_tag_stats(limit=12)


@app.get("/api/risk-stats")
def api_risk_stats():
    return get_risk_stats()


@app.get("/api/user-risk-stats")
def api_user_risk_stats():
    return get_user_risk_stats(limit=10)


@app.get("/api/word-stats")
def api_word_stats():
    return get_word_stats(limit=30)


@app.get("/api/youtube-channel-videos")
def api_youtube_channel_videos():
    config = load_config()

    api_key = config.get("youtube_api_key", "")
    channel_input = config.get("youtube_channel_input", "@maunmedya")
    limit = int(config.get("youtube_channel_video_limit", 40))

    if not is_youtube_configured():
        return {
            "success": False,
            "message": "YouTube API Key bulunamadı.",
            "videos": [],
            "video_ids": ""
        }

    videos = fetch_channel_videos(
        api_key=api_key,
        channel_input=channel_input,
        limit=limit
    )

    video_ids = ",".join([video["video_id"] for video in videos])

    return {
        "success": True,
        "message": f"{len(videos)} video ID çekildi.",
        "videos": videos,
        "video_ids": video_ids
    }


@app.get("/api/source-status")
def api_source_status():
    config = load_config()

    return {
        "use_fake": config.get("use_fake", False),

        "use_youtube": config.get("use_youtube", False),
        "youtube_configured": is_youtube_configured(),
        "youtube_poll_seconds": config.get("youtube_poll_seconds", 60),

        "use_x": config.get("use_x", False),
        "x_configured": is_x_configured(),
        "x_poll_seconds": config.get("x_poll_seconds", 60),

        "use_instagram": config.get("use_instagram", False),
        "instagram_configured": is_instagram_configured(),
        "instagram_poll_seconds": config.get("instagram_poll_seconds", 60)
    }


@app.get("/api/config")
def api_get_config():
    config = load_config()

    public_config = config.copy()

    public_config["youtube_api_key"] = ""
    public_config["x_bearer_token"] = ""
    public_config["instagram_access_token"] = ""

    public_config["youtube_configured"] = is_youtube_configured()
    public_config["x_configured"] = is_x_configured()
    public_config["instagram_configured"] = is_instagram_configured()

    return public_config


@app.post("/api/config")
def api_save_config(payload: dict = Body(...)):
    saved_config = save_config(payload)

    return {
        "message": "API ayarları kaydedildi.",
        "config": saved_config
    }


@app.post("/api/fake-comment")
def api_fake_comment():
    comment = generate_fake_comment()
    insert_comment(comment)

    return {
        "message": "Fake comment added",
        "comment": comment
    }


@app.delete("/api/comments")
def api_clear_comments():
    clear_comments()

    return {
        "message": "All comments deleted"
    }