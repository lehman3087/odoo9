# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Enapps LTD (<http://www.enapps.co.uk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from  openerp.osv import osv,fields
from psycopg2.extensions import adapt
from openerp.exceptions import UserError,Warning

class ea_import_template_unique_rule(osv.osv):

    _name = 'ea_import.template.unique.rule'

    _rec_name = 'source_field_id'

    _columns = {
        'source_field_id': fields.many2one('ir.model.fields', 'Template Line Fields', required=True),
        'comparison_model_id': fields.many2one('ir.model', 'Comparison Model', required=True),
        'target_field_id': fields.many2one('ir.model.fields', 'Target Model Fields', required=True),
        'template_id': fields.many2one('ea_import.template', 'EA import template'),
        'source_model_id': fields.related('template_id',
                                          'target_model_id',
                                          type='integer',
                                          string="Import Template Model",
                                          readonly=True, ),
    }

    def default_get(self, cr, uid, fields, context=None):
        # getting comparison_model_id
        if context is None:
            context = {}
        result = super(ea_import_template_unique_rule, self).default_get(cr, uid, fields, context=context)
        if 'target_model_id' in context:
            result.update({'source_model_id': context.get('target_model_id')})
        return result

    def onchange_model_id(self, cr, uid, ids, model_id, context={}):
        # onchange model id running
        if not model_id:
            return {'value': {}}
        return {'value': {'target_field_id': '', }}

    def onchange_target_field_id(self, cr, uid, ids, target_field_id, context={}):
        if target_field_id:
            field_in_table = self.check_field_in_table_presense(cr, uid, ids, target_field_id, context=None)
            if not field_in_table.get('field_present'):
                raise osv.except_osv(('Error !'), ('%s is not storable and can not be selected as target field') % (field_in_table.get('target_field_name')))
        return {}

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('target_field_id'):
            field_in_table = self.check_field_in_table_presense(cr, uid, ids, vals.get('target_field_id'), context=None)
            if not field_in_table.get('field_present'):
                raise osv.except_osv(('Error !'), ('%s is not storable and can not be selected as target field') % (field_in_table.get('target_field_name')))
        return super(ea_import_template_unique_rule, self).write(cr, uid, ids, vals, context)

    def check_field_in_table_presense(self, cr, uid, ids, target_field_id, context=None):
        res = {}
        if target_field_id:
            target_field_obj = self.pool.get('ir.model.fields').browse(cr, uid, target_field_id, context=None)
            target_field_name = target_field_obj.name
            target_field_description = target_field_obj.field_description
            model_name = target_field_obj.model_id.model
            comparison_model_table = self.pool.get(model_name)._table
            cr.execute('''SELECT column_name
                          FROM information_schema.columns
                          WHERE table_name = '%s'
                          AND column_name = '%s' ''' % (comparison_model_table, target_field_name, ))
            result = cr.fetchall()
            res = {'field_present': bool(result), 'target_field_name': target_field_description}
        return res

ea_import_template_unique_rule()


class ea_import_template(osv.osv):
    _name = 'ea_import.template'

    _order = 'target_model_id, chain_id, sequence'
    _columns = {
        'name': fields.char('Name', size=256),
        'target_model_id': fields.many2one('ir.model', 'Target Model'),
        'test_input_file': fields.binary('Test Importing File'),
        'update': fields.boolean('Update exist',),
        'update_current': fields.boolean('Update only current records',),
        'create_new': fields.boolean('Create New',),
        'create_unique_only': fields.boolean('Create Unique only', help="Create record only if one matching key does not already exist.  Do not use with 'update'."),
        'line_ids': fields.one2many('ea_import.template.line', 'template_id', 'Template Lines', ),
        'matching_rules_ids': fields.one2many('ea_import.template.unique.rule', 'template_id', 'Import Unique Rule'),
        'chain_id': fields.many2one('ea_import.chain', 'Import Chain'),
        'sequence': fields.integer('Sequence',),
        'post_import_hook': fields.char('Post-import method', size=512,
                                        help="Execute method after importing all records.\n"\
                                        "<target_model>.<function_name>(cr, uid, ids_of_imported_records, context=context)"),
        }

    _defaults = {
        'sequence': 1,
    }

    def generate_record(self, cr, uid, ids, record_list, row_number, context={}):
        result = []
        if len(record_list):
            for template in self.browse(cr, uid, ids, context=context):
                target_model_pool = self.pool.get(template.target_model_id.model)
                record = {}
                upd_key = []
                updated = False
                ready_to_create_new = True
                for template_line in template.line_ids:

                    field_name = template_line.target_field.name
                    #print(field_name)
                    value = template_line.get_field(record_list, row_number, testing=True, context=context)

                    #print(value)

                    if value:

                        record.update({field_name: value})
                        if template_line.key_field:
                            upd_key.append((template_line.target_field.name, '=', value))
                    else:
                        if template_line.required:
                            ready_to_create_new = False
                if template.create_new and template.create_unique_only and upd_key:
                    #check if record matching key already exists
                    if self.low_level_search(cr, uid, ids, upd_key, context=context):
                        log_notes = "Record already exists - skipping ", record
                        context['import_log'].append(log_notes)
                        return result
                    #checking if record matching key already exists in fields defined in matching rules
                    matching_model_field_ids = []
                    for template_line in template.line_ids:
                        field_name = template_line.target_field.name
                        value = template_line.get_field(record_list, row_number, testing=True, context=context)
                        for matching_value in template.matching_rules_ids:
                            if matching_value.source_field_id.name == field_name:
                                matching_model = matching_value.comparison_model_id.model
                                matching_model_upd_key = []
                                matching_model_upd_key.append((matching_value.target_field_id.name, '=', value))
                                kwargs = {'matching_model_name': matching_model}
                                matching_model_field_ids = self.low_level_search(cr, uid, ids, matching_model_upd_key, context=context, **kwargs)
                                if matching_model_field_ids:
                                    log_notes = ("Rules on other models checking:\
                                                  record already exists in model '%s';\
                                                  field: %s; value: %s - skipping " % (matching_model,
                                                                                       matching_value.target_field_id.name,
                                                                                       value)), record
                                    context['import_log'].append(log_notes)
                    if matching_model_field_ids:
                        return result
                    else:
                        try:
                            new_rec_id = target_model_pool.create(cr, uid, record, context=context)
                        except Exception, e:
                            raise Warning(('Error creating record!'), ("Error message: %s\nRow Number: %s\n\nRecord: %s" % (e, row_number, record)))
                        new_rec = target_model_pool.browse(cr, uid, new_rec_id)
                        if getattr(new_rec, target_model_pool._rec_name):
                            log_row_name = getattr(new_rec, target_model_pool._rec_name)
                        else:
                            log_row_name = ''
                        log_notes = "creating ", target_model_pool._name, "- name = ", new_rec._rec_name, "- data = ", record
                        context['import_log'].append(log_notes)
                        result.append(new_rec_id)
                        return result
                if template.update and upd_key:
                    if template.update_current:
                        upd_key.append(('create_date', '>', context['time_of_start']))
                    updating_record_id = self.low_level_search(cr, uid, ids, upd_key, context=context)
                    if updating_record_id:
                        existing_rec = target_model_pool.browse(cr, uid, updating_record_id)[0]
                        if existing_rec.name:
                            log_row_name = existing_rec.name
                        else:
                            log_row_name = ''
                        if self.need_to_update(cr, uid, target_model_pool, updating_record_id, record, context=context):
                            target_model_pool.write(cr, uid, updating_record_id, record, context=context)
                            result.append(updating_record_id[0])
                            log_notes = "update ", target_model_pool._name, "- record id = ", updating_record_id, "- name = ", log_row_name, "- data = ", record
                            context['import_log'].append(log_notes)
                        else:
                            log_notes = "no update ", target_model_pool._name, "- record id = ", updating_record_id, "- name = ", log_row_name, "- NO CHANGES REQUIRED - data = ", record
                            context['import_log'].append(log_notes)
                        updated = True
                if not updated and template.create_new and ready_to_create_new:
                    try:
                        new_rec_id = target_model_pool.create(cr, uid, record, context=context)
                    except Exception, e:
                        raise Warning(('Error creating record!'), ("Error message: %s\nRow Number: %s\n\nRecord: %s" % (e, row_number, record)))
                    new_rec = target_model_pool.browse(cr, uid, new_rec_id)
                    if new_rec._rec_name:
                        log_row_name = new_rec._rec_name
                    else:
                        log_row_name = ''
                    log_notes = "creating ", target_model_pool._name, "- name = ", new_rec._rec_name, "- data = ", record
                    context['import_log'].append(log_notes)
                    result.append(new_rec_id)
        return result

    def get_related_id(self, cr, uid, ids, input_list, row_number, context={}):
        result = []
        for template in self.browse(cr, uid, ids, context=context):
            key = []
            for template_line in template.line_ids:
                if template_line.key_field:
                    field_name = template_line.target_field.name
                    value = template_line.get_field(input_list, row_number, testing=True)
                    if value:
                        key.append((field_name, '=', value))
            if template.update_current:
                key.append(('create_date', '>', context['time_of_start']))
            result = self.low_level_search(cr, uid, [template.id], key, context=context)
            return result

    def low_level_search(self, cr, uid, ids, key_list, context={}, **kwargs):
        if not kwargs.get('matching_model_name'):
            for template in self.browse(cr, uid, ids, context=context):
                model = template.target_model_id.model
        else:
            model = kwargs.get('matching_model_name')
        target_model_pool = self.pool.get(model)
        where_string = "WHERE id IS NOT NULL\n"
        for key_sub_list in key_list:
            if isinstance(key_sub_list[2], basestring):
                second_parametr = adapt(key_sub_list[2]).getquoted()
            else:
                second_parametr = key_sub_list[2]
            where_string += "AND {0} {1} {2} \n".format(key_sub_list[0], key_sub_list[1], second_parametr)
        cr.execute("""
                    SELECT *
                    FROM %s
                    %s""" % (target_model_pool._table, where_string))
        result = cr.fetchall()
        result = [id_numders[0] for id_numders in result]
        return result

    def need_to_update(self, cr, uid, target_model_pool, updating_record_id, record, context={}):
        for old_record in target_model_pool.read(cr, uid, updating_record_id, context=context):
            filtered_old_record = {}
            for key, value in old_record.items():
                if isinstance(value, tuple):
                    filtered_old_record[key] = value[0]
                elif isinstance(value, dict):
                    continue
                else:
                    filtered_old_record[key] = value
        return any([filtered_old_record.get(key) != value for key, value in record.items()])

    def update_templates(self, cr, uid):
        """Relink templates from old table 'ea_import_chain_link'
        directly to ea_import_chain
        """
        cr.execute("""SELECT *
                    FROM information_schema.tables
                    WHERE table_name='ea_import_chain_link'""")
        if cr.fetchone():
            cr.execute("""UPDATE ea_import_template tmpl
                        SET sequence = q1.sequence,
                            chain_id = q1.chain_id,
                            post_import_hook = q1.post_import_hook
                        FROM (SELECT eit.id,
                            eicl.sequence,
                            eicl.chain_id,
                            eicl.post_import_hook
                              from ea_import_template eit
                              LEFT JOIN ea_import_chain_link eicl ON eicl.template_id = eit.id) as q1
                        WHERE tmpl.id = q1.id
            """)
        return True

ea_import_template()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
