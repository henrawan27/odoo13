import requests
import base64
import json

from odoo import http
from odoo.http import request
from odoo.addons.base.models.res_partner import _tzs


FIELDS = {
    'hr.expense': {
        'list': ['date', 'name', 'employee_id', 'payment_mode', 'state', 'sale_id', 'total_amount'],
        'form': ['name', 'product_id', 'date', 'unit_amount', 'quantity', 'description', 'sale_id', 'total_amount', 'state']
    },
    'hr.employee': {
        'form': ["image_1920", "name", "job_title", "mobile_phone", "department_id", "work_phone", "job_id", "work_email", "parent_id", "work_location", "address_id", "coach_id", "expense_manager_id", "resource_calendar_id", "tz", "address_home_id", "private_email", "phone", "bank_account_id", "km_home_work", "marital", "emergency_contact", "emergency_phone", "certificate", "study_field", "study_school", "country_id", "identification_id", "passport_id", "gender", "birthday", "place_of_birth", "country_of_birth", "children", "visa_no", "permit_no", "visa_expire", "pin", "barcode"]
    }
}

MENUS = {
    'hr_expense': {
        'shortdesc': 'Expenses',
        'icon': '/hr_expense/static/description/icon.png',
        'menus': [{
            'label': 'My Expenses',
            'children': [
                {'name': 'hr_expense', 'label': 'My Expense', 'view_mode': 'list'}
            ]
        }]
    },
    'hr': {
        'shortdesc': 'My Account',
        'icon': '/hr/static/description/icon.png',
        'menus': [{
            'label': 'My Account',
            'children': [
                {'name': 'hr_employee', 'label': 'My Account', 'view_mode': 'form'}
            ]
        }]
    }
}


class EmployeePortal(http.Controller):

    def _get_fields(self, active_model, mode='list'):

        list_fields = FIELDS.get(active_model, {}).get(mode, [])
        ir_fields = request.env['ir.model.fields'].sudo().search([
            ('model', '=', active_model), ('name', 'in', list_fields)
        ]).sorted(key=lambda x: list_fields.index(x.name))

        defaults = request.env[active_model].sudo().default_get(list_fields)
        defaults = json.loads(json.dumps(defaults, default=str))

        fields = {}
        for field in ir_fields:
            values = {
                'relation': field.relation,
                'ttype': field.ttype,
                'required': field.required,
                'field_description': field.field_description,
                'def': defaults.get(field.name)
            }

            if field.ttype in ['one2many', 'many2many']:
                values.update({'children': self._get_fields(field.relation)})
            elif field.ttype == 'selection':
                if field.name == 'tz':
                    selection = dict(_tzs)
                else:
                    selection = dict(eval(field.selection))
                values.update({'selection': selection})
            elif field.ttype == 'many2one':
                domain = field.domain or []
                if active_model == 'hr.expense' and field.name == 'product_id':
                    domain += [('can_be_expensed', '=', True)]
                selects = request.env[field.relation].sudo().search(domain or [])
                selection = {}
                for select in selects:
                    if 'name' in select:
                        selection[select.id] = select.name
                    elif 'bank_id' in select:
                        selection[select.id] = select.bank_id.name
                values.update({'selection': selection})

            fields[field.name] = values

        return fields

    def _read_model(self, view_mode, active_model, kwargs):

        domain = []
        if active_model == 'hr.expense':
            domain.append(('employee_id', '=', request.env.user.employee_id.id))

        if kwargs.get('domain'):
            domain.append(eval(kwargs.get('domain')))

        active_ids = kwargs.get('active_ids')

        if active_ids:
            offset = None
            limit = len(active_ids)
            domain.append(('id', 'in', active_ids))
        else:
            try:
                offset = int(kwargs.get('offset'))
                limit = int(kwargs.get('limit'))
            except TypeError:
                offset = None
                limit = 20
                if view_mode == 'form':
                    domain.append(('id', '=', False))

        print('domain', domain)
        print('offset', offset)
        print('limit', limit)

        fields = self._get_fields(active_model=active_model, mode=view_mode)
        list_fields = [f for f in fields]
        records = request.env[active_model].sudo().search(domain, offset=offset, limit=limit).read(list_fields)
        total_records = request.env[active_model].sudo().search(domain, count=True)

        for record in records:
            record['attachments'] = request.env['ir.attachment'].sudo().search([('res_id', '=', record['id']), ('res_model', '=', active_model)]).read()
            record['attachment_number'] = len(record['attachments'])

            for field, value in fields.items():
                if value['ttype'] == 'binary':
                    try:
                        record[field] = record[field].decode('utf-8')
                    except AttributeError:
                        continue

        data = {
            'records': records,
            'total_records': total_records,
            'fields': fields,
        }
        return json.dumps(data, default=str)

    def _handle_attachments(self, active_model, active_id, kwargs):
        attachment_names = []
        if kwargs.get('attachment_ids'):
            attachment_names = kwargs.get('attachment_ids').split(',')
        documents = request.httprequest.files.getlist('documents')
        documents = [doc for doc in documents if doc.filename in attachment_names]

        current_attachments = request.env['ir.attachment'].sudo().search([
            ('res_id', '=', active_id),
            ('res_model', '=', active_model)
        ])

        attachment_ids = [a.id for a in current_attachments if a.name not in attachment_names]
        deleted_ids = request.env['ir.attachment'].sudo().browse(attachment_ids)

        if deleted_ids:
            deleted_ids.unlink()

        for document in documents:
            request.env['ir.attachment'].sudo().create({
                'name': document.filename,
                'type': 'binary',
                'res_id': active_id,
                'res_model': active_model,
                'datas': base64.b64encode(document.read()),
            })

    def _handle_extra_values(self, active_model, origin_values, kwargs):
        new_values = dict()
        if active_model == 'hr.expense':
            new_values['employee_id'] = request.env.user.employee_id.id
            if origin_values.get('product_id'):
                product_id = request.env['product.product'].sudo().browse([origin_values['product_id']])[0]
                new_values['tax_ids'] = [(4, tax.id, 0) for tax in product_id.supplier_taxes_id]
                new_values['account_id'] = product_id.property_account_expense_id.id
        elif active_model == 'hr.employee':
            if kwargs.get('image_1920_src'):
                if kwargs['image_1920_src'] == 'default':
                    new_values['image_1920'] = False
        origin_values.update(new_values)
        return origin_values

    def _prepare_values(self, active_model, fields, kwargs):
        values = {}
        for key, field in fields.items():
            value = kwargs.get(key)
            if value and field['ttype'] in ['integer', 'many2one']:
                try:
                    value = int(value)
                except ValueError:
                    value = False
            elif value and field['ttype'] in ['float', 'monetary']:
                value = float(value)
            elif value and field['ttype'] == 'binary':
                value = base64.b64encode(value.read())

            if value:
                values[key] = value

        values = self._handle_extra_values(active_model, values, kwargs)
        return values

    @http.route('/portal/home', type="http", auth="user", website=True, method=['GET'])
    def portal_home(self, **kwargs):
        if request.env.user.employee_id:
            context = {'menus': MENUS}
            return request.render("custom_website_portal.home_views", context)

    @http.route('/portal/action', type="http", auth="user", website=True, method=['GET'])
    def portal_action(self, **kwargs):
        if request.env.user.employee_id:
            request.session['menu'] = MENUS[kwargs['menu']]['menus']
            action_url = f'/portal/{kwargs["view_mode"]}/{kwargs["model"]}'
            if kwargs['model'] == 'hr_employee':
                action_url += '/' + str(request.env.user.employee_id.id)
            return request.redirect(action_url)

    @http.route('/portal/list/<string:active_model>', type="http", auth="user", website=True, method=['GET'])
    def portal_list_view(self, active_model, **kwargs):
        if request.env.user.employee_id:
            context = {'model': active_model.replace('_', '.')}
            return request.render('custom_website_portal.list_views', context)

    @http.route([
        '/portal/form/<string:active_model>',
        '/portal/form/<string:active_model>/<int:active_id>'
    ], type="http", auth="user", website=True, method=['GET'])
    def portal_form_view(self, active_model, active_id=None, **kwargs):
        if request.env.user.employee_id:
            context = {'model': active_model.replace('_', '.'), 'id': active_id}
            return request.render('custom_website_portal.' + active_model + '_form_view', context)

    @http.route([
        '/portal/<string:action>/<string:view_mode>/<string:active_model>',
        '/portal/<string:action>/<string:view_mode>/<string:active_model>/<int:active_id>',
        '/portal/<string:action>/<string:view_mode>/<string:active_model>/<string:active_ids>'
    ], type="http", auth="user", website=True, method=['POST'])
    def employee_crud(self, action, view_mode, active_model, active_id=None, active_ids=None, **kwargs):

        response = {'code': 99, 'message': 'Something went wrong!'}
        if request.env.user.employee_id:

            active_model = active_model.replace('_', '.')
            if active_ids:
                if active_ids == 'new':
                    active_ids = []
                else:
                    active_ids = [int(act_id) for act_id in active_ids.split(',')]
            else:
                if active_id:
                    active_ids = [active_id]
                else:
                    active_ids = []

            kwargs['active_id'] = active_id
            kwargs['active_ids'] = active_ids

            fields = self._get_fields(active_model, mode=view_mode)
            values = self._prepare_values(active_model, fields, kwargs)
            list_fields = [f for f in fields]

            if action == 'create':
                if active_model == 'hr.expense':
                    record = request.env[active_model].sudo().create(values)
                    self._handle_attachments(active_model, record.id, kwargs)
                    response = {'code': 0, 'record': record.read(list_fields)[0], 'message': 'Record successfully created!'}

            elif action == 'read':
                return self._read_model(view_mode, active_model, kwargs)

            elif action == 'update':
                record = request.env[active_model].sudo().browse(active_id)
                if (active_model == 'hr.expense' and request.env.user.employee_id.id == record.employee_id.id) or active_model == 'hr.employee':
                    record.update(values)
                    self._handle_attachments(active_model, record.id, kwargs)
                    response = {'code': 0, 'record': record.read(list_fields)[0], 'message': 'Record successfully updated!'}

            elif action == 'delete':
                if active_model == 'hr.expense':
                    records = request.env[active_model].sudo().browse(active_ids)
                    if all([record.employee_id.id == request.env.user.employee_id.id for record in records]):
                        records.unlink()
                        response = {'code': 0, 'message': 'Records successfully deleted!'}

        return json.dumps(response, default=str)
