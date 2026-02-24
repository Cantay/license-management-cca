# -*- coding: utf-8 -*-
from datetime import datetime, time

from odoo import fields, models, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _apply_datetime_range(self, domain, date_from, date_to, field_name="create_date"):
        if date_from:
            try:
                dt_from = fields.Date.from_string(date_from)
                domain.append((
                    field_name, '>=',
                    fields.Datetime.to_string(datetime.combine(dt_from, time.min))
                ))
            except Exception:
                pass
        if date_to:
            try:
                dt_to = fields.Date.from_string(date_to)
                domain.append((
                    field_name, '<=',
                    fields.Datetime.to_string(datetime.combine(dt_to, time.max.replace(microsecond=0)))
                ))
            except Exception:
                pass

    @api.model
    def spreadsheet_fetch_ticket_count(self, args_list):
        """
        Fetch ticket counts for spreadsheet formulas
        Args:
            args_list: [{
                domain: list,
                team_id: int,
                stage_id: int,
                user_id: int,
                priority: str,
                has_maintenance: bool,
                has_free_support: bool,
            }]
        Returns:
            [{'count': int}]
        """
        results = []
        for args in args_list:
            domain = list(args.get('domain', []))

            if args.get('team_id'):
                domain.append(('team_id', '=', args['team_id']))
            if args.get('stage_id'):
                domain.append(('stage_id', '=', args['stage_id']))
            if args.get('user_id'):
                domain.append(('user_id', '=', args['user_id']))
            if args.get('priority'):
                domain.append(('priority', '=', args['priority']))
            if args.get('has_maintenance'):
                domain.append(('has_maintenance_agreement', '=', True))
            if args.get('has_free_support'):
                domain.append(('has_free_support_active', '=', True))
            if args.get('closed') is not None:
                domain.append(('closed', '=', args['closed']))

            self._apply_datetime_range(
                domain,
                args.get('date_from'),
                args.get('date_to'),
                field_name='create_date'
            )

            count = self.search_count(domain)
            results.append({'count': count})

        return results

    @api.model
    def spreadsheet_fetch_top_customers(self, args_list):
        """
        Fetch top customers by ticket volume.
        Args:
            args_list: [{
                domain: list,
                team_id: int,
                user_id: int,
                closed: bool,
                limit: int,
            }]
        Returns:
            [{'records': [{'partner_id': int, 'partner_name': str, 'count': int}]}]
        """
        results = []
        for args in args_list:
            domain = list(args.get('domain', []))
            team_id = args.get('team_id')
            user_id = args.get('user_id')
            closed = args.get('closed')
            limit = int(args.get('limit') or 5)
            limit = max(limit, 1)

            if team_id:
                domain.append(('team_id', '=', team_id))
            if user_id:
                domain.append(('user_id', '=', user_id))
            if closed is not None:
                domain.append(('closed', '=', closed))

            self._apply_datetime_range(
                domain,
                args.get('date_from'),
                args.get('date_to'),
                field_name='create_date'
            )

            read_group_result = self.read_group(
                domain,
                fields=['partner_id'],
                groupby=['partner_id'],
                limit=limit,
                orderby='__count DESC'
            )

            records = []
            for entry in read_group_result:
                partner = entry.get('partner_id')
                count = entry.get('__count', entry.get('partner_id_count', 0))
                records.append({
                    'partner_id': partner[0] if isinstance(partner, (list, tuple)) else False,
                    'partner_name': partner[1] if isinstance(partner, (list, tuple)) else '',
                    'count': count or 0,
                })

            results.append({'records': records})

        return results

    @api.model
    def spreadsheet_fetch_avg_close_time(self, args_list):
        """
        Calculate average time to close tickets in days
        Args:
            args_list: [{'team_id': int}]
        Returns:
            [{'avg_days': float}]
        """
        results = []
        for args in args_list:
            domain = [('closed', '=', True), ('closed_date', '!=', False)]

            if args.get('team_id'):
                domain.append(('team_id', '=', args['team_id']))

            self._apply_datetime_range(
                domain,
                args.get('date_from'),
                args.get('date_to'),
                field_name='closed_date'
            )

            tickets = self.search(domain)
            if tickets:
                total_days = sum([
                    (t.closed_date - t.create_date).days
                    for t in tickets if t.closed_date and t.create_date
                ])
                avg = total_days / len(tickets) if len(tickets) > 0 else 0
            else:
                avg = 0

            results.append({'avg_days': avg})

        return results
    
    @api.model
    def get_dashboard_data(self):
        """Dashboard için istatistikleri döndürür"""
        today = fields.Date.context_today(self)
        week_ago = today - timedelta(days=7)
        
        # Toplam ticket sayıları
        total_tickets = self.search_count([])
        open_tickets = self.search_count([('stage_id.is_close', '=', False)])
        closed_tickets = self.search_count([('stage_id.is_close', '=', True)])
        
        # Bugünkü ve bu haftaki ticketlar
        today_tickets = self.search_count([('create_date', '>=', today.strftime('%Y-%m-%d'))])
        week_tickets = self.search_count([('create_date', '>=', week_ago.strftime('%Y-%m-%d'))])
        
        # Bakım ve destek durumları
        maintenance_tickets = self.search_count([('has_maintenance_agreement', '=', True)])
        free_support_tickets = self.search_count([
            ('has_free_support_active', '=', True),
            ('has_maintenance_agreement', '=', False)
        ])
        
        # Atanmamış ve öncelikli ticketlar
        unassigned_tickets = self.search_count([('user_id', '=', False)])
        high_priority = self.search_count([('priority', '=', '3')])
        urgent_priority = self.search_count([('priority', '=', '4')])
        
        # Stage bazlı dağılım
        stage_data = self.read_group([], ['stage_id'], ['stage_id'])
        
        # Dealer bazlı top 5
        dealer_data = self.read_group(
            [('dealer_id', '!=', False)], 
            ['dealer_id'], 
            ['dealer_id'],
            limit=5,
            orderby='dealer_id_count desc'
        )
        
        return {
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'closed_tickets': closed_tickets,
            'today_tickets': today_tickets,
            'week_tickets': week_tickets,
            'maintenance_tickets': maintenance_tickets,
            'free_support_tickets': free_support_tickets,
            'unassigned_tickets': unassigned_tickets,
            'high_priority': high_priority,
            'urgent_priority': urgent_priority,
            'stage_data': stage_data,
            'dealer_data': dealer_data,
        }