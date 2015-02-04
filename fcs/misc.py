# coding=utf-8
import json
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from flask import Blueprint, Response, current_app
from flask.views import MethodView

from fcs.match import get_all_non_candidates
from fcs.api import UndertakingList
from fcs.models import User

MIMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

misc = Blueprint('misc', __name__)


class UndertakingListExport(MethodView):
    COLUMNS = [
        'company_id', 'name', 'domain', 'status', 'undertaking_type',
        'website',
        'date_updated', 'phone', 'oldcompany_extid', 'address_city',
        'address_country_code', 'address_country_name', 'address_country_type',
        'address_zipcode', 'address_number', 'address_street', 'country_code',
        'vat', 'users', 'users', 'types', 'collection_id', 'date_created',
        'oldcompany_account', 'oldcompany_verified', 'representative_name',
        'representative_contact_first_name',
        'representative_contact_last_name',
        'representative_vatnumber', 'representative_contact_email',
        'representative_address_zipcode', 'representative_address_number',
        'representative_address_street', 'representative_address_city',
        'representative_address_country_code',
        'representative_address_country_type',
        'representative_address_country_name'
    ]

    def get_data(self):
        return [UndertakingList.serialize(c) for c in get_all_non_candidates()]

    def parse_column(self, qs, column):
        def _parse_address(qs, column):
            for sub_column in column.split('_'):
                qs = qs[sub_column]
            return qs

        if column.startswith('address'):
            return _parse_address(qs, column)
        elif column.startswith('representative'):
            repr_info = column.split('_', 1)[1]
            qs = qs['representative']
            if not qs:
                return None
            if repr_info.startswith('address'):
                return _parse_address(qs, repr_info)
            return qs[repr_info]
        return qs[column]

    def get(self, **kwargs):
        queryset = self.get_data()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Companies List'
        ws.append(self.COLUMNS)
        for qs in queryset:
            qs['users'] = ', '.join([user['username'] for user in qs['users']])
            values = [self.parse_column(qs, column) for column in self.COLUMNS]
            ws.append(values)
        response = Response(save_virtual_workbook(wb), mimetype=MIMETYPE)
        response.headers.add('Content-Disposition',
                             'attachment; filename=companies_list.xlsx')
        return response


class UserListExport(MethodView):
    COLUMNS = [
        'username', 'companyname', 'country', 'contact_firstname',
        'contact_lastname', 'contact_email',
    ]

    def get(self, **kwargs):
        users = User.query.all()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Users List'
        ws.append(self.COLUMNS)
        for user in users:
            for company in user.verified_undertakings:
                for cp in company.contact_persons:
                    values = [user.username, company.name,
                              company.address.country.name, cp.first_name,
                              cp.last_name, cp.email]
                    ws.append(values)
        response = Response(save_virtual_workbook(wb), mimetype=MIMETYPE)
        response.headers.add('Content-Disposition',
                             'attachment; filename=users_list.xlsx')
        return response


class SettingsOverview(MethodView):
    def get(self, **kwargs):
        resp = {
            'BASE_URL': current_app.config.get('BASE_URL', 'undefined'),
            'AUTO_VERIFY_COMPANIES': current_app.config.get(
                'AUTO_VERIFY_NEW_COMPANIES', False)
        }
        return Response(json.dumps(resp, indent=2), mimetype='application/json')


misc.add_url_rule('/misc/undertaking/export',
                  view_func=UndertakingListExport.as_view(
                      'company-list-export'))
misc.add_url_rule('/misc/user/export',
                  view_func=UserListExport.as_view(
                      'user-list-export'))
misc.add_url_rule('/misc/settings',
                  view_func=SettingsOverview.as_view(
                      'settings-overview'))
