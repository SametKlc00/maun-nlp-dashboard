import json
import sqlite3

from nlp_service import analyze_comment

DB_PATH = "data/comments.db"


def reanalyze_all_comments():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, comment_text FROM comments")
    rows = cursor.fetchall()

    updated_count = 0

    for row in rows:
        comment_id = row["id"]
        comment_text = row["comment_text"] or ""

        analysis = analyze_comment(comment_text)

        cursor.execute("""
        UPDATE comments
        SET
            sentiment = ?,
            risk_level = ?,
            risk_score = ?,
            tags = ?
        WHERE id = ?
        """, (
            analysis["sentiment"],
            analysis["risk_level"],
            analysis["risk_score"],
            json.dumps(analysis["tags"], ensure_ascii=False),
            comment_id
        ))

        updated_count += 1

    conn.commit()
    conn.close()

    print(f"{updated_count} yorum yeni NLP kurallarına göre yeniden analiz edildi.")


if __name__ == "__main__":
    reanalyze_all_comments()