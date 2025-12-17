# Fundanur Öztürk – Backend Katkıları (Adaptive Access System)

Bu doküman, Adaptive Access System projesi kapsamında backend tarafında tarafımdan gerçekleştirilen çalışmaları özetlemektedir. Çalışmalar, projenin ilk haftalarındaki temel altyapıdan başlayarak, risk analizi, güvenlik mekanizmaları ve final sprintte yapılan koruma ve kurtarma senaryolarına kadar uzanmaktadır.

---

## 1. Genel Backend Altyapısı (Week 1–2)

- Flask tabanlı backend mimarisi kuruldu.
- PostgreSQL veritabanı entegrasyonu gerçekleştirildi.
- SQLAlchemy ve Flask-Migrate kullanılarak veritabanı modelleri ve migration yapısı oluşturuldu.
- Kullanıcı kimlik doğrulama altyapısı geliştirildi:
  - Kullanıcı kayıt (register)
  - Giriş (login)
  - Yetkili kullanıcı bilgisi alma (`/me`)
- JWT tabanlı access ve refresh token yapısı implemente edildi.
- Kullanıcı ve giriş denemelerini takip eden temel modeller oluşturuldu:
  - `User`
  - `LoginAttempt`

---

## 2. Risk Analizi ve Davranışsal Değerlendirme (Week 3)

- Kural tabanlı (rule-based) bir **risk engine** geliştirildi.
- Login işlemleri sırasında aşağıdaki faktörlere göre risk puanı hesaplandı:
  - IP adresi değişimi
  - User-Agent (cihaz/tarayıcı) değişimi
  - Alışılmadık giriş zamanı
  - Önceki başarısız giriş denemeleri
- Her login denemesi için:
  - `risk_score`
  - `risk_level` (safe / suspicious / critical)
  bilgileri hesaplanıp veritabanına kaydedildi.
- Backend’den frontend’e yönlendirme amacıyla `ui_state` bilgisi üretildi:
  - `normal`
  - `mfa`
  - `decoy`
- Bu risk altyapısı, projenin ilerleyen haftalarında ekip tarafından genişletilecek mekanizmalar için temel oluşturdu.

---

## 3. Emergency Lock ve Oturum Güvenliği (Week 4)

- Kullanıcı hesapları için **Emergency Lock** mekanizması geliştirildi.
- Hesap kilitlendiğinde:
  - Kullanıcının login yapması engellendi.
  - Mevcut oturumlar geçersiz hale getirildi.
- JWT içinde kullanılan **token_version (tv)** alanı ile:
  - Eski token’ların otomatik olarak geçersiz sayılması sağlandı.
- `/emergency-lock` endpoint’i ile kullanıcı kendi hesabını manuel olarak kilitleyebilir hale getirildi.
- Kilitli hesapların protected endpoint’lere erişimi backend seviyesinde engellendi.
- Bu mekanizma, daha sonra eklenen otomatik güvenlik tetikleyicileri için yeniden kullanılabilir bir yapı sundu.

---

## 4. Brute-Force Koruması ve Kurtarma Mekanizması (Week 5)

- Temel bir **brute-force saldırı koruması** eklendi:
  - Belirli sayıda (ör. 5) başarısız login denemesinden sonra hesap otomatik olarak kilitlenmektedir.
- Brute-force tetiklenme sebebi, login attempt kayıtlarına risk açıklaması olarak eklendi.
- Demo ve test senaryoları için **admin destekli unlock** mekanizması geliştirildi:
  - Admin anahtarı (`ADMIN_UNLOCK_KEY`) ile hesap kilidi kaldırılabilmektedir.
  - Unlock işlemi sırasında eski oturumlar geçersiz hale getirilmektedir.
- Lock → unlock → yeniden login senaryosu uçtan uca test edilmiştir.
- Ortam değişikliklerinde (yeni kurulum, zip üzerinden çalışma) migration ve environment uyumluluğu sağlanmıştır.

---

## 5. Genel Sonuç

Bu çalışmalar sonucunda:
- Backend güvenlik akışları uçtan uca çalışan bir hale getirilmiştir.
- Risk bazlı erişim, oturum geçersizleştirme ve hesap kilitleme senaryoları başarıyla uygulanmıştır.
- Sistem, hem demo hem de genişletilebilir akademik proje gereksinimlerini karşılayacak düzeye ulaşmıştır.

Backend tarafındaki bu altyapı, ekip arkadaşlarının frontend ve ek güvenlik mekanizmaları geliştirmesi için sağlam bir temel oluşturmuştur.
