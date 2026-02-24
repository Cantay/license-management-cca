from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_maintenance_on_partner_licenses = fields.Boolean(
        string="Check All Customer Licenses for Maintenance",
        config_parameter='helpdesk_license.check_maintenance_on_partner',
        help="If checked, a ticket will be marked as having a maintenance agreement "
             "if the customer has *any* active maintenance license, not just the "
             "one specifically selected on the ticket."
    )
