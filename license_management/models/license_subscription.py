# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)
class LicenseSubscription(models.Model):
    _name = 'license.subscription'
    _description = 'License Subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date desc, id desc'
    # _rec_names_search = ['license_no', 'product_id']
    # _rec_name = 'license_no'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True
    )
    license_no = fields.Char(
        string='License No',
        required=True,
        copy=False,
        default=lambda self: _('New')
    )
    license_key = fields.Char(
        string='License Key',
        copy=False,
        index=True,
        help="The unique key or serial number provided to the customer."
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer (Company/Person)',
        required=True,
        tracking=True,
        domain=[('is_dealer', '=', False)]
    )
    phone = fields.Char(
        related='customer_id.phone',
        readonly=False
    )
    mobile = fields.Char(
        related='customer_id.mobile',
        readonly=False
    )
    signboard_name = fields.Char(
        related='customer_id.signboard_name',
        readonly=False
    )
    category_id = fields.Many2many(
        related='customer_id.category_id',
        string='Customer Categories',
        readonly=False
    )
    contact_person_id = fields.Many2one(
        'res.partner',
        string='Contact Person',
        tracking=True,
        help="The contact person at the customer's company.")

    dealer_id = fields.Many2one(
        'res.partner',
        string='Dealer',
        required=True,
        tracking=True,
        domain=[('is_dealer', '=', True)],
        context={'search_default_dealer_code': True}
    )
    product_type_selector = fields.Selection(
        selection=[
            ('software', 'Program'),
            ('support_package', 'Destek Paketi'),
            ('server_service', 'Sunucu Hizmeti'),
            ('domain_tracking', 'Domain Takibi'),
            ('service', 'Service'),
            ('backup_service','Yedekleme'),
        ],
        string="Product/Service Type",
        help="Select the type of product to filter the list."
    )
    color = fields.Integer(string='Color', default=0, help="Color for kanban view organization")
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        tracking=True
    )
    product_category_id = fields.Many2one(
        'product.category',
        related='product_id.categ_id',
        string='Product Category',
        store=True,
        readonly=True
    )
    program_id = fields.Many2one('license.program', string='Program',
                                related='product_id.product_tmpl_id.license_program_id',
                                store=True)

    # License Details
    program_code = fields.Char(string='Program Code',
                              related='product_id.product_tmpl_id.program_code')
    reference_code = fields.Char(string='Reference Code',
                                related='product_id.product_tmpl_id.reference_code')
    license_term_id = fields.Many2one(
        'license.term', string='License Term', tracking=True)

    # Dates
    start_date = fields.Date(string='Start Date', required=True,
                            default=fields.Date.today, tracking=True)
    end_date = fields.Date(string='End Date', required=False, tracking=True, store=True)
    days_to_expire = fields.Integer(string='Days to Expire',
                                   compute='_compute_days_to_expire')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expiring', 'Expiring Soon'),
        ('urgent', 'Urgent'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True, compute='_compute_state',
        store=True)

    # Integration with subscription_oca
    subscription_id = fields.Many2one('sale.subscription', string='Subscription')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

    # Additional fields
    auto_renew = fields.Boolean(string='Auto Renew', default=False)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company',
                                default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 related='company_id.currency_id')
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        tracking=True,
        help="Pricelist to calculate the license amount"
    )
    use_manual_price = fields.Boolean(string='Use Manual Price', default=False)
    manual_amount = fields.Monetary(
        string='Manual Amount',
        currency_field='currency_id',
        help="Manual price override when not using pricelist"
    )
    amount = fields.Monetary(
        string='License Amount',
        currency_field='currency_id',
        compute='_compute_amount',
        store=True,
        tracking=True
    )

    detail_title = fields.Char(
        string="Details",
        copy=True
    )


    # History
    history_ids = fields.One2many('license.history', 'license_id', string='History')

    is_archived = fields.Boolean(
        string='Archived',
        default=False,
        tracking=True,
        help="If checked, the license is archived and won't appear in regular views"
    )

    expiration_progress = fields.Float(
        string="Expiration Progress (%)",
        compute='_compute_expiration_progress',
        store=True,
        help="Progress of the license towards its expiration date, from 0 to 100."
    )
    free_support_term_id = fields.Many2one(
        'license.term',
        string="Ücretsiz Destek Süresi",
        tracking=True,
        help="Bu lisansla birlikte sunulan ücretsiz destek süresini seçin."
    )
    free_support_end_date = fields.Date(
        string="Ücretsiz Destek Bitiş Tarihi",
        compute='_compute_free_support_end_date',
        store=True,
        readonly=False,  # Manuel değişikliğe izin ver
        tracking=True,
        help="Ücretsiz teknik desteğin sona ereceği tarih."
    )

    @api.depends('start_date', 'free_support_term_id')
    def _compute_free_support_end_date(self):
        """
        Ücretsiz destek süresi seçildiğinde ve başlangıç tarihi girildiğinde
        bitiş tarihini otomatik olarak hesaplar.
        """
        for license in self:
            if license.free_support_term_id and license.start_date:
                # license.term modelindeki mevcut metodu kullanarak tarihi hesapla
                license.free_support_end_date = license.free_support_term_id._get_end_date(license.start_date)
            else:
                license.free_support_end_date = False

    @api.depends('start_date', 'end_date', 'state')
    def _compute_expiration_progress(self):
        today = fields.Date.today()
        for license in self:
            if license.state in ('expired', 'cancelled') or not license.end_date or not license.start_date:
                license.expiration_progress = 100.0
                continue

            if license.start_date > today:
                license.expiration_progress = 0.0
                continue

            total_duration = (license.end_date - license.start_date).days
            days_passed = (today - license.start_date).days

            if total_duration <= 0:
                license.expiration_progress = 100.0
            else:
                progress = (days_passed / total_duration) * 100
                license.expiration_progress = min(max(progress, 0), 100)

    # Tekil arşivleme metodu
    def action_archive(self):
        """Archive the selected licenses"""
        for license in self:
            if license.state != 'cancelled':
                raise UserError(_("Only cancelled licenses can be archived."))
            license.is_archived = True
            license._create_history('archived', 'License archived')
        return True

    # Tekil arşivden çıkarma metodu
    def action_unarchive(self):
        """Unarchive the selected licenses"""
        for license in self:
            license.is_archived = False
            license._create_history('unarchived', 'License unarchived')
        return True

    # Toplu arşivleme metodu
    def action_bulk_archive(self):
        """Bulk archive selected licenses"""
        active_ids = self.env.context.get('active_ids', [])
        selected_licenses = self.env['license.subscription'].browse(active_ids)

        if not selected_licenses:
            raise UserError(_("Please select at least one license to archive."))

        # Sadece iptal edilmiş lisanslar arşivlenebilir
        archivable_licenses = selected_licenses.filtered(
            lambda l: l.state == 'cancelled' and not l.is_archived
        )

        if not archivable_licenses:
            raise UserError(_("Only cancelled licenses can be archived."))

        # Toplu arşivleme işlemi
        for license in archivable_licenses:
            license.is_archived = True
            license._create_history('archived', 'Bulk archiving')

        # Başarı mesajı
        archived_count = len(archivable_licenses)
        skipped_count = len(selected_licenses) - archived_count
        message = _("Successfully archived %d license(s).") % archived_count
        if skipped_count > 0:
            message += _(" %d license(s) were skipped (not cancelled or already archived).") % skipped_count

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Archive'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    # Tekil aktifleştirme metodu
    def action_set_active(self):
        """Set cancelled licenses back to active status"""
        for license in self:
            if license.state != 'cancelled':
                raise UserError(_("Only cancelled licenses can be set to active."))
            license.state = 'active'
            license._create_history('set_active', 'License set to active from cancelled')
        return True

    # Toplu aktifleştirme metodu
    def action_bulk_set_active(self):
        """Bulk set cancelled licenses back to active status"""
        active_ids = self.env.context.get('active_ids', [])
        selected_licenses = self.env['license.subscription'].browse(active_ids)

        if not selected_licenses:
            raise UserError(_("Please select at least one license to set to active."))

        # Sadece iptal edilmiş lisanslar aktif hale getirilebilir
        activable_licenses = selected_licenses.filtered(
            lambda l: l.state == 'cancelled'
        )

        if not activable_licenses:
            raise UserError(_("Selected licenses are not cancelled."))

        # Toplu aktifleştirme işlemi
        for license in activable_licenses:
            license.state = 'active'
            license._create_history('set_active', 'Bulk set to active')

        # Başarı mesajı
        activated_count = len(activable_licenses)
        skipped_count = len(selected_licenses) - activated_count
        message = _("Successfully set %d license(s) to active.") % activated_count
        if skipped_count > 0:
            message += _(" %d license(s) were skipped (not cancelled).") % skipped_count

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Set Active'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    # Toplu arşivden çıkarma metodu
    def action_bulk_unarchive(self):
        """Bulk unarchive selected licenses"""
        active_ids = self.env.context.get('active_ids', [])
        selected_licenses = self.env['license.subscription'].browse(active_ids)

        if not selected_licenses:
            raise UserError(_("Please select at least one license to unarchive."))

        # Sadece arşivlenmiş lisanslar arşivden çıkarılabilir
        unarchivable_licenses = selected_licenses.filtered(
            lambda l: l.is_archived
        )

        if not unarchivable_licenses:
            raise UserError(_("Selected licenses are not archived."))

        # Toplu arşivden çıkarma işlemi
        for license in unarchivable_licenses:
            license.is_archived = False
            license._create_history('unarchived', 'Bulk unarchiving')

        # Başarı mesajı
        unarchived_count = len(unarchivable_licenses)
        skipped_count = len(selected_licenses) - unarchived_count
        message = _("Successfully unarchived %d license(s).") % unarchived_count
        if skipped_count > 0:
            message += _(" %d license(s) were skipped (not archived).") % skipped_count

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Unarchive'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_bulk_cancel(self):
        """
        Tree view'da seçili lisansları toplu olarak iptal eder
        """
        # Seçili kayıtları context'ten al
        active_ids = self.env.context.get('active_ids', [])
        selected_licenses = self.env['license.subscription'].browse(active_ids)

        if not selected_licenses:
            raise UserError(_("Please select at least one license to cancel."))

        # Sadece iptal edilebilecek durumdaki lisansları filtrele
        cancelable_licenses = selected_licenses.filtered(
            lambda l: l.state != 'cancelled'
        )

        # Toplu iptal işlemi
        for license in cancelable_licenses:
            license.state = 'cancelled'
            license._create_history('cancelled', 'Bulk cancellation')

        # Başarı mesajı
        canceled_count = len(cancelable_licenses)
        skipped_count = len(selected_licenses) - canceled_count

        message = _("Successfully cancelled %d license(s).") % canceled_count
        if skipped_count > 0:
            message += _(" %d license(s) were skipped (already cancelled).") % skipped_count

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Cancellation'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    @api.onchange('product_type_selector')
    def _onchange_product_type_selector(self):
        """Product type değiştiğinde ürünü ve detail_title'ı sıfırlar, domain filtreler."""
        # Önce ürünü sıfırla
        self.product_id = False
        # detail_title'ı da sıfırla çünkü yeni tip için farklı değer gerekecek
        self.detail_title = False

        # Ürün domain'ini güncelle
        if self.product_type_selector:
            domain = [('product_tmpl_id.type', '=', self.product_type_selector)]
        else:
            domain = [('id', '=', False)]

        return {'domain': {'product_id': domain}}

    @api.onchange('dealer_id')
    def _onchange_dealer_id(self):
        """Bayi değiştiğinde müşteri listesini filtreler."""
        self.customer_id = False
        self.contact_person_id = False

        if self.dealer_id:
            domain = [
                ('is_dealer', '=', False),
                '|',
                ('dealer_id', '=', self.dealer_id.id),
                ('dealer_id', '=', False)
            ]
        else:
            domain = [('is_dealer', '=', False)]

        return {'domain': {'customer_id': domain}}

    @api.onchange('license_term_id', 'start_date')
    def _onchange_license_term_or_start_date(self):
        """Lisans süresi veya başlangıç tarihi değiştiğinde bitiş tarihini hesaplar."""
        if self.start_date and self.license_term_id:
            self.end_date = self.license_term_id._get_end_date(self.start_date)

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        """Müşteri değiştiğinde yetkili kişi atama ve domain güncelleme."""
        if self.customer_id:
            if self.customer_id.is_company:
                self.contact_person_id = self.customer_id.main_contact_id or False
                return {'domain': {'contact_person_id': [('parent_id', '=', self.customer_id.id)]}}
            else:
                self.contact_person_id = self.customer_id
                return {'domain': {'contact_person_id': [('id', '=', self.customer_id.id)]}}
        else:
            self.contact_person_id = False
            return {'domain': {'contact_person_id': []}}

    @api.model
    def create(self, vals):
        vals = dict(vals)
        # Normalize empty license keys to False so the DB uniqueness constraint
        # only applies when a key is actually provided.
        if 'license_key' in vals:
            license_key = vals.get('license_key')
            vals['license_key'] = license_key.strip() if isinstance(license_key, str) else license_key
            if not vals['license_key']:
                vals['license_key'] = False

        if vals.get('license_no', _('New')) == _('New'):
            vals['license_no'] = self.env['ir.sequence'].next_by_code('license.subscription') or _('New')

        license = super().create(vals)

        if license:
            license._set_customer_default_dealer_if_needed()

        # Create history entry
        license._create_history('created')
        return license

    @api.constrains('product_id', 'product_type_selector')
    def _sync_detail_title_with_product(self):
        """
        Product veya type değiştiğinde detail_title'ı otomatik senkronize eder.
        """
        for license in self:
            if not license.product_id:
                continue

            product_type = license.product_id.product_tmpl_id.type if license.product_id.product_tmpl_id else None

            # Software tipinde detail_title her zaman product name olmalı
            if product_type == 'software':
                if license.detail_title != license.product_id.name:
                    # ORM bypass ile güncelle (sonsuz döngü önlemek için)
                    license.with_context(skip_sync=True).write({
                        'detail_title': license.product_id.name
                    })

    # Write metodunu da güncelle (constrains ile çakışmayı önlemek için):
    def write(self, vals):
        # Constrains ile çakışmayı önle
        if self.env.context.get('skip_sync'):
            return super().write(vals)

        vals = dict(vals)
        if 'license_key' in vals:
            license_key = vals.get('license_key')
            vals['license_key'] = license_key.strip() if isinstance(license_key, str) else license_key
            if not vals['license_key']:
                vals['license_key'] = False

        # Normal write işlemi
        res = super().write(vals)

        if res:
            self._set_customer_default_dealer_if_needed()

        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Ürün değiştiğinde type günceller, detail_title doldurur, term domain ayarlar."""

        if self.product_id:
            product_type = self.product_id.product_tmpl_id.type if self.product_id.product_tmpl_id else None

            # 1. Product type selector'ı güncelle
            if product_type:
                self.product_type_selector = product_type

            # 2. Type'a göre detail_title'ı ayarla
            if product_type == 'software':
                # Software: Otomatik olarak product adını yaz
                self.detail_title = self.product_id.name
            elif product_type == 'domain_tracking':
                # Domain tracking: Boş bırak, kullanıcı dolduracak
                if not self.detail_title:
                    self.detail_title = ""
            elif product_type == 'server_service':
                # Server service: Boş bırak
                if not self.detail_title:
                    self.detail_title = ""
            elif product_type == 'support_package':
                # Support package: Varsayılan değer ver
                if not self.detail_title:
                    self.detail_title = f"Support for {self.product_id.name}"
            else:
                # Bilinmeyen tip: Product adını yaz
                self.detail_title = self.product_id.name
        else:
            # Product boşsa detail_title'ı da boşalt
            self.detail_title = False

        # 3. License term domain güncelleme (mevcut kodunuz)
        self.license_term_id = False
        term_domain = [('id', '=', False)]
        if self.product_id and self.product_id.product_tmpl_id.allowed_term_ids:
            allowed_terms_ids = self.product_id.product_tmpl_id.allowed_term_ids.ids
            term_domain = [('id', 'in', allowed_terms_ids)]

        return {'domain': {'license_term_id': term_domain}}

    # PRICELIST HESAPLAMA METODLARı - YENİ
    def _get_pricelist_price(self, product, pricelist, partner=None, quantity=1.0, date=None):
        """Odoo 18 uyumlu pricelist fiyat hesaplama"""
        if not product or not pricelist:
            return 0.0

        date = date or fields.Date.today()
        partner = partner or self.customer_id or self.dealer_id

        # Odoo 18 API
        try:
            if hasattr(pricelist, '_get_product_price'):
                result = pricelist._get_product_price(
                    product=product,
                    quantity=quantity,
                    partner=partner,
                    date=date,
                    uom_id=product.uom_id.id if product.uom_id else False
                )
                return result[0] if isinstance(result, tuple) else result
        except:
            pass

        # Fallback: get_product_price_rule
        try:
            if hasattr(pricelist, 'get_product_price_rule'):
                price, rule_id = pricelist.get_product_price_rule(
                    product=product,
                    quantity=quantity,
                    partner=partner,
                    date=date,
                    uom_id=product.uom_id.id if product.uom_id else False
                )
                return price
        except:
            pass

        # Son fallback: liste fiyatı
        return product.list_price or 0.0

    _sql_constraints = [
        ('license_key_uniq', 'unique(license_key)', 'License Key must be unique!'),
    ]

    @api.depends('product_id', 'pricelist_id', 'use_manual_price', 'manual_amount', 'start_date', 'customer_id',
                 'dealer_id')
    def _compute_amount(self):
        """Pricelist'e göre tutarı hesaplar"""
        for license in self:
            if license.use_manual_price:
                license.amount = license.manual_amount or 0.0
            elif license.product_id and license.pricelist_id:
                price = license._get_pricelist_price(
                    product=license.product_id,
                    pricelist=license.pricelist_id,
                    partner=license.customer_id or license.dealer_id,
                    quantity=1.0,
                    date=license.start_date
                )
                license.amount = price
            else:
                license.amount = license.product_id.list_price if license.product_id else 0.0

    @api.depends('license_no', 'customer_id', 'dealer_id', 'product_id')
    def _compute_name(self):
        for license in self:
            parts = []
            if license.license_no:
                parts.append(license.license_no)
            if license.customer_id:
                parts.append(license.customer_id.name)
            if license.dealer_id:
                parts.append(f"({license.dealer_id.name})")  # Bayiyi parantez içinde gösterelim
            if license.product_id:
                parts.append(license.product_id.name)
            license.name = ' - '.join(parts) if parts else ''

    #
    # @api.depends('start_date', 'license_term_id')
    # def _compute_end_date(self):
    #     """
    #     Başlangıç tarihi veya lisans süresi değiştiğinde bitiş tarihini otomatik olarak hesaplar.
    #     """
    #     for license in self:
    #         # Sadece gerekli alanlar doluysa hesaplama yap
    #         if license.start_date and license.license_term_id:
    #             # license.term modelindeki yardımcı metodu çağır
    #             license.end_date = license.license_term_id._get_end_date(license.start_date)
    #         else:
    #             # Eğer gerekli alanlar dolu değilse, end_date'i boş bırak
    #             license.end_date = False

    @api.depends('end_date')
    def _compute_days_to_expire(self):
        today = date.today()
        for license in self:
            if license.end_date:
                delta = license.end_date - today
                license.days_to_expire = delta.days
            else:
                license.days_to_expire = 0

    @api.depends('days_to_expire', 'start_date', 'license_term_id', 'end_date')
    def _compute_state(self):
        today = date.today()
        for license in self:
            # --- YENİ EKLENEN KONTROL ---
            # 1. Eğer kayıt yeni bir form ise (henüz ID'si yoksa) veya
            #    kaydedilmiş ama bitiş tarihi olmayan bir kayıt ise, her zaman taslaktır.
            # Bu, en başa konarak diğer tüm mantığı atlamasını sağlar.
            if not license.id or not license.end_date:
                license.state = 'draft'
                continue
            # ---------------------------

            # 2. İptal edilmişse dokunma (Bu zaten vardı, doğru)
            if license.state == 'cancelled':
                continue

            # 3. Henüz başlamamışsa taslaktır (Bu da vardı, doğru)
            if license.start_date and license.start_date > today:
                license.state = 'draft'
                continue

            # 4. Bitiş tarihi geçmişse (Doğru, ama küçük bir iyileştirme ile)
            # days_to_expire negatif olduğunda bu koşul zaten sağlanır.
            if license.days_to_expire < 0:
                license.state = 'expired'
                continue

            # 5. Uyarı mantığı (Mevcut kodunuzdaki gibi)
            # Eğer bir lisans süresi tanımlanmışsa, uyarı günlerini oradan oku
            if license.license_term_id:
                urgent_days = license.license_term_id.urgent_warning_days
                warning_days = license.license_term_id.warning_days

                if license.days_to_expire <= urgent_days:
                    license.state = 'urgent'
                elif license.days_to_expire <= warning_days:
                    license.state = 'expiring'
                else:
                    license.state = 'active'
            else:
                # Eğer lisans süresi tanımlanmamışsa (manuel bitiş tarihi),
                # varsayılan 30 günlük kuralı uygula.
                if license.days_to_expire <= 30:
                    license.state = 'expiring'
                else:
                    license.state = 'active'

    def _create_history(self, action, notes=''):
        self.ensure_one()
        self.env['license.history'].create({
            'license_id': self.id,
            'action': action,
            'date': fields.Datetime.now(),
            'user_id': self.env.user.id,
            'notes': notes,
        })

    @api.model
    def get_license_dashboard_data(self):
        """
        Returns data for the license dashboard.
        This method is called via RPC from JavaScript.
        """
        today = fields.Date.today()
        thirty_days_later = today + timedelta(days=30)

        # Toplam Aktif Lisans Sayısı
        total_active = self.search_count([('state', '=', 'active')])

        # 30 Gün İçinde Bitecek Lisans Sayısı
        expiring_30_days = self.search_count([
            ('end_date', '>=', today),
            ('end_date', '<=', thirty_days_later)
        ])

        # Toplam Süresi Dolmuş Lisans Sayısı
        total_expired = self.search_count([('state', '=', 'expired')])

        # Aktif Lisansların Toplam Değeri
        active_licenses = self.search_read([('state', '=', 'active')], ['amount'])
        total_revenue_active = sum(lic['amount'] for lic in active_licenses if lic['amount'])

        # Durum Dağılımı (Grafik için)
        states_data = self.read_group(
            domain=[],
            fields=['state'],
            groupby=['state'],
            lazy=False
        )
        state_counts = {
            'labels': [s['state'] for s in states_data],
            'data': [s['state_count'] for s in states_data],
        }

        # En Çok Lisansa Sahip 5 Bayi (Grafik için)
        # Sadece d['dealer_id'] bir değer içeriyorsa (False değilse) ID'yi al
        dealer_ids = [d['dealer_id'][0] for d in top_dealers_data if d['dealer_id']]
        dealer_names = self.env['res.partner'].browse(dealer_ids).mapped('name')
        top_dealers = {
            'labels': [d['dealer_id'][1] for d in top_dealers_data if d['dealer_id']],
            'data': [d['dealer_id_count'] for d in top_dealers_data if d['dealer_id']],
        }

        return {
            'total_active': total_active,
            'expiring_30_days': expiring_30_days,
            'total_expired': total_expired,
            'total_revenue_active': round(total_revenue_active, 2),
            'state_counts': state_counts,
            'top_dealers': top_dealers,
        }

    @api.model
    def _cron_update_license_states(self):
        """
        Daily cron job to re-calculate and update the 'days_to_expire' and 'state'
        of all non-terminal licenses. This is necessary because computed fields
        do not automatically update with the passage of time.
        """
        _logger.info("Starting daily cron job: Update License States...")

        # Performansı artırmak için toplu işlem yapalım (örneğin 500'lük gruplar halinde)
        BATCH_SIZE = 500
        offset = 0

        # Sadece durumu değişebilecek lisansları hedef alıyoruz:
        # Süresi dolmuş, iptal edilmiş veya taslak olanlarla işimiz yok.
        domain = [('state', 'not in', ['expired', 'cancelled', 'draft'])]

        # Lisansları toplu olarak bul
        all_relevant_licenses = self.search(domain)

        _logger.info(f"Found {len(all_relevant_licenses)} licenses to re-evaluate.")

        # Bulunan tüm lisanslar üzerinde hesaplama metodlarını yeniden tetikle
        # Odoo, bu metodlar çağrıldığında store=True olan alanları
        # otomatik olarak güncelleyecektir.
        if all_relevant_licenses:
            # Önce bağımlı olduğu alanı hesapla
            all_relevant_licenses._compute_days_to_expire()
            # Sonra bu alanı kullanan durumu hesapla
            all_relevant_licenses._compute_state()

        _logger.info("Cron job: Update License States finished successfully.")

    @api.model
    def _cron_check_expiring_licenses(self):
        """
        Cron job to check expiring licenses and send notifications.
        Optimized for large datasets using batch processing.
        """
        _logger.info("Starting cron job: Check Expiring Licenses...")

        BATCH_SIZE = 500  # Her döngüde kaç kayıt işleneceğini belirler
        offset = 0

        template = self.env.ref(
            'license_management.mail_template_license_expiring',
            raise_if_not_found=False
        )

        while True:
            _logger.info(f"Processing licenses batch: offset={offset}, limit={BATCH_SIZE}")

            # Süresi dolmakta olan ve otomatik yenilenmeyecek lisansları bul
            expiring_licenses = self.search([
                ('state', 'in', ['expiring', 'urgent']),
                ('auto_renew', '=', False)
            ], limit=BATCH_SIZE, offset=offset)

            # İşlenecek kayıt kalmadıysa döngüden çık
            if not expiring_licenses:
                break

            if template:
                for license in expiring_licenses:
                    try:
                        template.send_mail(license.id, force_send=True)
                        _logger.info(f"Expiring notification sent for license {license.license_no}")
                    except Exception as e:
                        _logger.error(f"Failed to send expiring email for license {license.license_no}: {e}")

            # Otomatik yenilenecek lisansları işle (ayrı bir sorgu daha performanslı olabilir)
            auto_renew_licenses = self.search([
                ('state', 'in', ['expiring', 'urgent']),
                ('auto_renew', '=', True),
                ('id', 'in', expiring_licenses.ids)  # Sadece bu batch içindekilere bak
            ])
            for license in auto_renew_licenses:
                try:
                    license.action_auto_renew()
                    _logger.info(f"Auto-renewed license {license.license_no}")
                except Exception as e:
                    _logger.error(f"Failed to auto-renew license {license.license_no}: {e}")

            # Bir sonraki batch için offset'i artır
            offset += BATCH_SIZE

        _logger.info("Cron job: Check Expiring Licenses finished.")

    def _set_customer_default_dealer_if_needed(self):
        """
        Lisans kaydedilirken, eğer müşterinin varsayılan bir bayisi yoksa
        ve lisansta bir bayi seçilmişse, bu bayiyi müşterinin varsayılan
        bayisi olarak atar.
        """
        for license in self:
            # Koşulları kontrol et:
            # 1. Müşteri var mı?
            # 2. Bayi var mı?
            # 3. Müşterinin zaten bir varsayılan bayisi VAR MI? (Eğer varsa, üzerine yazma)
            if license.customer_id and license.dealer_id and not license.customer_id.dealer_id:
                try:
                    license.customer_id.write({
                        'dealer_id': license.dealer_id.id
                    })
                    _logger.info(
                        f"Müşteri '{license.customer_id.name}' için varsayılan bayi "
                        f"'{license.dealer_id.name}' olarak ayarlandı."
                    )
                    # İsteğe bağlı: Müşterinin chatter'ına bir not bırakabilirsiniz.
                    license.customer_id.message_post(
                        body=_(
                            "Default dealer set to %s via License %s.",
                            license.dealer_id.name,
                            license.license_no,
                        )
                    )
                except Exception as e:
                    _logger.error(
                        f"Müşteri için varsayılan bayi ayarlanırken hata oluştu: {e}"
                    )

    def copy(self, default=None):
        """
        Bir lisans kopyalandığında çalışacak özel mantık.
        """
        if default is None:
            default = {}

        # Orijinal lisans numarasını al ve sonuna '(Kopya)' ekle.
        # Bu, yeni kaydın 'license_no' alanı için bir varsayılan değer olacak.
        copied_name = _("%s (Copy)") % self.license_no
        default['license_no'] = copied_name
        default['license_key'] = False
        # Sıfırlanacak alanları burada belirt.
        # Eğer bu alanlar default içinde zaten varsa (duplicate_license'dan geliyorsa),
        # onların üzerine yazılmaz.
        default.setdefault('history_ids', [(5, 0, 0)])  # Geçmişi temizle
        default.setdefault('product_id', False)
        default.setdefault('license_term_id', False)
        default.setdefault('start_date', fields.Date.today())
        default.setdefault('end_date', False)
        default.setdefault('state', 'draft')
        default.setdefault('notes', '')
        default.setdefault('amount', 0.0)

        return super().copy(default)

    def duplicate_license(self):
        """
        Mevcut lisansı temel alarak yeni bir lisans oluşturur.
        Bayi ve müşteri bilgileri korunur, diğer alanlar sıfırlanır.
        """
        self.ensure_one()

        # copy() metoduna gönderilecek varsayılan değerleri hazırla.
        # Bu değerler, copy() içindeki setdefault'lardan öncelikli olacaktır.
        default_vals = {
            'dealer_id': self.dealer_id.id,
            'customer_id': self.customer_id.id,
            'contact_person_id': self.contact_person_id.id if self.contact_person_id else False,
            # Diğer tüm alanları sıfırlama işini copy() metodu yapacak.
        }

        # Özelleştirdiğimiz copy() metodunu çağırıyoruz.
        new_license = self.copy(default=default_vals)

        new_license.message_post(body=_("This license was duplicated from license %s.") % self.license_no)

        # Kullanıcıyı yeni oluşturulan lisansın form görünümüne yönlendir.
        return {
            'type': 'ir.actions.act_window',
            'name': 'Duplicate License',
            'res_model': 'license.subscription',
            'res_id': new_license.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_activate(self):
        for license in self:
            if license.state == 'draft':
                license.write({
                    'state': 'active',
                    'start_date': fields.Date.today()
                })
                license._create_history('activated')

    def action_cancel(self):
        for license in self:
            if license.state == 'cancelled':
                continue
            previous_state = license.state
            license.state = 'cancelled'
            note = previous_state and _("Cancelled from state: %s") % previous_state or ''
            license._create_history('cancelled', note)

    def action_renew(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Renew License',
            'res_model': 'license.renewal.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_license_id': self.id,
                'default_customer_id': self.customer_id.id, # Müşteriyi gönder
                'default_dealer_id': self.dealer_id.id,     # Bayiyi gönder
                'default_product_id': self.product_id.id,
            }
        }

    def action_auto_renew(self):
        """Lisansı, tanımlı olan lisans süresini kullanarak otomatik olarak yeniler."""
        self.ensure_one()
        # Otomatik yenileme için lisans süresi tanımlı olmalı
        if self.license_term_id:
            new_start_date = self.end_date + timedelta(days=1) if self.end_date else fields.Date.today()
            # Yeni bitiş tarihini hesaplamak için license_term modelindeki metodu kullan
            new_end_date = self.license_term_id._get_end_date(new_start_date)

            # Aynı lisans kaydını güncelle
            self.write({
                'start_date': new_start_date,
                'end_date': new_end_date,
                'license_term_id': self.license_term_id.id,
            })

            start_display = fields.Date.to_string(new_start_date) if new_start_date else ''
            end_display = fields.Date.to_string(new_end_date) if new_end_date else ''
            note = _("Lisans otomatik yenilendi. Yeni dönem: %s - %s") % (start_display, end_display)
            self._create_history('auto_renewed', note)
            return self

        # Eğer lisans süresi yoksa loga uyarı yaz
        _logger.warning("Lisans %s için bir Lisans Süresi tanımlanmadığından otomatik yenilenemedi.", self.license_no)
        return False

    def action_create_subscription(self):
        self.ensure_one()

        # --- DEĞİŞİKLİK BAŞLANGICI: Akıllı Şablon Seçimi ---

        # 1. Lisanstaki süre tanımından eşleştirilmiş abonelik şablonunu al.
        subscription_template = self.license_term_id.subscription_template_id

        # 2. Eğer eşleştirilmiş bir şablon yoksa, kullanıcıya hata ver.
        if not subscription_template:
            raise ValidationError(
                _("The selected license term '%s' does not have an associated subscription template. Please configure it first.")
                % self.license_term_id.name
            )

        # --- DEĞİŞİKLİK SONU ---

        # Abonelik oluşturma işlemi
        subscription_vals = {
            'partner_id': self.customer_id.id,
            'template_id': subscription_template.id,  # Eşleştirilmiş şablonu kullan
            'date_start': self.start_date,
            'pricelist_id': self.pricelist_id.id or self.customer_id.property_product_pricelist.id,
            'sale_subscription_line_ids': [
                (0, 0, {
                    'product_id': self.product_id.id,
                    'name': self.product_id.display_name,
                    'product_uom_qty': 1,
                    'price_unit': self.amount,  # Lisanstaki tutarı kullan
                })
            ]
        }

        subscription = self.env['sale.subscription'].create(subscription_vals)

        # Lisansı oluşturulan aboneliğe bağla
        self.subscription_id = subscription
        self._create_history(
            'subscription_created',
            notes=f'Subscription {subscription.name} created'
        )

        # Kullanıcıyı yeni oluşturulan aboneliğin formuna yönlendir
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.subscription',
            'res_id': subscription.id,
            'view_mode': 'form',
            'target': 'current',
        }
