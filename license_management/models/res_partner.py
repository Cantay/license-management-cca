# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _rec_names_search = [
        "name",
        "phone",
        "mobile",
        "dealer_code",
        "signboard_name",
    ]

    # Dealer specific fields
    is_dealer = fields.Boolean(string='Is Dealer', default=False)
    dealer_code = fields.Char(string='Dealer Code', copy=False, index=True, tracking=True)
    dealer_since = fields.Date(string='Dealer Since')
    tax_number = fields.Char(string='Tax Number')
    signboard_name = fields.Char(string='Signboard Name')
    customer_since = fields.Date(string='Customer Since', copy=False)
    contact_role = fields.Char(string="Contact Role", help="e.g., Technical Contact, Billing Contact")
    main_contact_id = fields.Many2one(
        'res.partner',
        string='Main Contact Person',
        domain="[('parent_id', '=', id), ('is_company', '=', False)]",
        help="Default contact person for this company."
    )

    # Müşterinin bayisini belirten alan
    dealer_id = fields.Many2one(
        'res.partner', string='Default Dealer',
        domain=[('is_dealer', '=', True)],
        help="The default dealer for this customer.")

    # PRICELIST ALANLARI - YENİ
    dealer_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Dealer Pricelist',
        help="Special pricelist for dealer transactions"
    )

    # Bayiler için özel iskonto oranı
    dealer_discount_rate = fields.Float(
        string='Dealer Discount Rate (%)',
        help="Default discount rate for this dealer",
        default=0.0
    )

    dealer_license_ids = fields.One2many(
        'license.subscription', 'dealer_id', string='Dealer Licenses')

    # Bu partner'ın "Müşteri" olduğu tüm lisanslar
    customer_license_ids = fields.One2many(
        'license.subscription', 'customer_id', string='Customer Licenses')

    # Bayinin müşterilerini gösteren alan
    customer_ids = fields.One2many(
        'res.partner',
        'dealer_id',
        string='Customers'
    )
    customer_count = fields.Integer(
        string='Customer Count', compute='_compute_customer_count')

    # License related fields
    license_count = fields.Integer(
        string='License Count', compute='_compute_license_counts', store=True)
    active_license_count = fields.Integer(
        string='Active Licenses', compute='_compute_license_counts', store=True)
    expired_license_count = fields.Integer(
        string='Expired Licenses', compute='_compute_license_counts', store=True)

    # Location fields
    district = fields.Char(string='District')

    @api.depends('customer_ids')
    def _compute_customer_count(self):
        for partner in self:
            if partner.is_dealer:
                partner.customer_count = len(partner.customer_ids)
            else:
                partner.customer_count = 0

    @api.depends('is_dealer', 'dealer_license_ids.state', 'customer_license_ids.state')
    def _compute_license_counts(self):
        for partner in self:
            licenses = self.env['license.subscription']
            if partner.is_dealer:
                licenses = partner.dealer_license_ids
            else:
                licenses = partner.customer_license_ids

            partner.license_count = len(licenses)
            partner.active_license_count = len(licenses.filtered(
                lambda l: l.state == 'active'))
            partner.expired_license_count = len(licenses.filtered(
                lambda l: l.state == 'expired'))

    @api.model
    def create(self, vals):
        if vals.get('is_dealer') and not vals.get('dealer_code'):
            vals['dealer_code'] = self.env['ir.sequence'].next_by_code('dealer.code')
        if vals.get('is_dealer') is False and not vals.get('customer_since'):
            vals['customer_since'] = fields.Date.today()
        return super().create(vals)

    # PRICELIST METODLARı - YENİ
    def get_license_pricelist(self):
        """Lisans için kullanılacak pricelist'i döndürür"""
        self.ensure_one()

        if self.is_dealer and self.dealer_pricelist_id:
            # Bayi ise ve özel bayi pricelist'i varsa onu kullan
            return self.dealer_pricelist_id
        elif self.property_product_pricelist:
            # Müşteri/bayi normal pricelist'i varsa onu kullan
            return self.property_product_pricelist
        else:
            # Varsayılan pricelist'i döndür
            return self.env['product.pricelist'].search([
                ('company_id', 'in', [self.env.company.id, False])
            ], limit=1)

    def get_license_price(self, product_id, quantity=1.0, date=None):
        """Belirli bir ürün için lisans fiyatını hesaplar"""
        self.ensure_one()
        pricelist = self.get_license_pricelist()
        if not pricelist:
            return 0.0

        price = pricelist.get_product_price(
            product_id,
            quantity,
            self,
            date=date or fields.Date.today()
        )

        # Bayi ise ve iskonto oranı varsa uygula
        if self.is_dealer and self.dealer_discount_rate > 0:
            price = price * (1 - self.dealer_discount_rate / 100)

        return price

    @api.onchange('is_dealer')
    def _onchange_is_dealer(self):
        """Bayi durumu değiştiğinde pricelist alanlarını temizle/ayarla"""
        if not self.is_dealer:
            self.dealer_pricelist_id = False
            self.dealer_discount_rate = 0.0
        else:
            # Bayi olduğunda varsayılan bir pricelist atayabilirsiniz
            default_dealer_pricelist = self.env['product.pricelist'].search([
                ('name', 'ilike', 'dealer'),
                ('company_id', 'in', [self.env.company.id, False])
            ], limit=1)
            if default_dealer_pricelist:
                self.dealer_pricelist_id = default_dealer_pricelist

    # Mevcut metodlar aynı kalacak...
    def action_view_licenses(self):
        self.ensure_one()
        domain = []
        context = {}
        if self.is_dealer:
            domain = [('dealer_id', '=', self.id)]
            context = {'default_dealer_id': self.id}
        else:
            domain = [('customer_id', '=', self.id)]
            context = {
                'default_customer_id': self.id,
                'default_dealer_id': self.dealer_id.id if self.dealer_id else False,
            }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Licenses',
            'res_model': 'license.subscription',
            'view_mode': 'list,form,calendar,pivot,graph',
            'domain': domain,
            'context': context,
        }

    def action_view_active_licenses(self):
        """Sadece aktif lisansları gösteren pencere eylemini döndürür."""
        self.ensure_one()
        base_action = self.action_view_licenses()
        base_action['domain'].append(('state', '=', 'active'))
        base_action['name'] = 'Active Licenses'
        return base_action

    def action_view_expired_licenses(self):
        """Sadece süresi dolmuş lisansları gösteren pencere eylemini döndürür."""
        self.ensure_one()
        base_action = self.action_view_licenses()
        base_action['domain'].append(('state', '=', 'expired'))
        base_action['name'] = 'Expired Licenses'
        return base_action

    def action_view_customers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Customers of {self.name}',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.customer_ids.ids)],
            'context': {'default_dealer_id': self.id}
        }
