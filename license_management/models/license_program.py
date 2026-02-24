# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class LicenseProgram(models.Model):
    _name = 'license.program'
    _description = 'License Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='Program Name', required=True, tracking=True)
    code = fields.Char(string='Program Code', required=True, copy=False, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    type = fields.Selection(
        [
            ('program', 'Program / Software'),
            ('support', 'Support Service'),
            ('hosting', 'Hosting / Server Service'),
            ('backup_service', 'Yedekleme'),
        ],
        string="Program Type",
        required=True,
        default='program',
        help="Defines the default type of products created under this program."
    )
    # Related products
    product_ids = fields.One2many('product.template', 'license_program_id',
                                  string='Products')
    product_count = fields.Integer(string='Product Count',
                                   compute='_compute_product_count')

    # License statistics
    license_ids = fields.One2many('license.subscription', 'program_id',
                                  string='Licenses')
    license_count = fields.Integer(string='Total Licenses',
                                   compute='_compute_license_stats')
    active_license_count = fields.Integer(string='Active Licenses',
                                          compute='_compute_license_stats')

    @api.depends('product_ids')
    def _compute_product_count(self):
        for program in self:
            program.product_count = len(program.product_ids)

    @api.depends('license_ids', 'license_ids.state')
    def _compute_license_stats(self):
        for program in self:
            licenses = program.license_ids
            program.license_count = len(licenses)
            program.active_license_count = len(
                licenses.filtered(lambda l: l.state == 'active'))

    def write(self, vals):
        res = super(LicenseProgram, self).write(vals)

        if 'type' in vals:
            new_type = vals['type']

            # Güncellenecek tüm ürünleri al
            products_to_update = self.mapped('product_ids')
            if not products_to_update:
                return res  # Güncellenecek ürün yoksa işlemi bitir

            # 1. Adım: Tüm ürünlerin 'type' alanını güncelle
            product_type_val = False
            if new_type == 'software':
                product_type_val = 'software'
            elif new_type == 'support':
                product_type_val = 'support_package'
            elif new_type == 'hosting':
                product_type_val = 'server_service'

            if product_type_val:
                products_to_update.write({'type': product_type_val})

            # 2. Adım: 'is_license_product' alanını koşullu olarak güncelle
            if new_type == 'software':
                # Sadece 'is_license_product' alanı False olan ürünleri bul ve True yap
                products_to_make_license = products_to_update.filtered(lambda p: not p.is_license_product)
                if products_to_make_license:
                    products_to_make_license.write({'is_license_product': True})
            else:
                products_to_update.write({'is_license_product': False})

            # Kullanıcıya bilgi ver
            for program in self:
                program.message_post(
                    body=_("Program type changed to '%s'. Related products have been updated.")
                         % (program.display_name)
                )

        return res

    def action_view_products(self):
        """
        Bu programla ilişkili ürünleri gösterir ve yeni ürün oluştururken
        programın türüne göre doğru varsayılanları ayarlar.
        """
        self.ensure_one()

        action_context = {
            'default_license_program_id': self.id,
        }

        # Programın türüne göre 'product.template.type' alanını doldur
        if self.type == 'software':
            action_context['default_is_license_product'] = True
            action_context['default_type'] = 'software' # Ürünün tipi 'software'
        elif self.type == 'support':
            action_context['default_is_license_product'] = False
            action_context['default_type'] = 'support_package' # Ürünün tipi 'support_package'
        elif self.type == 'hosting':
            action_context['default_is_license_product'] = False
            action_context['default_type'] = 'server_service' # Ürünün tipi 'server_service'

        return {
            'type': 'ir.actions.act_window',
            'name': _('Products'),
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [('license_program_id', '=', self.id)],
            'context': action_context,
        }
    # --- METODUN SONU ---

    def action_view_licenses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licenses',
            'res_model': 'license.subscription',
            'view_mode': 'list,form,calendar,pivot',
            'domain': [('program_id', '=', self.id)],
        }

    def action_view_licenses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licenses',
            'res_model': 'license.subscription',
            'view_mode': 'list,form,calendar,pivot',
            'domain': [('program_id', '=', self.id)],
        }
