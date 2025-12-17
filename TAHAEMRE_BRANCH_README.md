# Taha Emre Orhan Branch – Özellikler ve Kullanım Kılavuzu

## 📋 İçindekiler
1. [Eklenen Özellikler](#eklenen-özellikler)
2. [Mevcut Tüm Özellikler](#mevcut-tüm-özellikler)
3. [Oluşturulan/Düzenlenen Dosyalar](#oluşturulandüzenlenen-dosyalar)
4. [Programı Çalıştırma](#programı-çalıştırma)
5. [Test Senaryoları](#test-senaryoları)
6. [API Endpoint'leri](#api-endpointleri)

---

## 🎯 Eklenen Özellikler

### 🔐 1. Risk Engine (Risk Skoru ve Aksiyon Kararı)
- Her girişte **otomatik risk analizi** yapılır
- Analiz kriterleri:
  - IP adresi değişimi
  - Cihaz (User-Agent) değişimi
  - Gece / olağan dışı saatler
  - Kısa sürede başarısız girişler
- Üretilen çıktılar:
  - `risk_score` (0–100)
  - `risk_reasons` (ör. `new_ip`, `new_device`, `rapid_failures`)
  - `risk_action`: `SAFE`, `MFA`, `DECOY`
  - `risk_level`: `safe`, `suspicious`, `critical`

---

### 🔑 2. OTP Tabanlı MFA Akışı
- MFA gerektiğinde sistem **tek kullanımlık doğrulama kodu (OTP)** üretir
- OTP doğrulanmadan **token verilmez**
- OTP doğrulandıktan sonra:
  - `access_token`
  - `refresh_token`
  oluşturulur
- Demo amaçlı OTP response içinde `dev_otp` olarak döner

---

### 🎭 3. Decoy (Aldatıcı Yanıt) Mekanizması
- Çok yüksek riskli girişlerde:
  - Gerçek token üretilmez
  - Sahte (decoy) response döndürülür
- Amaç:
  - Saldırganı oyalamak
  - Gerçek API erişimini engellemek

---

### 🧪 4. Otomatik Test Altyapısı
- Pytest kullanılarak otomatik testler yazıldı
- Test edilen akışlar:
  - Register
  - Login
  - MFA Request / Verify
  - Risk Engine kararları
- Tüm testler başarıyla geçmektedir

---

## 📊 Mevcut Tüm Özellikler

### Temel Özellikler
✅ Kullanıcı Kaydı  
✅ Kullanıcı Girişi (JWT)  
✅ Token ile `/me` endpoint’i  
✅ LoginAttempt kayıtları  

### Güvenlik Özellikleri
✅ RiskDataPacket yapısı  
✅ Risk skoru üretimi  
✅ OTP doğrulamalı MFA  
✅ Decoy response  
✅ Trust score güncelleme  

### Veritabanı Özellikleri
✅ SQLAlchemy ORM  
✅ Flask-Migrate migration desteği  
✅ SQLite ile çalışma  

---

## 📁 Oluşturulan / Düzenlenen Dosyalar

### ➕ Yeni Dosyalar
1. **`app/risk_engine.py`**
   - Risk skoru hesaplama
   - Aksiyon kararı verme
   - Trust score güncelleme

2. **`app/mfa_otp.py`**
   - OTP üretimi
   - OTP doğrulama

3. **`tests/`**
   - `test_auth_basic.py`
   - `test_mfa_flow.py`
   - `test_risk_engine_unit.py`

4. **`pytest.ini`**
   - Test ortamı konfigürasyonu

---

### ✏️ Düzenlenen Dosyalar
1. **`app/auth_routes.py`**
   - Login akışına risk analizi eklendi
   - MFA endpoint’leri eklendi
   - Decoy yanıt eklendi

2. **`app/models.py`**
   - MFA alanları eklendi:
     - `mfa_code_hash`
     - `mfa_expires_at`
     - `mfa_pending`

3. **`app/risk_data.py`**
   - RiskDataPacket yapısı uyumlu hale getirildi

4. **`migrations/versions/9a01_add_mfa_otp_fields.py`**
   - MFA alanları için migration

---

## 🚀 Programı Çalıştırma

### 1️⃣ Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt

Not: Windows + Python 3.13 ortamında psycopg2-binary kurulum hatası verebilir. SQLite kullanıldığı için bu paket kaldırılabilir.

2️⃣ Veritabanı Migration’larını Çalıştırın
set FLASK_APP=run.py
python -m flask db upgrade

3️⃣ Programı Başlatın
python run.py
http://localhost:5001

🧪 Test Senaryoları
🔹 Otomatik Test

pytest -q
Beklenen: 4 passed


🔹 Manuel Test – MFA Akışı
OTP Talebi

curl -X POST http://localhost:5001/api/auth/mfa/request ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\"}"

OTP Doğrulama
curl -X POST http://localhost:5001/api/auth/mfa/verify ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"code\":\"<DEV_OTP>\"}"

🔌 API Endpoint'leri
Base URL


http://localhost:5001
POST /api/auth/register

POST /api/auth/login
GET /api/auth/me
POST /api/auth/mfa/request
POST /api/auth/mfa/verify

## 🎨 Görsel Test Arayüzü

### Test Sayfası Kullanımı

1. **Programı Başlatın:**
```bash
# Migration'ları çalıştırın (eğer yapılmadıysa)
export FLASK_APP=run.py
flask db upgrade

# Programı başlatın
python run.py
```

2. **Test Sayfasını Açın:**
   - Tarayıcınızda `test.html` dosyasını açın
   - Veya: `open test.html` (macOS) / `start test.html` (Windows)

3. **Test Senaryoları:**

✅ Sağlık Kontrolü: Sunucunun ayakta olup olmadığı kontrol edilir
✅ Kullanıcı Kaydı: Yeni kullanıcı oluşturulur
✅ Giriş Yap: Normal giriş akışı test edilir
✅ Risk Analizi: Giriş sırasında risk skoru ve aksiyon (SAFE / MFA / DECOY) gözlemlenir
✅ MFA Akışı: OTP talep edilir ve doğrulama yapılır
✅ Decoy Yanıt: Yüksek riskli girişte sahte (decoy) response görüntülenir

### Test Sayfası Özellikleri
- 🎨 Modern ve kullanıcı dostu arayüz
- ✅ Başarılı işlemler için yeşil mesajlar
- ❌ Hatalar için kırmızı mesajlar
- 📊 JSON response'ları görüntüleme
- 🔐 Token otomatik saklama (localStorage)
- ⏱️ Progressive lock sürelerini görüntüleme

---