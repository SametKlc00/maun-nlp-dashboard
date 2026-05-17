import re


positive_words = [
    "güzel", "başarılı", "teşekkür", "teşekkürler", "harika", "mükemmel",
    "beğendim", "iyi", "çok iyi", "süper", "faydalı", "gurur", "kaliteli",
    "memnun", "sevindim", "tebrikler", "başarılar", "efsane", "muhteşem",
    "şahane", "takdir", "destekliyorum", "gelişmiş", "yararlı", "verimli",
    "anlamlı", "değerli", "umut verici", "seviyoruz", "çok güzel",
    "iyi olmuş", "başarılı olmuş", "çok başarılı", "helal olsun",
    "emeğinize sağlık", "elinize sağlık", "gurur duyuyoruz", "çok faydalı",
    "mükemmel olmuş", "çok iyi olmuş", "bravo", "alkış", "kutluyorum",
    "başarılarınızın devamını dilerim", "harika iş", "çok beğendim",
    "memnun kaldım", "iyi ki varsınız", "takdire şayan", "hayırlı olsun",
    "hayırlı uğurlu olsun", "başarı diliyorum", "çok başarılısınız",
    "çok iyi düşünülmüş", "yerinde karar", "doğru karar", "çok doğru",
    "gurur verici", "örnek çalışma", "çok değerli", "çok anlamlı",
    "güzel hizmet", "iyi hizmet", "kaliteli eğitim", "başarılı üniversite",
    "çok güzel kampüs", "kampüs güzel", "hocalar iyi", "hocalar ilgili",
    "ilgili hocalar", "başarılı öğrenciler", "çok güzel etkinlik",
    "çok güzel program", "çok güzel video", "çok iyi anlatılmış",
    "açıklayıcı", "bilgilendirici", "faydalı içerik", "çok yararlı",
    "sevindirici", "mutlu oldum", "takipteyiz", "destekliyoruz",
    "çok iyi proje", "başarı hikayesi", "ülkemiz için güzel", "maşallah",
    "allah razı olsun", "ellerinize sağlık", "emeği geçenlere teşekkürler",
    "teşekkür ederiz", "tebrik ederim", "tebrik ediyoruz", "gururlandık",
    "çok gururlandık", "mükemmel bir çalışma", "başarılı bir çalışma",
    "eline sağlık", "emeğine sağlık", "sağ ol", "sağol", "çok sağol",
    "iyi forumlar", "ilgiyle izliyorum", "severek izliyorum",
    "videolar güzel", "anlatım güzel", "çok açıklayıcı", "yardımcı oldu"
]


negative_words = [
    "kötü", "çok kötü", "berbat", "şikayet", "şikâyet", "memnun değil",
    "cevap vermiyor", "sorun", "problem", "rezalet", "yetersiz", "pahalı",
    "geç", "ilgisiz", "hatalı", "mağdur", "rahatsız", "saçmalık",
    "ayıp", "yazık", "yazıklar olsun", "rezil", "çözüm yok", "adaletsiz",
    "haksızlık", "umursamaz", "duyarsız", "beceriksiz", "kalitesiz",
    "kötü yönetim", "ihmal", "ihmalkarlık", "ihmalkârlık", "skandal",
    "utanın", "bıktık", "yeter artık", "çok pahalı", "mağduruz",
    "sıkıntı", "bozuk", "çalışmıyor", "cevap alamıyoruz", "geri dönüş yok",
    "kimse ilgilenmiyor", "kimse cevap vermiyor", "ciddiyetsiz", "vasat",
    "çözümsüz", "usandık", "pişmanlık", "hayal kırıklığı", "adalet yok",
    "hizmet yok", "sistem kötü", "hiç memnun değilim", "çok mağduruz",
    "böyle olmaz", "kabul etmiyoruz", "sorumsuzluk", "denetim yok",
    "çok üzücü", "üzücü", "utanç verici", "kabul edilemez", "yetersiz kalmış",
    "çok eksik", "eksik", "eksiklik", "boşuna", "boşa zaman", "gereksiz",
    "anlamsız", "yanlış karar", "hatalı karar", "yanlış uygulama",
    "mağduriyet", "mağdur edildik", "mağdur ediyor", "adaletsiz uygulama",
    "haksız uygulama", "haksızlık yapılıyor", "şikayetçiyiz",
    "şikayet edeceğiz", "cevap istiyoruz", "açıklama bekliyoruz",
    "neden cevap yok", "neden açıklama yok", "kimse bakmıyor",
    "kimse duymuyor", "kimse görmüyor", "sözde üniversite",
    "yönetim istifa", "istifa", "denetimsizlik", "başarısız",
    "çok başarısız", "kötü hizmet", "kötü eğitim", "kalitesiz eğitim",
    "kötü kampüs", "kötü yurt", "yurt kötü", "yemek kötü", "ulaşım kötü",
    "hocalar ilgisiz", "personel ilgisiz", "öğrenci işleri kötü",
    "öğrenci işleri ilgisiz", "çok sıra var", "sıra bekliyoruz",
    "geç kaldınız", "geç açıklanıyor", "açıklanmıyor", "duyuru yok",
    "bilgi yok", "iletişim yok", "çözüm istiyoruz", "rezalet sistem",
    "sistem çökmüş", "sistem açılmıyor", "site çalışmıyor",
    "başvuru yapamıyoruz", "kayıt yapamıyoruz", "ders seçemiyoruz",
    "notlar açıklanmadı", "hakkımız yeniyor", "hakkımızı arıyoruz",
    "tepki gösteriyoruz", "çok sinirliyim", "sinir bozucu", "can sıkıcı",
    "hayal kırıklığına uğradım", "gelmeyin", "seçmeyin",
    "pişman olursunuz", "pişman olursun", "mantıklı değil",
    "tavsiye etmem", "önermem", "boş bölüm", "işsiz kalırsınız",
    "okunmaz", "değmez", "çok zor", "soğuk", "soğuk kanlı",
    "eğlence yok", "imkanı yok", "olanak yok", "bitmemiş", "arkadaşın yok"
]


question_words = [
    "ne zaman", "nasıl", "nerede", "kaç", "hangi", "neden", "niçin",
    "başvuru", "kayıt", "son tarih", "bilgi", "açıklandı mı",
    "nereden", "kimden", "nasıl yapılıyor", "nasıl başvurulur",
    "başvurular ne zaman", "kayıtlar ne zaman", "belli oldu mu",
    "duyuru var mı", "yardımcı olur musunuz", "bilgi alabilir miyim",
    "link var mı", "nereden bakılır", "kim ilgileniyor", "sonuçlar ne zaman",
    "kaç puan", "taban puan", "kontenjan", "bölüm var mı", "yurt var mı",
    "burs var mı", "servis var mı", "ulaşım nasıl", "ders kaydı nasıl",
    "transkript nasıl alınır", "belge nasıl alınır", "var mı", "mı", "mi",
    "mu", "mü", "sence", "sizce", "acaba", "olur mu", "gerekir mi"
]


risk_words_high = [
    "tehdit", "saldırı", "saldıracağım", "kavga", "yakacağım",
    "hesap soracağım", "hesabını soracağım", "pişman olacaksınız",
    "pişman edeceğim", "bedel ödeyeceksiniz", "bunun hesabı sorulur",
    "mahkemeye vereceğim", "savcılığa vereceğim", "dava açacağım",
    "yanınıza kalmayacak", "bunu ödeyeceksiniz", "sizi bulacağım",
    "hesap vereceksiniz", "bunun bedeli olacak", "bomba", "bombalı",
    "patlama", "patlatacağım", "silah", "silahlı", "bıçak",
    "bıçaklayacağım", "kurşun", "ateş edeceğim", "vuracağım",
    "öldüreceğim", "öldürürüm", "dayak", "döveceğim", "yakılsın",
    "basacağım", "saldırı olacak", "kan çıkacak", "kan çıkar",
    "intikam", "hedef alacağım", "tehdit ediyorum", "canınıza okurum",
    "hesaplaşacağız", "bunu yanınıza bırakmam", "bedelini ödeyeceksiniz",
    "orayı basarım", "gelip hesap sorarım", "bu iş burada bitmez",
    "sonunuz kötü olur", "kimse kurtaramaz", "savaş çıkar",
    "ortalık karışır", "yakıp yıkarım", "patlatırım", "vururum",
    "saldırırım", "döverim", "öldürmek", "zarar vermek", "zarar vereceğim"
]


risk_words_critical = [
    "intihar", "kendime zarar", "kendimi öldür", "yaşamak istemiyorum",
    "ölmek istiyorum", "dayanamıyorum", "artık yaşamak istemiyorum",
    "hayatıma son", "hayatıma son vereceğim", "kendimi yok edeceğim",
    "bana kimse yardım etmiyor", "son çarem", "kendime bir şey yapacağım",
    "kendimi asacağım", "kendimi keseceğim", "kendimi yakacağım",
    "artık dayanamıyorum", "yaşamaktan yoruldum", "yaşamak zor geliyor",
    "kimse beni anlamıyor", "yardım edin dayanamıyorum", "son kez yazıyorum",
    "hayat bitti", "çıkış yolu yok", "kendimi iyi hissetmiyorum"
]


hate_speech_words = [
    "nefret", "nefret söylemi", "ırkçı", "ırkçılık", "ayrımcılık",
    "ayrımcı", "dışlayıcı", "aşağılama", "aşağılayıcı",
    "ötekileştirme", "defolun", "bunları istemiyoruz",
    "bu kişiler gelmesin", "bunlar okumasın", "bunlara yer yok",
    "ülkeden gitsinler", "hepsi aynı", "bunlardan bir şey olmaz",
    "insan değil", "hak etmiyorlar", "okula alınmasın",
    "kampüse alınmasın", "yurda alınmasın", "sınıfa alınmasın"
]


vital_risk_words = [
    "hayati tehlike", "yaşam tehlikesi", "can güvenliği",
    "can güvenliğimiz yok", "can güvenliği yok", "hayatım tehlikede",
    "ambulans", "hastaneye kaldırıldı", "bayıldı", "bayıldım",
    "nefes alamıyorum", "kan kaybı", "kalp krizi", "acil yardım",
    "ölüm tehlikesi", "ölüm riski", "can kaybı", "intihar",
    "kendime zarar", "kendimi öldür", "yaşamak istemiyorum",
    "ölmek istiyorum", "hayatıma son", "dayanamıyorum",
    "artık dayanamıyorum", "yaşamaktan yoruldum"
]


weapon_words = [
    "bomba", "silah", "bıçak", "kurşun", "patlayıcı", "molotof",
    "tüfek", "tabanca", "mermi", "kesici alet", "ateşli silah",
    "patlama", "bombalı", "silahlı saldırı", "bıçaklı saldırı",
    "dinamit", "el bombası", "mayın", "barut", "patlatıcı"
]


violence_words = [
    "öldür", "öldüreceğim", "öldürürüm", "vuracağım", "döveceğim",
    "darp", "linç", "saldırı", "saldıracağım", "zarar vereceğim",
    "yakacağım", "patlatacağım", "bıçaklayacağım", "şiddet",
    "intikam", "tehdit", "kavga", "döverim", "vurma", "yaralama",
    "yaralayacağım", "yakıp yıkmak", "baskın", "kan çıkacak",
    "kan çıkar"
]


insult_words = [
    "aptal", "salak", "rezil", "beceriksiz", "gerizekalı", "cahil",
    "utanmaz", "terbiyesiz", "saygısız", "sorumsuz", "yetersizsiniz",
    "iş bilmez", "işbilmez", "boş yapıyorsunuz", "dalga mı geçiyorsunuz",
    "adam değilsiniz", "ciddiyetsizsiniz", "vasatsınız", "şerefsiz",
    "ahlaksız", "rezilsiniz", "kepazelik", "kepaze", "yüzsüz",
    "rezillik", "yetersizler", "beceremiyorsunuz", "ciddiyetsizler",
    "utanmanız lazım", "aklınız yok", "işinizi yapın",
    "işinizi bilmiyorsunuz"
]


crisis_words = [
    "acil", "hemen", "kriz", "skandal", "ihmal", "ölüm", "kaza",
    "asansör", "yangın", "güvenlik", "tehlike", "risk", "panik",
    "can güvenliği", "sağlık sorunu", "yurt sorunu", "barınamıyoruz",
    "felaket", "ihmal var", "önlem alın", "yardım edin", "ambulans",
    "polis", "savcılık", "mahkeme", "olay", "krize dönüştü",
    "can kaybı", "yaralı", "ölü", "hastane", "güvenlik açığı",
    "büyük sorun", "ciddi sorun", "derhal", "ivedi", "önlem yok",
    "tehlikedeyiz", "yardım bekliyoruz", "sesimizi duyun"
]


positive_emojis = [
    "😊", "😄", "😁", "😍", "🥰", "👏", "👍", "💚", "💙", "❤️",
    "❤", "🔥", "✨", "🎉", "🙌", "👌", "🤩", "⭐", "🌟", "🙂",
    "😇", "💯", "🏆", "✅", "💪", "🙏"
]


negative_emojis = [
    "😡", "😠", "🤬", "😤", "👎", "😞", "😢", "😭", "💔",
    "😒", "🙄", "😔", "😟", "😕", "😩", "😫", "😣", "❌"
]


risk_emojis = [
    "⚠️", "⚠", "🚨", "❗", "💀", "☠️", "☠", "🔪", "💣", "🔫", "🧨"
]


topic_keywords = {
    "yemekhane": [
        "yemekhane", "yemek", "menü", "kantin", "tabldot", "öğle yemeği",
        "yemekhane zammı", "yemek fiyatı", "porsiyon", "kalitesiz yemek",
        "yemekler kötü", "yemek pahalı"
    ],
    "ulaşım": [
        "otobüs", "servis", "ulaşım", "durak", "ring", "metro", "dolmuş",
        "kampüs içi ulaşım", "sefer", "ulaşamıyoruz", "ring yok",
        "servis yok", "otobüs yok"
    ],
    "öğrenci işleri": [
        "öğrenci işleri", "transkript", "belge", "harç", "kayıt",
        "danışman onayı", "ders kaydı", "mezuniyet belgesi", "dilekçe",
        "evrak", "sistem açılmıyor", "obs", "öbs", "otomasyon"
    ],
    "akademik": [
        "ders", "sınav", "hoca", "not", "vize", "final", "bütünleme",
        "devamsızlık", "ödev", "proje", "akademisyen", "ders seçimi",
        "ortalama", "mezuniyet", "staj", "bölüm", "fakülte", "danışman"
    ],
    "barınma": [
        "yurt", "kyk", "kalacak yer", "barınma", "oda", "yatak",
        "asansör", "yurt sorunu", "yurt ücreti", "yurttan çıkarıldık",
        "yurt çıkmadı", "barınamıyoruz", "konaklama", "oda sorunu"
    ],
    "etkinlik": [
        "etkinlik", "konferans", "seminer", "şenlik", "festival",
        "kulüp", "topluluk", "panel", "söyleşi", "program"
    ],
    "tercih ve kayıt": [
        "yks", "tercih", "kayıt", "ek tercih", "yerleştirme",
        "üniversite tercihi", "e-kayıt", "kontenjan", "taban puan",
        "bölüm seçimi", "puan", "sıralama"
    ],
    "güvenlik": [
        "güvenlik", "tehlike", "kaza", "yangın", "asansör",
        "can güvenliği", "ihmal", "önlem", "saldırı", "silah",
        "bıçak", "bomba", "patlama", "polis", "güvenlik görevlisi"
    ],
    "ekonomi": [
        "zam", "pahalı", "ücret", "harç", "burs", "geçim", "para",
        "fiyat", "maliyet", "fahiş", "ödeyemiyoruz", "ekonomik",
        "burs yatmadı"
    ],
    "protesto": [
        "protesto", "eylem", "boykot", "yürüyüş", "basın açıklaması",
        "itiraz", "tepki", "direniş", "hak arıyoruz"
    ],
    "şiddet": [
        "bomba", "silah", "bıçak", "saldırı", "tehdit", "öldür",
        "vuracağım", "yakacağım", "patlatacağım", "döveceğim"
    ],
    "nefret söylemi": [
        "nefret", "nefret söylemi", "ırkçı", "ırkçılık", "ayrımcılık",
        "ayrımcı", "dışlayıcı", "ötekileştirme", "defolun",
        "bunları istemiyoruz"
    ],
    "hayati risk": [
        "hayati tehlike", "yaşam tehlikesi", "can güvenliği",
        "ambulans", "hastaneye kaldırıldı", "bayıldı", "nefes alamıyorum",
        "kan kaybı", "kalp krizi", "acil yardım", "ölüm tehlikesi",
        "ölüm riski", "can kaybı", "intihar", "kendime zarar",
        "yaşamak istemiyorum", "ölmek istiyorum"
    ]
}


def normalize_text(text):
    return str(text or "").lower()


def contains_term(text, term):
    text = normalize_text(text)
    term = normalize_text(term).strip()

    if term == "":
        return False

    if not re.search(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]", term):
        return term in text

    if " " in term:
        return term in text

    pattern = rf"(?<![a-zA-ZçğıöşüÇĞİÖŞÜ0-9]){re.escape(term)}(?![a-zA-ZçğıöşüÇĞİÖŞÜ0-9])"

    return re.search(pattern, text, re.IGNORECASE) is not None


def contains_any(text, words):
    return any(contains_term(text, word) for word in words)


def count_matches(text, words):
    return sum(1 for word in words if contains_term(text, word))


def detect_personal_data(text):
    text = str(text or "")

    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"(\+90|0)?\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}"
    tc_pattern = r"\b[1-9][0-9]{10}\b"

    has_email = re.search(email_pattern, text) is not None
    has_phone = re.search(phone_pattern, text) is not None
    has_tc = re.search(tc_pattern, text) is not None

    return has_email or has_phone or has_tc


def detect_tags(text, original_text):
    tags = []

    if contains_any(text, positive_words) or contains_any(original_text, positive_emojis):
        tags.append("övgü")

    if contains_any(text, negative_words) or contains_any(original_text, negative_emojis):
        tags.append("şikayet")

    if contains_any(text, question_words) or "?" in original_text:
        tags.append("soru")

    if contains_any(text, risk_words_high):
        tags.append("tehdit")

    if contains_any(text, risk_words_critical):
        tags.append("kritik ifade")

    if contains_any(text, hate_speech_words):
        tags.append("nefret söylemi")

    if contains_any(text, vital_risk_words):
        tags.append("hayati risk")

    if contains_any(text, weapon_words) or contains_any(original_text, risk_emojis):
        tags.append("silah/patlayıcı riski")

    if contains_any(text, violence_words):
        tags.append("şiddet riski")

    if contains_any(text, insult_words):
        tags.append("hakaret")

    if contains_any(text, crisis_words) or contains_any(original_text, risk_emojis):
        tags.append("kriz")

    if detect_personal_data(text):
        tags.append("kişisel veri")

    for topic, keywords in topic_keywords.items():
        if contains_any(text, keywords):
            tags.append(topic)

    if len(tags) == 0:
        tags.append("genel")

    return list(dict.fromkeys(tags))


def is_simple_question(text, original_text):
    text = normalize_text(text)

    question_signal = (
        "?" in original_text
        or contains_any(text, question_words)
        or text.endswith("mi")
        or text.endswith("mı")
        or text.endswith("mu")
        or text.endswith("mü")
    )

    dangerous_signal = (
        contains_any(text, risk_words_high)
        or contains_any(text, risk_words_critical)
        or contains_any(text, hate_speech_words)
        or contains_any(text, vital_risk_words)
        or contains_any(text, weapon_words)
        or contains_any(text, violence_words)
        or contains_any(original_text, risk_emojis)
    )

    return question_signal and not dangerous_signal


def analyze_comment(comment_text):
    original_text = str(comment_text or "")
    text = normalize_text(original_text)

    positive_count = count_matches(text, positive_words) + count_matches(original_text, positive_emojis)
    negative_count = count_matches(text, negative_words) + count_matches(original_text, negative_emojis)

    has_high_risk = contains_any(text, risk_words_high)
    has_critical_risk = contains_any(text, risk_words_critical)
    has_hate_speech = contains_any(text, hate_speech_words)
    has_vital_risk = contains_any(text, vital_risk_words)
    has_weapon = contains_any(text, weapon_words)
    has_violence = contains_any(text, violence_words)
    has_insult = contains_any(text, insult_words)
    has_crisis = contains_any(text, crisis_words)
    has_personal_data = detect_personal_data(text)
    has_risk_emoji = contains_any(original_text, risk_emojis)
    has_negative_emoji = contains_any(original_text, negative_emojis)

    if has_insult:
        negative_count += 2

    if has_crisis:
        negative_count += 2

    if has_high_risk:
        negative_count += 3

    if has_critical_risk:
        negative_count += 4

    if has_hate_speech:
        negative_count += 3

    if has_vital_risk:
        negative_count += 4

    if has_weapon or has_violence:
        negative_count += 4

    if has_personal_data:
        negative_count += 1

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        if contains_any(text, question_words) or "?" in original_text:
            sentiment = "neutral"
        elif contains_any(text, topic_keywords["ekonomi"]) or contains_any(text, topic_keywords["güvenlik"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"

    risk_score = 0

    if has_critical_risk:
        risk_score += 85

    if has_vital_risk:
        risk_score += 70

    if has_high_risk:
        risk_score += 55

    if has_weapon:
        risk_score += 50

    if has_violence:
        risk_score += 45

    if has_hate_speech:
        risk_score += 45

    if has_insult:
        risk_score += 25

    if has_crisis:
        risk_score += 20

    if has_risk_emoji:
        risk_score += 25

    if has_negative_emoji:
        risk_score += 8

    if has_personal_data:
        risk_score += 35

    if sentiment == "negative":
        risk_score += 15

    if original_text.isupper() and len(original_text) > 15:
        risk_score += 10

    if contains_any(text, ["acil", "hemen", "şikayet edeceğim", "mahkemeye", "savcılığa"]):
        risk_score += 10

    if len(original_text) > 250 and sentiment == "negative":
        risk_score += 5

    if is_simple_question(text, original_text) and risk_score < 60:
        risk_score = 0
        risk_level = "low"
    else:
        if risk_score > 100:
            risk_score = 100

        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"

    tags = detect_tags(text, original_text)

    return {
        "sentiment": sentiment,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "tags": tags
    }