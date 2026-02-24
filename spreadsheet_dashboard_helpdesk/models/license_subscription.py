# -*- coding: utf-8 -*-
from odoo import fields, models, api


class LicenseSubscription(models.Model):
    _inherit = 'license.subscription'

    def _apply_date_range(self, domain, date_from, date_to, field_name='start_date'):
        if date_from:
            try:
                dt_from = fields.Date.from_string(date_from)
                domain.append((field_name, '>=', dt_from))
            except Exception:
                pass
        if date_to:
            try:
                dt_to = fields.Date.from_string(date_to)
                domain.append((field_name, '<=', dt_to))
            except Exception:
                pass

    @api.model
    def spreadsheet_fetch_license_count(self, args_list):
        """
        Fetch license counts for spreadsheet formulas
        Args:
            args_list: [{
                domain: list,
                state: str ('active', 'expired', 'expiring', 'urgent', 'draft', 'cancelled'),
                dealer_id: int,
                program_id: int,
            }]
        Returns:
            [{'count': int}]
        """
        results = []
        for args in args_list:
            domain = list(args.get('domain', []))
            state = args.get('state')

            if state:
                if state == 'all':
                    pass  # No state filter needed
                else:
                    domain.append(('state', '=', state))

            if args.get('dealer_id'):
                domain.append(('dealer_id', '=', args['dealer_id']))
            if args.get('program_id'):
                domain.append(('program_id', '=', args['program_id']))

            self._apply_date_range(
                domain,
                args.get('date_from'),
                args.get('date_to')
            )

            count = self.search_count(domain)
            results.append({'count': count})
        return results

    @api.model
    def spreadsheet_fetch_top_dealers(self, args_list):
        """
        Fetch top dealers ordered by license count.
        Args:
            args_list: [{
                domain: list,
                state: str,
                dealer_id: int,
                program_id: int,
                limit: int,
            }]
        Returns:
            [{'records': [{'dealer_id': int, 'dealer_name': str, 'count': int}]}]
        """
        results = []
        for args in args_list:
            domain = list(args.get('domain', []))
            state = args.get('state')
            dealer_id = args.get('dealer_id')
            program_id = args.get('program_id')
            limit = int(args.get('limit') or 5)
            limit = max(limit, 1)

            if state and state != 'all':
                domain.append(('state', '=', state))
            if dealer_id:
                domain.append(('dealer_id', '=', dealer_id))
            if program_id:
                domain.append(('program_id', '=', program_id))

            self._apply_date_range(
                domain,
                args.get('date_from'),
                args.get('date_to')
            )

            read_group_result = self.read_group(
                domain,
                fields=['dealer_id'],
                groupby=['dealer_id'],
                limit=limit,
                orderby='__count DESC'
            )

            records = []
            for entry in read_group_result:
                dealer = entry.get('dealer_id')
                count = entry.get('__count', entry.get('dealer_id_count', 0))
                records.append({
                    'dealer_id': dealer[0] if isinstance(dealer, (list, tuple)) else False,
                    'dealer_name': dealer[1] if isinstance(dealer, (list, tuple)) else '',
                    'count': count or 0,
                })

            results.append({'records': records})

        return results
