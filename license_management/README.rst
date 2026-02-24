.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://img.shields.io/badge/oca-beta-yellow.svg
   :alt: Beta
.. image:: https://img.shields.io/badge/odoo--version-18.0-lightgreen.svg
   :alt: Odoo 18.0

==============
Lisans Yönetimi
==============

Bu modül, yazılım lisanslarını, abonelikleri ve bayi (dealer) ağını yönetmek için kapsamlı bir çözüm sunar. Odoo üzerinde lisans tabanlı ürün ve hizmet satan işletmeler için tasarlanmıştır.

**Temel Özellikler**
-------------------

*   **Gelişmiş Bayi Yönetimi:**
    *   Partner kayıtlarını "Bayi" olarak işaretleme.
    *   Her bayi için özel bayi kodu, başlangıç tarihi ve tabela adı gibi alanlar.
    *   Bayilere özel fiyat listeleri ve indirim oranları tanımlama.
    *   Bayilerin müşteri ve lisans sayılarını kolayca takip etme.

*   **Detaylı Lisans Takibi:**
    *   Her lisans için benzersiz bir lisans numarası ve anahtarı.
    *   Lisansların başlangıç ve bitiş tarihlerine göre otomatik durum takibi (Taslak, Aktif, Süresi Yaklaşıyor, Süresi Doldu, İptal).
    *   Lisans süresine göre kalan günleri ve doluluk oranını gösteren ilerleme çubuğu.
    *   Müşteri, bayi, ürün ve lisans süresi bazında detaylı lisans kayıtları.

*   **Ürün ve Program Entegrasyonu:**
    *   Ürünleri "Lisans Ürünü" olarak tanımlama ve lisans programlarıyla ilişkilendirme.
    *   Her ürün için izin verilen lisans sürelerini (1 Ay, 1 Yıl vb.) belirleme.
    *   Lisans programları oluşturarak ürünleri kategorize etme.

*   **Raporlama ve Analiz:**
    *   Genel durumu özetleyen interaktif bir **Dashboard**.
    *   Aktif lisans sayısı, süresi yaklaşanlar, toplam ciro gibi anlık veriler.
    *   Lisansları bayi, müşteri, ürün ve duruma göre gruplandırarak pivot ve grafik analizleri yapma.

*   **Otomasyon ve Bildirimler:**
    *   Süresi dolmak üzere olan lisanslar için müşterilere ve bayilere otomatik e-posta bildirimleri gönderen zamanlanmış görev (Cron Job).
    *   Lisans yenileme işlemlerini kolaylaştıran sihirbaz (wizard).
    *   Otomatik yenileme seçeneği.

*   **Güvenlik ve Erişim Kontrolü:**
    *   Lisans verilerine erişim için "Kullanıcı" ve "Yönetici" rolleri.
    *   Sadece yetkili kullanıcıların yapılandırma menülerine erişimi.

Kurulum
=======

Bu modülü kurmak için:

1.  Modül klasörünü Odoo `addons` dizininize ekleyin.
2.  Odoo'yu geliştirici modunda yeniden başlatın.
3.  **Uygulamalar** menüsüne gidin, "Uygulama Listesini Güncelle" seçeneğine tıklayın.
4.  Arama çubuğuna "License Management" yazın ve modülü bulun.
5.  "Kur" butonuna tıklayın.


Yapılandırma
============

Modülü kurduktan sonra temel yapılandırmayı yapmak için:

1.  **Lisans Yönetimi > Yapılandırma > Lisans Programları** menüsüne giderek sattığınız yazılım veya hizmet gruplarını (örn: Muhasebe Programı, CRM Yazılımı) oluşturun.
2.  **Lisans Yönetimi > Yapılandırma > Lisans Süreleri** menüsünden geçerli lisans periyotlarını (örn: 1 Aylık Deneme, 1 Yıllık Standart, 3 Yıllık Premium) tanımlayın.
3.  **Satış > Ürünler** menüsünden lisans olarak satacağınız ürünleri düzenleyin. "Satış" sekmesi altında "Lisans Ürünü mü?" seçeneğini işaretleyip ilgili "Lisans Programı" ve "İzin Verilen Süreler"i seçin.
4.  **Kişiler** uygulamasından bayilerinizi oluşturun ve "Satış ve Satın Alma" sekmesinde veya özel "Lisans Bilgileri" sayfasında "Bayi mi?" seçeneğini işaretleyin.

Kullanım
========

*   **Yeni Lisans Oluşturma:**
    *   `Lisans Yönetimi > Lisanslar` menüsüne gidin ve "Oluştur" butonuna tıklayın.
    *   İlgili bayi, müşteri, ürün ve lisans süresini seçin. Başlangıç ve bitiş tarihleri otomatik olarak hesaplanacaktır.
    *   Kaydı kaydedin.

*   **Dashboard'u Görüntüleme:**
    *   `Lisans Yönetimi > Dashboard` menüsüne tıklayarak lisanslarınızın genel durumunu, istatistikleri ve grafikleri görüntüleyin.

*   **Lisans Yenileme:**
    *   Süresi dolmuş veya dolmak üzere olan bir lisansın form görünümünde "Yenile" butonuna tıklayın. Açılan pencerede yeni süre ve tutar bilgilerini girerek lisansı kolayca yenileyin.

Hata Bildirimi
==============

Hatalar GitHub Issues üzerinden takip edilmektedir. Eğer bir hatayla karşılaşırsanız, lütfen burada bir kayıt oluşturun:
(Buraya projenizin GitHub Issues linkini ekleyebilirsiniz)

Katkıda Bulunanlar
==================

*   Lugatsoft

Lisans
======

LGPL-3
