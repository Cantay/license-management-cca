# Spreadsheet Dashboard Helpdesk

Helpdesk modülü için gelişmiş spreadsheet dashboard ve özel formüller.

## Özellikler

### Özel Formüller

1. **ODOO.HELPDESK.COUNT(team_id, stage_id, user_id, priority)**
   - Kriterlere göre ticket sayısı
   - Örnek: `=ODOO.HELPDESK.COUNT(1, 5)` (Takım 1, Stage 5)

2. **ODOO.HELPDESK.OPEN(team_id)**
   - Açık ticket sayısı
   - Örnek: `=ODOO.HELPDESK.OPEN()` veya `=ODOO.HELPDESK.OPEN(1)`

3. **ODOO.HELPDESK.CLOSED(team_id)**
   - Kapalı ticket sayısı
   - Örnek: `=ODOO.HELPDESK.CLOSED()`

4. **ODOO.HELPDESK.MAINTENANCE(team_id)**
   - Bakım anlaşmalı ticket sayısı
   - Örnek: `=ODOO.HELPDESK.MAINTENANCE()`

5. **ODOO.HELPDESK.FREESUPPORT(team_id)**
   - Ücretsiz destek kapsamındaki ticket sayısı
   - Örnek: `=ODOO.HELPDESK.FREESUPPORT()`

6. **ODOO.HELPDESK.AVG.CLOSE(team_id)**
   - Ortalama kapatma süresi (gün)
   - Örnek: `=ODOO.HELPDESK.AVG.CLOSE()` veya `=ODOO.HELPDESK.AVG.CLOSE(1)`

7. **ODOO.HELPDESK.TOP_CUSTOMER_NAME(rank, team_id, include_closed)**
   - Ticket sayısına göre sıralı müşteri adı (varsayılan sadece açık ticketlar)
   - Örnek: `=ODOO.HELPDESK.TOP_CUSTOMER_NAME(1)`

8. **ODOO.HELPDESK.TOP_CUSTOMER_COUNT(rank, team_id, include_closed)**
   - İlgili sıradaki müşterinin ticket adedi
   - Örnek: `=ODOO.HELPDESK.TOP_CUSTOMER_COUNT(1)`

9. **ODOO.LICENSE.TOP_DEALER_NAME(rank, state, program_id)**
   - Aktif lisans adetlerine göre bayi adı (`state` varsayılan `active`)
   - Örnek: `=ODOO.LICENSE.TOP_DEALER_NAME(1)`

10. **ODOO.LICENSE.TOP_DEALER_COUNT(rank, state, program_id)**
    - İlgili sıradaki bayinin lisans adedi
    - Örnek: `=ODOO.LICENSE.TOP_DEALER_COUNT(1)`

11. **ODOO.LICENSE.COUNT / ACTIVE / EXPIRING / EXPIRED (dealer_id)**
    - Toplam ve durum bazlı lisans sayıları

## Kurulum

1. Modülü Odoo addons klasörüne kopyalayın
2. Odoo'yu yeniden başlatın
3. Apps menüsünden modülü kurun
4. Dashboards > Helpdesk Tickets, Helpdesk Performance veya License Health ekranlarına gidin

## Dashboard Özelleştirme

Dashboard'u düzenlemek için:
1. Edit moduna geçin
2. Özel formülleri kullanın
3. Pivot/List ekleyin
4. Grafikler oluşturun

### Hazır Dashboardlar

- **Helpdesk Tickets**: Ticket ve lisans genel görünümü
- **Helpdesk Performance**: KPI kartları ve en çok ticket açan müşteriler
- **License Health**: Lisans durum kartları ve en çok aktif lisansa sahip bayiler

## Lisans

LGPL-3
