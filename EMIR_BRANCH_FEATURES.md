# Emir Branch - Özellikler ve Kullanım Kılavuzu

## 📋 İçindekiler
1. [Eklenen Özellikler](#eklenen-özellikler)
2. [Mevcut Tüm Özellikler](#mevcut-tüm-özellikler)
3. [Oluşturulan/Düzenlenen Dosyalar](#oluşturulandüzenlenen-dosyalar)
4. [Programı Çalıştırma](#programı-çalıştırma)
5. [Test Senaryoları](#test-senaryoları)
6. [API Endpoint'leri](#api-endpointleri)
7. [Dosya İçerikleri](#dosya-içerikleri)

---

## 🎯 Eklenen Özellikler

### 1. Progressive Lock (İlerlemeli Kilitleme) Mekanizması
- **3 hatalı giriş** → 30 saniye bekleme süresi (429 Too Many Attempts)
- **5 hatalı giriş** → 2 dakika geçici hesap kilidi (423 Locked)
- **7 hatalı giriş** → 24 saat geçici tam hesap kilidi (423 Locked)
- Başarılı girişte kilit otomatik kaldırılır
- Kilit süresi dolduğunda otomatik açılır
- Her login denemesi veritabanında kaydedilir

### 2. MFA (Multi-Factor Authentication) Tetikleme
- **IP değişikliği** tespit edildiğinde MFA gerektirir
- **Cihaz bilgisi değişikliği** tespit edildiğinde MFA gerektirir
- İlk girişte MFA gerekmez (henüz kayıt yok)
- Normal girişlerde MFA gerekmez
- Başarılı girişte IP ve cihaz bilgisi güncellenir

### 3. RiskDataPacket Yapısı
- IP adresi, cihaz bilgisi, giriş zamanı, konum bilgisi içerir
- Week 3'te Risk Engine'e aktarılacak veriyi temsil eder
- Flask request'ten otomatik oluşturulur
- Dictionary formatına dönüştürülebilir
- Her login denemesinde oluşturulur

### 4. Standart Error Handling
- Tüm hatalar tek tip JSON formatında döndürülür
- HTTP status code → UI error message eşleştirmesi
- Özel hata mesajları ve ek veri desteği
- Hata kodları: 400, 401, 403, 404, 409, 423, 429, 500
- Frontend entegrasyonu için hazır format

---

## 📊 Mevcut Tüm Özellikler

### Temel Özellikler
✅ **Kullanıcı Kaydı** - Email ve şifre ile kayıt
✅ **Kullanıcı Girişi** - JWT token tabanlı authentication
✅ **Token Doğrulama** - Access token ve refresh token
✅ **Kullanıcı Bilgileri** - Token ile korumalı endpoint

### Güvenlik Özellikleri
✅ **Progressive Lock** - İlerlemeli hesap kilitleme
✅ **MFA Tetikleme** - IP/cihaz değişikliği tespiti
✅ **Şifre Hashleme** - bcrypt ile güvenli şifre saklama
✅ **Login Attempt Tracking** - Tüm giriş denemeleri kaydedilir
✅ **Risk Score Tracking** - Risk skoru alanları hazır (ileride kullanılacak)

### API Özellikleri
✅ **RESTful API** - Standart REST endpoint'leri
✅ **JSON Response** - Tüm response'lar JSON formatında
✅ **Error Handling** - Standart hata yönetimi
✅ **Health Check** - Sistem durumu kontrolü
✅ **Root Endpoint** - API bilgileri ve endpoint listesi

### Veritabanı Özellikleri
✅ **SQLAlchemy ORM** - Veritabanı yönetimi
✅ **Flask-Migrate** - Database migration desteği
✅ **SQLite/PostgreSQL** - Esnek veritabanı desteği
✅ **Login Attempt History** - Giriş geçmişi kayıtları

---

## 📁 Oluşturulan/Düzenlenen Dosyalar

### Yeni Dosyalar:
1. **`app/lock_utils.py`** - Progressive lock mekanizması fonksiyonları
2. **`app/risk_data.py`** - RiskDataPacket dataclass yapısı
3. **`app/error_handlers.py`** - Standart error response formatı
4. **`app/mfa_utils.py`** - MFA tetikleme kontrol fonksiyonları
5. **`migrations/versions/727e20610b00_add_progressive_lock_and_mfa_fields.py`** - Database migration

### Düzenlenen Dosyalar:
1. **`app/models.py`** - User modeline yeni alanlar eklendi:
   - `locked_until` (DateTime) - Hesap kilidinin bitiş zamanı
   - `last_ip` (String) - Son başarılı giriş IP adresi
   - `last_device_info` (String) - Son başarılı giriş cihaz bilgisi
   - `require_mfa` (Boolean) - MFA gerekip gerekmediği

2. **`app/auth_routes.py`** - Login endpoint'i güncellendi:
   - Progressive lock kontrolü eklendi
   - MFA tetikleme kontrolü eklendi
   - RiskDataPacket oluşturma eklendi
   - Standart error handling kullanılıyor

3. **`app/__init__.py`** - Root path endpoint eklendi

4. **`run.py`** - Port yapılandırması eklendi (varsayılan: 5001)

---

## 🚀 Programı Çalıştırma

### Adım 1: Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

**Not:** Anaconda Python kullanılıyor, venv gerekmez.

### Adım 2: Veritabanı Migration'larını Çalıştırın
```bash
export FLASK_APP=run.py
flask db upgrade
```

Bu komut veritabanı tablolarını oluşturur ve yeni alanları ekler.

### Adım 3: Programı Başlatın
```bash
python run.py
```

Program **http://localhost:5001** adresinde çalışacaktır.

**Not:** 
- Port 5000 macOS AirPlay Receiver tarafından kullanılıyorsa, program otomatik olarak port 5001'i kullanır
- Farklı bir port kullanmak için: `PORT=8080 python run.py`
- Program arka planda çalıştırmak için: `python run.py &`

### Program Çalışıyor mu Kontrol Edin
```bash
curl http://localhost:5001/api/health
```

**Beklenen:** `{"status": "ok"}`

---

## 🧪 Test Senaryoları

### Hızlı Test Komutları

#### 1. Kullanıcı Kaydı
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}'
```
**Beklenen:** `201 Created` - `{"message": "Kayıt başarılı."}`

#### 2. Başarılı Giriş
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}'
```
**Beklenen:** `200 OK` - access_token ve refresh_token döner

#### 3. Progressive Lock Testi (3 Hatalı Giriş → 30 saniye)
```bash
# 1. hatalı giriş
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'

# 2. hatalı giriş
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'

# 3. hatalı giriş (30 saniye bekleme uyarısı)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'
```
**Beklenen:** `429 Too Many Attempts` - `{"error": "Too many attempts, please wait", "wait_seconds": 30}`

#### 4. Progressive Lock Testi (5 Hatalı Giriş → 2 dakika kilit)
```bash
# 4. ve 5. hatalı girişler (2 dakika kilit)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'
```
**Beklenen:** `423 Locked` - `{"error": "Account temporarily locked", "remaining_seconds": 120}`

#### 5. Progressive Lock Testi (7 Hatalı Giriş → 24 saat kilit)
```bash
# 6. ve 7. hatalı girişler (24 saat kilit)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'
```
**Beklenen:** `423 Locked` - `{"error": "Account temporarily locked", "remaining_seconds": 86400}`

#### 6. MFA Tetikleme Testi
```bash
# İlk giriş (normal - MFA gerekmez)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}'

# Farklı User-Agent ile giriş (MFA gerektirir)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -H "User-Agent: DifferentBrowser/1.0" \
  -d '{"email":"test@example.com","password":"test12345"}'
```
**Beklenen:** `401 Unauthorized` - `{"error": "Invalid credentials", "message": "Multi-factor authentication required", "require_mfa": true}`

#### 7. Kullanıcı Bilgilerini Görüntüleme
```bash
# Önce login yapıp token alın
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}' | jq -r '.access_token')

# Token ile kullanıcı bilgilerini al
curl -X GET http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```
**Beklenen:** `200 OK` - Kullanıcı bilgileri (id, email, trust_score, require_mfa vb.)

#### 8. Health Check
```bash
curl http://localhost:5001/api/health
```
**Beklenen:** `200 OK` - `{"status": "ok"}`

#### 9. Ana Sayfa
```bash
curl http://localhost:5001/
```
**Beklenen:** `200 OK` - API bilgileri ve endpoint listesi

---

## 🔌 API Endpoint'leri

### Base URL
```
http://localhost:5001
```

### Endpoint'ler

#### 1. Ana Sayfa
- **GET** `/`
- **Response:** API bilgileri ve endpoint listesi

#### 2. Health Check
- **GET** `/api/health`
- **Response:** `{"status": "ok"}`

#### 3. Kullanıcı Kaydı
- **POST** `/api/auth/register`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** `201 Created` - `{"message": "Kayıt başarılı."}`
- **Errors:** 
  - `400` - Email/şifre eksik veya geçersiz
  - `409` - Email zaten kayıtlı

#### 4. Kullanıcı Girişi
- **POST** `/api/auth/login`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** `200 OK`
  ```json
  {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "require_mfa": false
  }
  ```
- **Errors:**
  - `400` - Email/şifre eksik
  - `401` - Geçersiz kimlik bilgileri veya MFA gerekli
  - `423` - Hesap kilitli
  - `429` - Çok fazla deneme

#### 5. Kullanıcı Bilgileri
- **GET** `/api/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2025-12-03T...",
    "trust_score": 0.0,
    "last_login_at": "2025-12-03T...",
    "require_mfa": false
  }
  ```
- **Errors:**
  - `401` - Token eksik veya geçersiz

---

## 📄 Dosya Açıklamaları

### Yeni Dosyalar

**app/lock_utils.py** - Progressive lock mekanizması için utility fonksiyonları:
- `check_account_lock()`: Hesabın kilitli olup olmadığını kontrol eder
- `apply_progressive_lock()`: Hatalı giriş sayısına göre kilit uygular
- `get_lock_status_message()`: Kullanıcıya gösterilecek mesajı döndürür

**app/risk_data.py** - RiskDataPacket dataclass yapısı:
- IP adresi, cihaz bilgisi, giriş zamanı, konum bilgisi içerir
- Flask request'ten otomatik oluşturulur
- Week 3'te Risk Engine'e aktarılacak veriyi temsil eder

**app/error_handlers.py** - Standart error response formatı:
- HTTP status code → UI error message eşleştirmesi
- `error_response()`, `invalid_credentials()`, `account_locked()`, `too_many_attempts()`, `mfa_required()` helper fonksiyonları

**app/mfa_utils.py** - MFA tetikleme kontrol fonksiyonları:
- `should_require_mfa()`: IP veya cihaz değişikliğini kontrol eder
- `update_user_device_info()`: Kullanıcının son IP ve cihaz bilgisini günceller

**migrations/versions/727e20610b00_add_progressive_lock_and_mfa_fields.py** - Database migration:
- `users` tablosuna `locked_until`, `last_ip`, `last_device_info`, `require_mfa` alanlarını ekler

### Düzenlenen Dosyalar

**app/models.py** - User modeline eklenen alanlar:
- `locked_until` (DateTime): Hesap kilidinin bitiş zamanı
- `last_ip` (String): Son başarılı giriş IP adresi
- `last_device_info` (String): Son başarılı giriş cihaz bilgisi
- `require_mfa` (Boolean): MFA gerekip gerekmediği

**app/auth_routes.py** - Login endpoint'i güncellendi:
- Progressive lock kontrolü eklendi
- MFA tetikleme kontrolü eklendi
- RiskDataPacket oluşturma eklendi
- Standart error handling kullanılıyor

**app/__init__.py** - Root path endpoint eklendi

**run.py** - Port yapılandırması eklendi (varsayılan: 5001)

---

## ✅ Main Branch ile Merge Uyumluluğu

### Değişiklik Özeti
- **Yeni Dosyalar (5):** Çakışma riski yok
  - `app/error_handlers.py`
  - `app/lock_utils.py`
  - `app/mfa_utils.py`
  - `app/risk_data.py`
  - `migrations/versions/727e20610b00_add_progressive_lock_and_mfa_fields.py`

- **Düzenlenen Dosyalar (4):** Sadece genişletme, çakışma riski düşük
  - `app/__init__.py` - Sadece root endpoint eklendi
  - `app/auth_routes.py` - Login fonksiyonu genişletildi
  - `app/models.py` - User modeline yeni alanlar eklendi
  - `run.py` - Port yapılandırması eklendi

### Merge Güvenliği
✅ **Çakışma riski çok düşük** çünkü:
- Yeni dosyalar eklendi (çakışma yok)
- Mevcut dosyalar sadece genişletildi (yeni kod eklendi, mevcut kod değiştirilmedi)
- Migration dosyası doğru şekilde oluşturuldu (`down_revision` mevcut)
- `.gitignore` eklendi (venv ve .env ignore ediliyor)

### Merge Komutları
```bash
# Main branch'e geç
git checkout main

# Emir branch'ini merge et
git merge emir

# Eğer çakışma olursa (olması beklenmiyor)
# Çakışmaları çöz ve commit yap
git add .
git commit -m "Merge emir branch: Add progressive lock and MFA features"
```

---

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
   - ✅ **Sağlık Kontrolü:** Sunucunun çalıştığını kontrol edin
   - ✅ **Kullanıcı Kaydı:** Yeni kullanıcı oluşturun
   - ✅ **Giriş Yap:** Başarılı giriş test edin
   - ✅ **Kullanıcı Bilgileri:** Token ile bilgileri görüntüleyin
   - ✅ **Progressive Lock:** Hatalı giriş denemeleri yapın (3, 5, 7 kez)

### Test Sayfası Özellikleri
- 🎨 Modern ve kullanıcı dostu arayüz
- ✅ Başarılı işlemler için yeşil mesajlar
- ❌ Hatalar için kırmızı mesajlar
- 📊 JSON response'ları görüntüleme
- 🔐 Token otomatik saklama (localStorage)
- ⏱️ Progressive lock sürelerini görüntüleme

---

## 📝 Notlar

### Venv ve Ortam Değişkenleri
- **`.gitignore` eklendi:** `venv/` ve `.env` dosyaları Git tarafından takip edilmiyor
- **Herkes kendi ortamını kullanabilir:**
  - ✅ Anaconda Python kullananlar → venv'e gerek yok
  - ✅ Standart Python kullananlar → `python -m venv venv` ile kendi venv'ini oluşturabilir
  - ✅ Her iki durumda da program çalışır
- **Main branch ile uyumlu:** Main'de venv varsa, o sadece o kişinin local'inde var (Git'te olmamalı)
- **Öneri:** Herkes kendi ortamını oluştursun, Git'e commit etmesin

### Diğer Notlar
- Port 5001 varsayılan olarak kullanılıyor (5000 AirPlay tarafından kullanılıyor)
- Tüm kodlar derleniyor ve hatasız çalışıyor
- Migration'lar çalıştırıldı ve veritabanı güncel
- Test sayfası (`test.html`) görsel test için hazır

---

## 🎓 Öğrenme Notları

- Progressive lock mekanizması basit ve etkili bir brute-force koruması sağlar
- MFA tetikleme, şüpheli girişleri tespit eder
- RiskDataPacket yapısı, gelecekteki risk analizi için hazır
- Standart error handling, frontend entegrasyonunu kolaylaştırır

