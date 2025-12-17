# Emir Branch - Özellikler ve Kullanım Kılavuzu

## 📋 İçindekiler
1. [Week 1-2](#week-1-2)
2. [Week 3](#week-3)
3. [Week 4](#week-4)
4. [Oluşturulan/Düzenlenen Dosyalar](#oluşturulandüzenlenen-dosyalar)
5. [Programı Çalıştırma](#programı-çalıştırma)
6. [Test Senaryoları](#test-senaryoları)
7. [API Endpoint'leri](#api-endpointleri)
8. [Dosya İçerikleri](#dosya-içerikleri)
9. [Sistem Analizi](#sistem-analizi)

---

## 📅 Week 1-2

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
- Flask request'ten otomatik oluşturulur
- Dictionary formatına dönüştürülebilir
- Her login denemesinde oluşturulur

### 4. Standart Error Handling
- Tüm hatalar tek tip JSON formatında döndürülür
- HTTP status code → UI error message eşleştirmesi
- Özel hata mesajları ve ek veri desteği
- Hata kodları: 400, 401, 403, 404, 409, 423, 429, 500
- Frontend entegrasyonu için hazır format

### 5. Temel Özellikler
✅ **Kullanıcı Kaydı** - Email ve şifre ile kayıt

✅ **Kullanıcı Girişi** - JWT token tabanlı authentication

✅ **Token Doğrulama** - Access token ve refresh token

✅ **Kullanıcı Bilgileri** - Token ile korumalı endpoint

### 6. Güvenlik Özellikleri
✅ **Progressive Lock** - İlerlemeli hesap kilitleme

✅ **MFA Tetikleme** - IP/cihaz değişikliği tespiti

✅ **Şifre Hashleme** - bcrypt ile güvenli şifre saklama

✅ **Login Attempt Tracking** - Tüm giriş denemeleri kaydedilir

✅ **Risk Score Tracking** - Risk skoru alanları hazır (ileride kullanılacak)

### 7. API Özellikleri
✅ **RESTful API** - Standart REST endpoint'leri

✅ **JSON Response** - Tüm response'lar JSON formatında

✅ **Error Handling** - Standart hata yönetimi

✅ **Health Check** - Sistem durumu kontrolü

✅ **Root Endpoint** - API bilgileri ve endpoint listesi

### 8. Veritabanı Özellikleri
✅ **SQLAlchemy ORM** - Veritabanı yönetimi

✅ **Flask-Migrate** - Database migration desteği

✅ **SQLite/PostgreSQL** - Esnek veritabanı desteği

✅ **Login Attempt History** - Giriş geçmişi kayıtları

---

## ✅ Week 3

### 1. Risk Flag'lerin Netleştirilmesi
- Login response'da IP değişimi ve cihaz değişimi bilgisinin risk flag olarak açık ve okunur şekilde tutulması
- `ip_changed` ve `device_changed` flag'lerinin response'a eklenmesi
- Backend iç akışında bu bilgilerin risk flag olarak netleştirilmesi
- `compute_risk_from_last_success` fonksiyonu artık `ip_changed` ve `device_changed` boolean flag'lerini döndürüyor
- Login response'da risk flag'leri açık şekilde görünüyor: `{"ip_changed": true/false, "device_changed": true/false}`

### 2. RiskDataPacket Kullanımının Doğrulanması
- RiskDataPacket'in her login denemesinde (başarılı/başarısız) kesin olarak oluşturulduğunun doğrulanması
- RiskDataPacket'in kullanılabilir olduğunun garantilenmesi
- Açıklayıcı yorum satırları eklendi: "Her login denemesinde kesin olarak oluşturulur ve kullanılabilir"
- RiskDataPacket'in `user_id`'si login akışında güncelleniyor

### 3. Login Attempt Kayıtlarına Açıklayıcı Yorumlar
- Login attempt kayıtlarının gelecekte risk analizi için kullanılacağını açıklayan yorumlar eklendi
- Her login denemesinin (başarılı/başarısız) neden kaydedildiğinin açıklanması
- `LoginAttempt` modeline detaylı docstring eklendi
- Her alanın risk analizindeki rolü açıklandı (IP değişimi, cihaz değişimi, konum, zaman analizi için)

### 4. Test Arayüzü Güncellemeleri
- `test.html` dosyası güncellendi - yeni risk flag'leri gösteriliyor
- Risk analizi bilgileri (risk_level, risk_score, risk_reasons) görüntüleniyor
- Yeni "Risk Analizi Testi" bölümü eklendi - farklı User-Agent ile test yapılabiliyor
- Response formatı güncellendi (`{ok: true, data: {...}}` formatına uyumlu)

### 5. Kod Temizliği
- Gereksiz test scripti (`test_new_features.sh`) silindi
- Tüm değişiklikler küçük, açıklayıcı ve sade dokunuşlar olarak yapıldı

### Sprint Hedefleri
- ✅ Risk-related login metadata validated and stabilized
- ✅ IP and device change indicators clarified for future risk evaluation
- ✅ Login attempt records verified for analysis readiness
- ✅ System prepared for Risk Engine scoring implementation

### Notlar
- ⚠️ Yeni risk scoring EKLEMEDİK (sadece mevcut yapı netleştirildi)
- ⚠️ GeoIP veya zaman analizi EKLEMEDİK (sadece mevcut veriler hazırlandı)
- ✅ Mevcut çalışan kod bozulmadı
- ✅ Küçük, açıklayıcı, sade dokunuşlar yapıldı

---

## ✅ Week 4

### 1. Basit Risk Sınıflandırması
- `classify_risk_simple()` fonksiyonu eklendi
- Sadece IP ve cihaz değişimine bakarak risk seviyesi belirleniyor
- `ip_changed` veya `device_changed` true ise → `risk_level = "suspicious"`
- Aksi halde → `risk_level = "safe"`
- Basit tutulmasının nedeni açıklandı (Week 5'te genişletilecek)

### 2. Risk Level'in Authentication Akışında Kullanımı
- Risk level bilgisi login response'a eklendi
- Authentication decision için kullanılabilir hale getirildi
- `classify_risk_simple()` fonksiyonu authentication akışında kullanılıyor
- Risk level response'da açık şekilde görünüyor

### 3. Risk Sonucuna Göre Sistem Davranışı
- **SAFE** → Normal login (token verilir)
- **SUSPICIOUS** → MFA zorunlu (401 MFA_REQUIRED hatası döner)
- SUSPICIOUS durumunda `require_mfa = True` olarak ayarlanıyor
- User modelindeki `require_mfa` alanı risk seviyesine göre güncelleniyor
- Mevcut MFA yapısı kullanılıyor

### 4. Kod Yapısı
- Basit ve sade kod yapısı
- Yeni kompleks scoring eklenmedi
- GeoIP, zaman analizi veya ağırlıklı puanlama eklenmedi
- Mevcut dosyalar içinde küçük fonksiyonlar eklendi (`classify_risk_simple`)
- Mevcut `compute_risk_from_last_success` fonksiyonu korundu

### 5. Dokümantasyon ve Yorumlar
- Risk sınıflandırmasının neden basit tutulduğu açıklandı
- Week 5'te genişletileceği not edildi
- Fonksiyon docstring'leri eklendi
- Kod içinde açıklayıcı yorumlar eklendi

### Sprint Backlog - Tamamlanma Durumu
- ✅ **Introduce basic risk classification logic (safe vs suspicious)** - `classify_risk_simple()` fonksiyonu eklendi
- ✅ **Connect risk outcomes with authentication decisions** - Risk level'e göre MFA zorunlu hale getirildi
- ✅ **Ensure consistent propagation of risk states through the system** - Risk state'leri tüm akışta tutarlı şekilde yayılıyor
- ✅ **Validate system behavior under different login scenarios** - Farklı login senaryoları test edildi
- ✅ **Prepare structure for more advanced risk scoring in the final sprint** - Week 5 için yapı hazırlandı

### Sprint Hedefleri
- ✅ Basit risk sınıflandırma mantığı eklendi
- ✅ Risk level authentication akışında kullanılabilir hale getirildi
- ✅ Risk sonucuna göre sistem davranışı netleştirildi
- ✅ Kodlar sade ve okunabilir tutuldu
- ✅ Risk evaluation results consistently propagated through backend flow
- ✅ Multiple login scenarios tested and validated

### Increment Log (Release Notes)
- ✅ Basic risk classification logic introduced
- ✅ Risk evaluation connected with authentication flow
- ✅ System reactions adjusted based on evaluated risk
- ✅ Multiple risk scenarios tested and validated
- ✅ Infrastructure prepared for final risk scoring improvements

### Test Arayüzü Güncellemeleri
- ✅ `test.html` güncellendi - MFA_REQUIRED durumu özel olarak gösteriliyor
- ✅ Risk sınıflandırması test bölümü güncellendi
- ✅ SUSPICIOUS durumunda MFA zorunlu mesajı eklendi
- ✅ Risk flag'leri ve risk level bilgileri görüntüleniyor

### Notlar
- ⚠️ Kompleks risk scoring EKLEMEDİK (sadece basit sınıflandırma)
- ⚠️ GeoIP veya zaman analizi EKLEMEDİK
- ⚠️ Ağırlıklı puanlama EKLEMEDİK
- ✅ Mevcut çalışan kod bozulmadı
- ✅ Basit, sade ve okunabilir kod yapısı korundu
- ✅ Logic simple and interpretable - sistem maintainable
- 📝 Week 5'te daha gelişmiş risk scoring eklenecek

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
   - RiskDataPacket oluşturma eklendi (her login denemesinde)
   - IP ve cihaz değişimi risk flag'leri eklendi (`ip_changed`, `device_changed`)
   - Login attempt kayıtlarına açıklayıcı yorumlar eklendi
   - Basit risk sınıflandırması eklendi (`classify_risk_simple`)
   - SUSPICIOUS durumunda MFA zorunlu hale getirildi
   - Risk level'e göre authentication decision yapılıyor
   - Standart error handling kullanılıyor

3. **`app/__init__.py`** - Root path endpoint eklendi

4. **`run.py`** - Port yapılandırması eklendi (varsayılan: 5001)

---

## 🚀 Programı Çalıştırma

### Adım 1: Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

**Not:** Anaconda Python kullanılıyorsa venv gerekmez.

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

#### 6. Risk Sınıflandırması Testi (SUSPICIOUS → MFA)
```bash
# İlk giriş (normal - SAFE)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}'

# Farklı User-Agent ile giriş (SUSPICIOUS → MFA gerektirir)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -H "User-Agent: DifferentBrowser/1.0" \
  -d '{"email":"test@example.com","password":"test12345"}'
```
**Beklenen:** `401 MFA_REQUIRED` - `{"error": "MFA_REQUIRED", "message": "Multi-factor authentication required due to suspicious activity.", "require_mfa": true}`

#### 7. Kullanıcı Bilgilerini Görüntüleme
```bash
# Önce login yapıp token alın
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}' | jq -r '.data.access_token')

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
    "ok": true,
    "data": {
      "access_token": "...",
      "refresh_token": "...",
      "token_type": "Bearer",
      "risk_level": "safe",
      "risk_score": 0.0,
      "ui_state": "normal",
      "alert_type": "none",
      "message_key": "auth.safe",
      "ip_changed": false,
      "device_changed": false,
      "require_mfa": false
    }
  }
  ```
- **Errors:**
  - `400` - Email/şifre eksik
  - `401` - Geçersiz kimlik bilgileri veya MFA gerekli (MFA_REQUIRED)
  - `423` - Hesap kilitli
  - `429` - Çok fazla deneme

#### 5. Kullanıcı Bilgileri
- **GET** `/api/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`
  ```json
  {
    "ok": true,
    "data": {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2025-12-03T...",
      "is_active": true,
      "is_locked": false,
      "locked_until": null,
      "token_version": 0
    }
  }
  ```
- **Errors:**
  - `401` - Token eksik veya geçersiz

---

## 📄 Dosya İçerikleri

### Yeni Dosyalar

**app/lock_utils.py** - Progressive lock mekanizması için utility fonksiyonları:
- `check_account_lock()`: Hesabın kilitli olup olmadığını kontrol eder
- `apply_progressive_lock()`: Hatalı giriş sayısına göre kilit uygular
- `get_lock_status_message()`: Kullanıcıya gösterilecek mesajı döndürür

**app/risk_data.py** - RiskDataPacket dataclass yapısı:
- IP adresi, cihaz bilgisi, giriş zamanı, konum bilgisi içerir
- Flask request'ten otomatik oluşturulur
- Her login denemesinde (başarılı/başarısız) kesin olarak oluşturulur ve kullanılabilir
- Risk Engine'e aktarılacak veriyi temsil eder
- Açıklayıcı yorumlar eklendi

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
   - ✅ **Giriş Yap:** Başarılı giriş test edin (risk flag'leri görüntülenir)
   - ✅ **Kullanıcı Bilgileri:** Token ile bilgileri görüntüleyin
   - ✅ **Progressive Lock:** Hatalı giriş denemeleri yapın (3, 5, 7 kez)
   - ✅ **Risk Analizi Testi:** Farklı User-Agent ile giriş yaparak risk sınıflandırmasını test edin
   - ✅ **MFA Zorunluluğu Testi:** SUSPICIOUS durumunda MFA_REQUIRED hatasını test edin

### Test Sayfası Özellikleri
- 🎨 Modern ve kullanıcı dostu arayüz
- ✅ Başarılı işlemler için yeşil mesajlar
- ❌ Hatalar için kırmızı mesajlar
- 📊 JSON response'ları görüntüleme
- 🔐 Token otomatik saklama (localStorage)
- ⏱️ Progressive lock sürelerini görüntüleme
- 🚩 Risk flag'leri görüntüleme (ip_changed, device_changed)
- 📈 Risk analizi bilgileri (risk_level, risk_score, risk_reasons)
- 🔍 Risk Analizi Testi bölümü - farklı User-Agent ile test
- 🔐 MFA_REQUIRED durumu özel gösterimi
- ⚠️ SUSPICIOUS durumunda MFA zorunlu mesajı

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

## 🧪 test.html ile Sistem Testi

### Adım 1: Uygulamayı Başlatın
```bash
python run.py
```

### Adım 2: test.html'i Açın
Tarayıcınızda `test.html` dosyasını açın:
- macOS: `open test.html`
- Windows: `start test.html`
- Veya dosyaya çift tıklayın

### Adım 3: Test Senaryoları

#### Test Senaryosu 1: Normal Giriş (SAFE)
1. **Kullanıcı Kaydı** bölümünden yeni bir kullanıcı oluşturun
2. **Giriş Yap** bölümünden aynı bilgilerle giriş yapın
3. **Beklenen Sonuç:**
   - ✅ Giriş başarılı
   - Risk Seviyesi: `safe`
   - IP Değişti: `❌ Hayır`
   - Cihaz Değişti: `❌ Hayır`
   - Token verildi

#### Test Senaryosu 2: Risk Sınıflandırması (SUSPICIOUS → MFA)
1. **Risk Analizi Testi** bölümüne gidin
2. Email ve şifre girin
3. **Farklı bir User-Agent** girin (örn: `DifferentBrowser/2.0`)
4. "Risk Sınıflandırmasını Test Et" butonuna tıklayın
5. **Beklenen Sonuç:**
   - ❌ Hata: `401 MFA_REQUIRED`
   - Risk Seviyesi: `suspicious`
   - IP Değişti veya Cihaz Değişti: `✅ Evet`
   - MFA zorunlu mesajı görünür

#### Test Senaryosu 3: İlk Giriş (SAFE)
1. Yeni bir kullanıcı oluşturun
2. İlk girişi yapın
3. **Beklenen Sonuç:**
   - ✅ Giriş başarılı
   - Risk Seviyesi: `safe` (ilk giriş olduğu için)
   - Token verildi

#### Test Senaryosu 4: Progressive Lock
1. **Progressive Lock Testi** bölümüne gidin
2. Email ve yanlış şifre girin
3. "Hatalı Giriş Dene" butonuna 3 kez tıklayın
4. **Beklenen Sonuç:**
   - 3. denemede: `429 Too Many Attempts`
   - 30 saniye bekleme mesajı

### Özelliklerini Gözlemleme

**test.html'de görebileceğiniz özellikler:**

1. **Risk Sınıflandırması:**
   - Risk seviyesi (`safe` veya `suspicious`) görüntülenir
   - IP ve cihaz değişimi flag'leri gösterilir

2. **MFA Zorunluluğu:**
   - SUSPICIOUS durumunda özel MFA_REQUIRED mesajı
   - Risk detayları (risk_level, risk_score, ip_changed, device_changed) gösterilir

3. **Sistem Davranışı:**
   - SAFE → Normal giriş (token verilir)
   - SUSPICIOUS → MFA zorunlu (401 hatası)

### İpuçları
- Farklı User-Agent'ler deneyerek cihaz değişimini test edebilirsiniz
- Aynı kullanıcı ile birden fazla giriş yaparak IP/cihaz değişimini gözlemleyebilirsiniz
- Risk Analizi Testi bölümü risk özelliklerini test etmek için özel olarak hazırlandı

---

## 🔍 Sistem Analizi

### Sistem Ne Yapıyor?

Bu sistem, **Adaptive Access System** adında bir kimlik doğrulama ve risk tabanlı erişim kontrolü sistemidir. Temel amacı, kullanıcı girişlerini risk seviyesine göre değerlendirip, şüpheli aktiviteleri tespit ederek güvenliği artırmaktır.

**Ana İşlevler:**

1. **Kullanıcı Yönetimi:**
   - Email ve şifre ile kullanıcı kaydı
   - JWT token tabanlı kimlik doğrulama
   - Şifreler bcrypt ile hashleniyor

2. **Güvenlik Mekanizmaları:**
   - **Progressive Lock:** Brute-force saldırılarına karşı kademeli kilitleme (3→30sn, 5→2dk, 7→24saat)
   - **Risk Tabanlı MFA:** IP veya cihaz değişiminde MFA zorunlu hale getiriliyor
   - **Emergency Lock:** Kullanıcı hesabını anında kilitleyebiliyor
   - **Session Invalidation:** Token version ile tüm oturumları geçersiz kılma

3. **Risk Analizi:**
   - Her login denemesinde risk değerlendirmesi yapılıyor
   - IP değişimi, cihaz değişimi gibi sinyaller toplanıyor
   - Basit risk sınıflandırması: SAFE veya SUSPICIOUS
   - Risk sonuçlarına göre sistem davranışı değişiyor

4. **Veri Toplama:**
   - Tüm login denemeleri (başarılı/başarısız) kaydediliyor
   - Risk skoru, risk seviyesi, risk nedenleri saklanıyor
   - Gelecekteki risk analizi için veri hazırlanıyor
