# -*- coding: utf-8 -*-
{
    "name": "Spreadsheet Dashboard for Helpdesk & Licenses",
    "version": "18.0.1.0.0",
    "category": "Services/Helpdesk",
    "summary": "Spreadsheet dashboard with custom helpdesk and license formulas",
    "description": "Provides a spreadsheet dashboard for analyzing helpdesk tickets and licenses with custom formulas",
    "author": "Lugatsoft",
    "website": "https://www.lugatsoft.com",
    "depends": [
        "spreadsheet_dashboard",
        "helpdesk_mgmt",
        "license_management",
        "helpdesk_license",
    ],
    "data": [
        "data/dashboards.xml",
    ],
    "assets": {
        "spreadsheet.o_spreadsheet": [
            (
                "after",
                "spreadsheet/static/src/o_spreadsheet/o_spreadsheet.js",
                "spreadsheet_dashboard_helpdesk/static/src/**/*.js",
            ),
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
