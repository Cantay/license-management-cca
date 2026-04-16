# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.tools import html_escape

class LicenseRenewalWizard(models.TransientModel):
    _name = 'license.renewal.wizard'
    _description = 'License Renewal Wizard'

    license_id = fields.Many2one('license.subscription', string='License',
                                required=True)
    customer_id = fields.Many2one(
        'res.partner', string='Customer',
        related='license_id.customer_id', readonly=True)
    dealer_id = fields.Many2one(
        'res.partner', string='Dealer',
        related='license_id.dealer_id', readonly=True)
    product_id = fields.Many2one('product.product', string='Product',
                                required=True)
    license_term_id = fields.Many2one(
        'license.term',
        string='License Term',
        help="Select the term that defines the renewal duration.",
    )
    renewal_start_type = fields.Selection([
        ('next_day', 'Eski Bitişin Ertesi Günü'),
        ('today', 'Bugün İtibariyle'),
        ('custom', 'Özel Bir Tarih Seç')
    ], string='Başlama Seçeneği', default='next_day', required=True)
    start_date = fields.Date(string='New Start Date', required=True)
    duration = fields.Integer(string='Duration (Days)', required=True)
    end_date = fields.Date(string='New End Date', compute='_compute_end_date',
                          store=True)
    amount = fields.Float(string='Renewal Amount', required=True)
    notes = fields.Text(string='Notes')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'license_id' in res:
            license = self.env['license.subscription'].browse(res['license_id'])
            if license:
                start_date = license.end_date + timedelta(days=1) if license.end_date else fields.Date.today()
                term = license.license_term_id
                if term:
                    end_date = term._get_end_date(start_date)
                    duration = (end_date - start_date).days if end_date and start_date else term.duration
                    res.update({
                        'license_term_id': term.id,
                        'duration': duration,
                        'end_date': end_date,
                    })
                else:
                    res['duration'] = 365

                res.update({
                    'product_id': license.product_id.id,
                    'start_date': start_date,
                    'amount': license.amount,
                })
        return res

    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for wizard in self:
            if wizard.start_date and wizard.duration:
                wizard.end_date = wizard.start_date + timedelta(days=wizard.duration)
            else:
                wizard.end_date = False

    @api.onchange('renewal_start_type')
    def _onchange_renewal_start_type(self):
        for wizard in self:
            if wizard.renewal_start_type == 'next_day':
                if wizard.license_id and wizard.license_id.end_date:
                    wizard.start_date = wizard.license_id.end_date + timedelta(days=1)
                else:
                    wizard.start_date = fields.Date.today()
            elif wizard.renewal_start_type == 'today':
                wizard.start_date = fields.Date.today()
            
            # Recalculate end_date logic
            wizard._onchange_license_term_id()

    @api.onchange('license_term_id', 'start_date')
    def _onchange_license_term_id(self):
        for wizard in self:
            if wizard.license_term_id and wizard.start_date:
                end_date = wizard.license_term_id._get_end_date(wizard.start_date)
                wizard.end_date = end_date
                if end_date:
                    wizard.duration = (end_date - wizard.start_date).days or 0

    def action_renew(self):
        self.ensure_one()

        license = self.license_id
        # Mevcut lisansı güncelle
        license.write({
            'product_id': self.product_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'amount': self.amount,
            'notes': self.notes,
            'license_term_id': self.license_term_id.id if self.license_term_id else False,
        })

        # Güncelleme kaydını oluştur
        term_label = self.license_term_id.display_name if self.license_term_id else _('No term selected')
        term_display = html_escape(term_label)
        start_display = fields.Date.to_string(self.start_date) if self.start_date else ''
        end_display = fields.Date.to_string(self.end_date) if self.end_date else ''
        history_notes = _(
            'Lisans güncellendi. Yeni dönem: %(start)s - %(end)s. Lisans süresi: %(term)s. Notlar: %(notes)s',
        ) % {
            'start': start_display,
            'end': end_display,
            'term': term_label,
            'notes': self.notes or '',
        }
        license._create_history('renewed', history_notes)
        message_body = _(
            "Lisans yenilendi.<br/>"
            "Yeni süre: %(term)s<br/>"
            "Başlangıç: %(start)s<br/>"
            "Bitiş: %(end)s<br/>"
            "Tutar: %(amount).2f"
        ) % {
            'term': term_display,
            'start': start_display,
            'end': end_display,
            'amount': self.amount,
        }
        if self.notes:
            message_body += "<br/>%s" % _("Notlar: %s") % html_escape(self.notes)
        license.message_post(body=message_body)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'license.subscription',
            'res_id': license.id,
            'view_mode': 'form',
            'target': 'current',
        }
