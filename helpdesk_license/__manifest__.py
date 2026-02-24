# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk - License Management Integration',
    'version': '18.0.1.0.0',
    'category': 'Services/Helpdesk',
    'summary': 'Integrate Helpdesk with License Management to link tickets to licenses.',
    'author': 'Lugatsoft',
    'website': 'https://www.lugatsoft.com',
    'depends': [
        'helpdesk_mgmt',
        'helpdesk_product',
        'helpdesk_mgmt_timesheet',
        'license_management',
        'product',
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
		'views/license_subscription_views.xml',
        'views/res_partner_views.xml',
		'views/res_config_settings_views.xml',
        'views/helpdesk_license_reporting_views.xml',
],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}
