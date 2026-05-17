import sqlite3
import os
import json
import re
from collections import Counter, defaultdict

DB_PATH = "data/comments.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        external_id TEXT,
        author_username TEXT,
        author_hash TEXT,
        comment_text TEXT,
        sentiment TEXT,
        risk_level TEXT,
        risk_score INTEGER,
        tags TEXT,
        source_url TEXT,
        created_at TEXT,
        collected_at TEXT
    );
    """)

    cursor.execute("PRAGMA table_info(comments)")
    columns = [column["name"] for column in cursor.fetchall()]

    if "source_url" not in columns:
        cursor.execute("ALTER TABLE comments ADD COLUMN source_url TEXT")

    conn.commit()
    conn.close()


def insert_comment(comment):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO comments (
        platform,
        external_id,
        author_username,
        author_hash,
        comment_text,
        sentiment,
        risk_level,
        risk_score,
        tags,
        source_url,
        created_at,
        collected_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        comment["platform"],
        comment["external_id"],
        comment["author_username"],
        comment["author_hash"],
        comment["comment_text"],
        comment["sentiment"],
        comment["risk_level"],
        comment["risk_score"],
        comment["tags"],
        comment.get("source_url", ""),
        comment["created_at"],
        comment["collected_at"]
    ))

    conn.commit()
    conn.close()


def get_all_comments(limit=100):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM comments
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_risky_comments(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM comments
    WHERE risk_level IN ('high', 'critical')
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM comments")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS positive FROM comments WHERE sentiment = 'positive'")
    positive = cursor.fetchone()["positive"]

    cursor.execute("SELECT COUNT(*) AS negative FROM comments WHERE sentiment = 'negative'")
    negative = cursor.fetchone()["negative"]

    cursor.execute("SELECT COUNT(*) AS neutral FROM comments WHERE sentiment = 'neutral'")
    neutral = cursor.fetchone()["neutral"]

    cursor.execute("""
    SELECT COUNT(*) AS high_risk
    FROM comments
    WHERE risk_level IN ('high', 'critical')
    """)
    high_risk = cursor.fetchone()["high_risk"]

    conn.close()

    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "high_risk": high_risk
    }


def clear_comments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM comments")

    conn.commit()
    conn.close()


def comment_exists(external_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) AS count
    FROM comments
    WHERE external_id = ?
    """, (external_id,))

    count = cursor.fetchone()["count"]

    conn.close()

    return count > 0

def parse_tags(tags_text):
    if not tags_text:
        return []

    try:
        tags = json.loads(tags_text)

        if isinstance(tags, list):
            return tags

        return []
    except Exception:
        return [
            tag.strip()
            for tag in str(tags_text).split(",")
            if tag.strip() != ""
        ]


def get_tag_stats(limit=12):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT tags FROM comments")
    rows = cursor.fetchall()
    conn.close()

    counter = Counter()

    for row in rows:
        tags = parse_tags(row["tags"])

        for tag in tags:
            counter[tag] += 1

    return [
        {
            "tag": tag,
            "count": count
        }
        for tag, count in counter.most_common(limit)
    ]


def get_risk_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT risk_level, COUNT(*) AS count
    FROM comments
    GROUP BY risk_level
    """)

    rows = cursor.fetchall()
    conn.close()

    result = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }

    for row in rows:
        level = row["risk_level"]

        if level in result:
            result[level] = row["count"]

    return result


def get_user_risk_stats(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        author_username,
        author_hash,
        COUNT(*) AS total_comments,
        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_comments,
        SUM(CASE WHEN risk_level = 'medium' THEN 1 ELSE 0 END) AS medium_risk_comments,
        SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) AS high_risk_comments,
        SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END) AS critical_risk_comments,
        MAX(risk_score) AS max_risk_score,
        AVG(risk_score) AS avg_risk_score
    FROM comments
    GROUP BY author_username, author_hash
    ORDER BY
        critical_risk_comments DESC,
        high_risk_comments DESC,
        medium_risk_comments DESC,
        max_risk_score DESC,
        total_comments DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    users = []

    for row in rows:
        users.append({
            "author_username": row["author_username"],
            "author_hash": row["author_hash"],
            "total_comments": row["total_comments"] or 0,
            "negative_comments": row["negative_comments"] or 0,
            "medium_risk_comments": row["medium_risk_comments"] or 0,
            "high_risk_comments": row["high_risk_comments"] or 0,
            "critical_risk_comments": row["critical_risk_comments"] or 0,
            "max_risk_score": row["max_risk_score"] or 0,
            "avg_risk_score": round(row["avg_risk_score"] or 0, 1)
        })

    return users


def get_word_stats(limit=30):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT comment_text FROM comments")
    rows = cursor.fetchall()
    conn.close()

    stopwords = {
        "bir", "bu", "şu", "o", "ve", "ile", "de", "da", "mi", "mı", "mu", "mü",
        "çok", "daha", "için", "gibi", "ama", "fakat", "olan", "olarak", "var",
        "yok", "ne", "neden", "nasıl", "nerede", "hangi", "ben", "sen", "biz",
        "siz", "onlar", "her", "hiç", "kadar", "sonra", "önce", "bile", "artık",
        "şey", "şeyi", "şekilde", "zaman", "diye", "ki", "en", "ya", "hem",
        "veya", "ya da", "ise", "bana", "bize", "bunu", "bunun", "şunu", "onu",
        "oldu", "olur", "olan", "olsun", "oluyor", "etmek", "eden", "ediyor",
        "https", "http", "www", "com"
    }

    counter = Counter()

    for row in rows:
        text = row["comment_text"] or ""
        words = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+", text.lower())

        for word in words:
            if len(word) < 3:
                continue

            if word in stopwords:
                continue

            counter[word] += 1

    return [
        {
            "word": word,
            "count": count
        }
        for word, count in counter.most_common(limit)
    ]


def get_analysis_summary():
    stats = get_stats()
    tag_stats = get_tag_stats(limit=5)
    risk_stats = get_risk_stats()
    word_stats = get_word_stats(limit=5)

    total = stats["total"]

    if total == 0:
        return {
            "summary_text": "Henüz analiz edilecek yorum bulunmuyor.",
            "total": 0,
            "positive_rate": 0,
            "negative_rate": 0,
            "neutral_rate": 0,
            "high_risk_rate": 0,
            "top_tags": [],
            "top_words": [],
            "risk_stats": risk_stats
        }

    positive_rate = round((stats["positive"] / total) * 100, 1)
    negative_rate = round((stats["negative"] / total) * 100, 1)
    neutral_rate = round((stats["neutral"] / total) * 100, 1)
    high_risk_rate = round((stats["high_risk"] / total) * 100, 1)

    top_tag_names = [item["tag"] for item in tag_stats]
    top_word_names = [item["word"] for item in word_stats]

    if len(top_tag_names) > 0:
        top_tags_text = ", ".join(top_tag_names)
    else:
        top_tags_text = "etiket bulunamadı"

    if len(top_word_names) > 0:
        top_words_text = ", ".join(top_word_names)
    else:
        top_words_text = "kelime bulunamadı"

    summary_text = (
        f"Toplam {total} yorum analiz edildi. "
        f"Yorumların %{positive_rate} kadarı olumlu, %{negative_rate} kadarı olumsuz "
        f"ve %{neutral_rate} kadarı nötr olarak sınıflandırıldı. "
        f"Yüksek/kritik riskli yorum oranı %{high_risk_rate} seviyesindedir. "
        f"En sık görülen etiketler: {top_tags_text}. "
        f"Öne çıkan kelimeler: {top_words_text}."
    )

    return {
        "summary_text": summary_text,
        "total": total,
        "positive_rate": positive_rate,
        "negative_rate": negative_rate,
        "neutral_rate": neutral_rate,
        "high_risk_rate": high_risk_rate,
        "top_tags": tag_stats,
        "top_words": word_stats,
        "risk_stats": risk_stats
    }
def normalize_spam_text(text):
    text = str(text or "").lower()
    text = re.sub(r"http\S+|www\S+", " link ", text)
    text = re.sub(r"[^a-zA-ZçğıöşüÇĞİÖŞÜ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def calculate_spam_level(score):
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 35:
        return "medium"
    return "low"


def get_spam_analysis(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        platform,
        author_username,
        author_hash,
        comment_text,
        collected_at,
        source_url
    FROM comments
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    comments = [dict(row) for row in rows]

    message_groups = defaultdict(list)
    user_groups = defaultdict(list)

    for comment in comments:
        normalized_text = normalize_spam_text(comment.get("comment_text", ""))

        if len(normalized_text) < 5:
            continue

        comment["normalized_text"] = normalized_text

        message_groups[normalized_text].append(comment)

        user_key = comment.get("author_hash") or comment.get("author_username") or "unknown"
        user_groups[user_key].append(comment)

    repeated_messages = []

    for normalized_text, items in message_groups.items():
        if len(items) < 2:
            continue

        users = sorted(list(set([
            item.get("author_username", "unknown")
            for item in items
        ])))

        repeated_messages.append({
            "comment_text": items[0].get("comment_text", ""),
            "repeat_count": len(items),
            "user_count": len(users),
            "users": users[:5],
            "platform": items[0].get("platform", ""),
            "latest_time": items[0].get("collected_at", ""),
            "source_url": items[0].get("source_url", "")
        })

    repeated_messages.sort(
        key=lambda item: (item["repeat_count"], item["user_count"]),
        reverse=True
    )

    spam_users = []

    for user_key, items in user_groups.items():
        total_comments = len(items)

        if total_comments < 3:
            continue

        normalized_texts = [
            item.get("normalized_text", normalize_spam_text(item.get("comment_text", "")))
            for item in items
        ]

        text_counter = Counter(normalized_texts)

        unique_comment_count = len(text_counter)
        max_same_comment_count = max(text_counter.values()) if text_counter else 0
        duplicate_comment_count = total_comments - unique_comment_count

        link_count = sum(
            1 for item in items
            if "http" in str(item.get("comment_text", "")).lower()
            or "www" in str(item.get("comment_text", "")).lower()
        )

        short_comment_count = sum(
            1 for item in items
            if len(str(item.get("comment_text", "")).strip()) < 20
        )

        spam_score = 0

        spam_score += duplicate_comment_count * 18
        spam_score += max_same_comment_count * 12
        spam_score += link_count * 15

        if total_comments >= 5:
            spam_score += 15

        if unique_comment_count <= 2 and total_comments >= 4:
            spam_score += 25

        if short_comment_count >= 4:
            spam_score += 10

        if spam_score > 100:
            spam_score = 100

        spam_level = calculate_spam_level(spam_score)

        if spam_score < 35:
            continue

        most_repeated_text = text_counter.most_common(1)[0][0]

        original_example = ""
        for item in items:
            if item.get("normalized_text") == most_repeated_text:
                original_example = item.get("comment_text", "")
                break

        spam_users.append({
            "author_username": items[0].get("author_username", "unknown"),
            "author_hash": items[0].get("author_hash", ""),
            "platform": items[0].get("platform", ""),
            "total_comments": total_comments,
            "unique_comment_count": unique_comment_count,
            "duplicate_comment_count": duplicate_comment_count,
            "max_same_comment_count": max_same_comment_count,
            "link_count": link_count,
            "spam_score": spam_score,
            "spam_level": spam_level,
            "example_comment": original_example,
            "latest_time": items[0].get("collected_at", "")
        })

    spam_users.sort(
        key=lambda item: item["spam_score"],
        reverse=True
    )

    return {
        "repeated_messages": repeated_messages[:limit],
        "spam_users": spam_users[:limit]
    }