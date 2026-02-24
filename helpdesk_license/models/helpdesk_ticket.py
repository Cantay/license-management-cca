# -*- coding: utf-8 -*-
from odoo import fields, models, api
import ast

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    color = fields.Integer(string='Color', default=0, help="Color for kanban view organization")

    license_id = fields.Many2one(
        'license.subscription',
        string='License',
        help="The specific license this ticket is related to.",
        domain="[('customer_id', 'child_of', partner_id)]",
    )

    dealer_id = fields.Many2one(
        'res.partner',
        string='Dealer',
        related='partner_id.dealer_id',
        store=True,
        readonly=True,
        domain=[('is_dealer', '=', True)]
    )

    has_free_support_active = fields.Boolean(
        string="Has Active Free Support",
        compute='_compute_has_free_support_active',
        store=True,
        help="Indicates if the ticket is linked to a license with active free support."
    )

    # BAĞIMLILIKLAR GÜNCELLENDİ
    @api.depends('license_id', 'license_id.free_support_term_id', 'license_id.free_support_end_date')
    def _compute_has_free_support_active(self):
        """
        Check if the related license has an active free support term.
        """
        today = fields.Date.context_today(self)
        for ticket in self:
            ticket.has_free_support_active = False
            license = ticket.license_id
            # MANTIK GÜNCELLENDİ: Artık free_support_term_id'nin varlığını kontrol ediyoruz
            if license and license.free_support_term_id and license.free_support_end_date:
                if license.free_support_end_date >= today:
                    ticket.has_free_support_active = True

    has_maintenance_agreement = fields.Boolean(
        string="Has Maintenance Agreement",
        compute='_compute_has_maintenance_agreement',
        store=True,
        help="Indicates if the ticket is linked to an active maintenance agreement."
    )

    # @api.depends DEĞİŞİYOR: partner_id'yi de bağımlılıklara ekliyoruz.
    @api.depends('license_id', 'license_id.state', 'license_id.product_id.product_tmpl_id.has_maintenance_agreement',
                 'partner_id')
    def _compute_has_maintenance_agreement(self):
        """
        Check for an active maintenance agreement based on Helpdesk settings.
        1. If setting is ON: Checks all licenses of the customer.
        2. If setting is OFF: Checks only the license selected on the ticket.
        """
        # Ayarı sistem parametrelerinden oku
        param = self.env['ir.config_parameter'].sudo().get_param('helpdesk_license.check_maintenance_on_partner',
                                                                 'False')
        check_on_partner = ast.literal_eval(param)  # 'False' string'ini False boolean'a çevirir

        for ticket in self:
            # Varsayılan olarak false
            ticket.has_maintenance_agreement = False

            if check_on_partner:
                # YENİ MANTIK: Müşterinin tüm lisanslarını kontrol et
                if not ticket.partner_id:
                    continue  # Müşteri yoksa devam et

                # Müşteriye ait aktif ve bakım anlaşmalı lisans var mı diye ara
                domain = [
                    ('customer_id', 'child_of', ticket.partner_id.id),
                    ('state', 'in', ['active', 'expiring', 'urgent']),
                    ('product_id.product_tmpl_id.has_maintenance_agreement', '=', True),
                ]
                # search_count daha performanslıdır, sadece 1 tane bulmamız yeterli
                if self.env['license.subscription'].search_count(domain) > 0:
                    ticket.has_maintenance_agreement = True

            else:
                # ESKİ MANTIK: Sadece seçili lisansı kontrol et
                license = ticket.license_id
                if license and license.state in ['active', 'expiring', 'urgent']:
                    if license.product_id.product_tmpl_id.has_maintenance_agreement:
                        ticket.has_maintenance_agreement = True

    @api.onchange('partner_id')
    def _onchange_partner_id_for_license(self):
        """
        Partner değiştiğinde:
        1. Lisans alanı için domain'i günceller
        2. Eğer partner'ın tek lisansı varsa otomatik olarak seçer
        """
        # Önceki lisans seçimini temizle
        self.license_id = False

        if self.partner_id:
            # Partner'a ait lisansları bul
            partner_licenses = self.env['license.subscription'].search([
                ('customer_id', '=', self.partner_id.id)
            ])

            # Domain'i ayarla
            domain = {'license_id': [('customer_id', '=', self.partner_id.id)]}

            # Eğer tek lisans varsa otomatik seç
            if len(partner_licenses) == 1:
                self.license_id = partner_licenses[0]
                # Lisans seçildiğinde ürünü de otomatik doldur
                if partner_licenses[0].product_id:
                    # product_id alanı varsa (helpdesk_product modülünden)
                    if hasattr(self, 'product_id'):
                        self.product_id = partner_licenses[0].product_id

            return {'domain': domain}
        else:
            # Partner yoksa hiçbir lisans gösterme
            return {'domain': {'license_id': [('id', '=', 0)]}}

    @api.onchange('license_id')
    def _onchange_license_id(self):
        """
        Lisans seçildiğinde otomatik olarak ürünü ayarlar.
        """
        if hasattr(self, 'product_id'):
            if self.license_id and self.license_id.product_id:
                self.product_id = self.license_id.product_id
            else:
                self.product_id = False
