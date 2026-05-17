import random
import hashlib
import json
from datetime import datetime

from nlp_service import analyze_comment


sample_comments = [
    "Üniversitenizin etkinliği çok güzel olmuş, tebrikler.",
    "Öğrenci işleri hiçbir şekilde cevap vermiyor, çok mağdur olduk.",
    "Kayıt tarihleri ne zaman açıklanacak?",
    "Yemekhane fiyatları çok pahalı, öğrenciler zor durumda.",
    "Bugünkü konferans çok faydalıydı, teşekkürler.",
    "Otobüs seferleri yetersiz, ulaşımda ciddi sorun yaşıyoruz.",
    "Bu kadar ilgisizlik olmaz, gerçekten rezalet.",
    "Final sınav tarihleri nereden öğreniliyor?",
    "Bu üniversiteyle gurur duyuyorum.",
    "Acil çözüm istiyoruz, yoksa şikayet edeceğim.",
    "Yurt başvuruları hakkında bilgi alabilir miyim?",
    "Kampüs çok güzel ve temiz.",
    "Ders programı hâlâ açıklanmadı, bu durum bizi mağdur ediyor.",
    "Bana dönüş yapılmazsa hesabını soracağım.",
    "Belge almak için üç gündür bekliyorum.",
    "Etkinlik duyuruları çok başarılı.",
    "Telefon numaram 0555 123 45 67 bana dönüş yapar mısınız?",
    "Yaşamak istemiyorum, kimse bana yardımcı olmuyor.",
    "Hocalarımız çok ilgili, teşekkür ederiz.",
    "Kantin fiyatları çok yüksek."
]

sample_authors = [
    "ogrenci_27",
    "aday_ogrenci",
    "mezun_2020",
    "kampus_haber",
    "anonim_kullanici",
    "ogrenci_toplulugu",
    "veli_01",
    "user_1453"
]


def hash_author(author_username):
    return hashlib.sha256(author_username.encode("utf-8")).hexdigest()


def generate_fake_comment():
    comment_text = random.choice(sample_comments)
    author_username = random.choice(sample_authors)

    analysis = analyze_comment(comment_text)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    comment = {
        "platform": "X",
        "external_id": "fake_" + str(random.randint(100000, 999999)),
        "author_username": author_username,
        "author_hash": hash_author(author_username),
        "comment_text": comment_text,
        "sentiment": analysis["sentiment"],
        "risk_level": analysis["risk_level"],
        "risk_score": analysis["risk_score"],
        "tags": json.dumps(analysis["tags"], ensure_ascii=False),
        "created_at": now,
        "collected_at": now
    }

    return comment