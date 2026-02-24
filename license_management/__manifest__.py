# -*- coding: utf-8 -*-
{
    'name': 'License Management',
    'version': '18.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'Comprehensive License and Dealer Management System',
    'description': """
        This module provides comprehensive license and dealer management features:
        - Dealer (Bayi) management with custom fields
        - License tracking with automatic expiration alerts
        - Integration with subscription_oca for advanced features
        - Reporting and analytics
        - Automatic renewal reminders
    """,
    'author': 'Lugatsoft',
    'website': 'https://www.lugatsoft.com',
    'depends': [
        'base',
        'sale',
        'product',
        'mail',
        'subscription_oca',
        'contacts',
    ],
    'data': [
        'security/license_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/license_data.xml',
        'data/license_term_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/license_term_views.xml',
        'views/license_subscription_views.xml',
        'views/license_program_views.xml',
        # 'views/license_dashboard_views.xml',
        'views/menu_views.xml',
        'wizard/license_renewal_wizard_views.xml',
        'reports/license_report_views.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'license_management/static/src/js/license_dashboard.js',
    #     ],
    # },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
