Ayşe Branch – Backend Güvenlik, Risk & Session Kontrol Özellikleri
📋 İçindekiler

1. Eklenen Özellikler

2. Mevcut Tüm Özellikler

3. Oluşturulan / Düzenlenen Dosyalar

4. Test Senaryoları (Manuel)

5. API Endpoint’leri

6. Frontend Entegrasyon Notları

🎯 Eklenen Özellikler
🔐 1. Risk Tabanlı Login Akışı (Adaptive Access)

Her başarılı login işleminde sistem otomatik risk analizi yapar ve sonucu frontend’e iletir.

Kullanılan Risk Sinyalleri

- Önceki başarılı login’e göre:

    - IP değişimi

    - User-Agent değişimi

    - Device değişimi

    - Location değişimi

- İlk başarılı login (baseline)

- Brute-force geçmişi

Üretilen Alanlar

- risk_score (0–100)

- risk_level: safe | suspicious | critical

- risk_reasons (explainability için)

Tüm sonuçlar login_attempts tablosuna kaydedilir.


🎨 2. Frontend için Risk → UI Mapping (Contract)

Backend, frontend’in karar vermesi için hazır state döner.
Frontend hesaplama yapmaz, sadece bu alanları kullanır.

{
  "access_token": "...",
  "risk_level": "safe | suspicious | critical",
  "ui_state": "normal | mfa | decoy",
  "alert_type": "none | warning | danger",
  "message_key": "auth.safe | auth.suspicious | auth.critical"
}

| risk_level | ui_state | Açıklama                   |
| ---------- | -------- | -------------------------- |
| safe       | normal   | Normal login               |
| suspicious | mfa      | MFA / uyarı akışı          |
| critical   | decoy    | Aldatıcı veya kısıtlı akış |


🧱 3. Brute-force Koruması (Progressive Lock)

Yanlış şifre denemelerinde kademeli geçici kilit uygulanır.
| Yanlış Deneme | Kilit Süresi |
| ------------- | ------------ |
| 3             | 30 saniye    |
| 5             | 2 dakika     |
| 7             | 24 saat      |


Davranışlar:

- Kilitliyken yapılan denemeler sayılmaz

- Süre bitince sayaç kaldığı yerden devam eder

- Lock bilgisi API response ile döner

Örnek:
{
  "code": "TEMP_LOCKED",
  "details": {
    "locked_until": "...",
    "remaining_seconds": 29
  }
}

🚨 4. Emergency Lock (Anlık Oturum İptali)

POST /api/auth/emergency-lock

Kullanıcı kendi hesabını anında kilitleyebilir.

Bu işlem:

- is_locked = true

- token_version artırılır

- Tüm mevcut token’lar geçersiz olur

Sonuç:

- Eski token → SESSION_INVALID

- /me erişimi kapanır
🔓 5. Admin Unlock Endpoint (Opsiyonel)

POST /api/auth/unlock

Amaç:

- Kilitli hesabı manuel açmak

- Demo / test / admin müdahalesi

Gereken Header:
X-ADMIN-UNLOCK-KEY: <ADMIN_UNLOCK_KEY>

Davranış:

- is_locked = false

- locked_until = null

- failed_login_attempts = 0

- token_version artırılır

- Eski token’lar otomatik geçersiz olur

🔑 6. Token Version ile Session Invalidation

Her JWT token içinde:

"tv": token_version
Kontroller:

- Emergency lock

- Admin unlock

- Manual session invalidate

Avantaj:

- Token blacklist gerekmez

- Stateless ama güvenli session yönetimi

📊 Mevcut Tüm Özellikler
Temel

✅ Kullanıcı kaydı

✅ JWT login

✅ /me endpoint

✅ LoginAttempt kayıtları

Güvenlik

✅ Risk score & risk level

✅ Explainable risk (risk_reasons)

✅ Progressive brute-force lock

✅ Emergency lock

✅ Admin unlock

✅ Session invalidation (token_version)

Veritabanı

✅ PostgreSQL

✅ SQLAlchemy ORM

✅ Flask-Migrate migration desteği

📁 Oluşturulan / Düzenlenen Dosyalar
✏️ Düzenlenen Dosyalar

- app/auth_routes.py

    - Risk hesaplama

    - Login response contract

    - Brute-force lock

    - Emergency lock

    -Unlock endpoint

app/models.py

- User: lock & token_version alanları

- LoginAttempt: risk alanları

migrations/

- Progressive lock

- MFA & risk alanları

🧪 Test Senaryoları (Manuel – Terminal)
✅ Safe Login

- Aynı IP / device

- Beklenen:

    - risk_level = safe

    - ui_state = normal

⚠️ Suspicious Login

- Yeni device / UA

- Beklenen:

    - risk_level = suspicious

    - ui_state = mfa

❌ Brute-force

- 3 yanlış → 30sn lock

- Süre bitince sayaç devam eder

🚨 Emergency Lock

- Lock atılır

- Eski token → SESSION_INVALID

🔓 Admin Unlock

- Hesap açılır

- Eski token çalışmaz

- Yeni login gerekir

🔌 API Endpoint’leri

Base URL
http://localhost:5001

| Method | Endpoint                 |
| ------ | ------------------------ |
| POST   | /api/auth/register       |
| POST   | /api/auth/login          |
| GET    | /api/auth/me             |
| POST   | /api/auth/emergency-lock |
| POST   | /api/auth/unlock         |

📌 Frontend Entegrasyon Notları

- Frontend risk hesaplamaz

- UI tamamen backend’den dönen:

    - ui_state

    - alert_type

    - message_key
alanlarına göre şekillenir

- MFA / decoy kararları backend kaynaklıdır

✅ Son Durum

- Backend güvenlik & risk altyapısı tamamlandı

- Frontend entegrasyonuna hazır

- Demo ve sunum için stabil