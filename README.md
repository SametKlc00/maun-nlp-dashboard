# MAUN NLP Sosyal Medya Risk Dashboard

Bu proje, sosyal medya platformlarından alınan yorumları doğal dil işleme yöntemleriyle analiz eden bir web dashboard sistemidir.

Sistem; yorumları olumlu, olumsuz ve nötr olarak sınıflandırır. Ayrıca yüksek riskli yorumları, nefret söylemini, hayati risk / intihar riski ifadelerini, spam mesajları ve kullanıcı bazlı risk durumlarını tespit eder.

## Özellikler

- YouTube Data API ile gerçek yorum çekme
- X ve Instagram API için altyapı
- Olumlu / olumsuz / nötr duygu analizi
- Yüksek riskli yorum tespiti
- Hayati risk / intihar riski analizi
- Nefret söylemi analizi
- Şiddet riski ve tehdit etiketi
- Kullanıcı bazlı risk analizi
- Spam / tekrar eden mesaj analizi
- Etiket, kelime ve risk grafikleri
- Tarih, duygu, risk, platform ve etiket filtreleme
- Kaynak bağlantısı ile yoruma doğrudan gitme

## Kullanılan Teknolojiler

- Python
- FastAPI
- SQLite
- HTML
- CSS
- JavaScript
- Chart.js
- YouTube Data API v3

## Kurulum

Önce gerekli kütüphaneleri yükleyin:

```powershell
py -m pip install -r requirements.txt
