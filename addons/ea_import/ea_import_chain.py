# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
import base64
import csv
import re
import MySQLdb as mdb
import datetime
from openerp.exceptions import UserError,Warning
from openerp.http import request, serialize_exception as _serialize_exception
from cStringIO import StringIO
try:
    from ftplib import FTP_TLS
except:
    from ftplib import FTP


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, charset='utf-8', **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data, charset),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, charset) for cell in row]


def utf_8_encoder(unicode_csv_data, charset):
    for line in unicode_csv_data:
        yield line
        #yield line.decode(charset).encode('utf-8', 'ignore')


class ea_import_chain(osv.osv):
    _name = 'ea_import.chain'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'type': fields.selection([
            ('csv', 'CSV Import'),
            ('ftp', 'Import from ftp server'),
            ('mysql', 'MySql Import'),
        ], 'Import Type', required=True, help="Type of connection import will be done from"),
        'mysql_config_id': fields.many2one('mysql.config', 'MySql configuration'),
        'ftp_config_id': fields.many2one('import.ftp_config', 'FTP Configuration'),
        'input_file': fields.binary('Test Importing File', required=False),
        'header': fields.boolean('Header'),
        'template_ids': fields.one2many('ea_import.template', 'chain_id', 'Templates', ),
        'result_ids': fields.one2many('ea_import.chain.result', 'chain_id', 'Import Results', ),  # to be removed
        'log_ids': fields.one2many('ea_import.log', 'chain_id', 'Import Log', ),
        'separator': fields.selection([
            (",", '<,> - Coma'),
            (";", '<;> - Semicolon'),
            ("\t", '<TAB> - Tab'),
            (" ", '<SPACE> - Space'),
        ], 'Separator', required=True),
        'delimiter': fields.selection([
            ("'", '<\'> - Single quotation mark'),
            ('"', '<"> - Double quotation mark'),
            ('None', 'None'),
        ], 'Delimiter', ),
        'charset': fields.selection([
            ('us-ascii', 'US-ASCII'),
            ('utf-7', 'Unicode (UTF-7)'),
            ('utf-8', 'Unicode (UTF-8)'),
            ('utf-16', 'Unicode (UTF-16)'),
            ('windows-1250', 'Central European (Windows 1252)'),
            ('windows-1251', 'Cyrillic (Windows 1251)'),
            ('iso-8859-1', 'Western European (ISO)'),
            ('iso-8859-15', 'Latin 9 (ISO)'),
        ], 'Encoding', required=True),
        'model_id': fields.many2one('ir.model', 'Related document model'),
        'ir_act_window_id': fields.many2one('ir.actions.act_window', 'Sidebar action', readonly=True, ),
        'ir_value_id': fields.many2one('ir.values', 'Sidebar button', readonly=True, ),
        }

    _defaults = {
        'separator': ",",
        'charset': 'utf-8',
        'delimiter': None,
        'type': 'csv',
    }

    def copy(self, cr, uid, id, default=None, context=None):
            if default is None:
                default = {}
            default.update({'result_ids': [],
                            'log_ids': [],
                            'ir_act_window_id': False,
                            'ir_value_id': False,
                            })
            return super(ea_import_chain, self).copy(cr, uid, id, default, context)

    def get_mysql_data(self, config_obj):
        connect = mdb.connect(host=config_obj.host, user=config_obj.username,
                           passwd=config_obj.passwd, db=config_obj.db)
        connect.escape_string("'")
        cursor = connect.cursor()
        if re.match(r'CREATE|DROP|UPDATE|DELETE', config_obj.query, re.IGNORECASE):
            raise Warning(('Error !'), ("Operation prohibitet!"))
        cursor.execute(config_obj.query)
        data = cursor.fetchall()
        connect.close()
        return '\n'.join([row[1:-2] for row in [str(item) + ',' for item in data]])

    def get_ftp_data(self, cr, uid, ids, context={}):
        for chain in self.browse(cr, uid, ids, context=context):
            config_obj = chain.ftp_config_id
            try:
                conn = FTP_TLS(host=config_obj.host, user=config_obj.username, passwd=config_obj.passwd)
                conn.prot_p()
            except:
                conn = FTP(host=config_obj.host, user=config_obj.username, passwd=config_obj.passwd)
            filenames = conn.nlst()
            for filename in filenames:
                input_file = StringIO()
                conn.retrbinary('RETR %s' % filename, lambda data: input_file.write(data))
                input_string = input_file.getvalue()
                input_file.close()
                csv_reader = unicode_csv_reader(StringIO(input_string), delimiter=str(chain.separator), quoting=(not chain.delimiter and csv.QUOTE_NONE) or csv.QUOTE_MINIMAL, quotechar=chain.delimiter and str(chain.delimiter) or None, charset=chain.charset)
                self.import_to_db(cr, uid, ids, csv_reader=csv_reader, context=context)
                conn.delete(filename)
            conn.quit()
        return True

    def check_active_ids(self, context={}):
        """Checks whether import is run from form view
        of object with model name defined above if there
        is template line defined with relational type of
        'active_id'.
        """
        if not context.get('active_id') or len(context.get('active_ids', [])) > 1:
            raise Warning('Error!', "This import template can be used only from form view!")
        return True

    def import_to_db(self, cr, uid, ids, context={}, csv_reader=False):

        if not csv_reader:
            time_of_start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            context.update({'time_of_start': time_of_start})
            context['result_ids'] = []
            context['log_id'] = []
            context['import_log'] = []
        result_pool = self.pool.get('ea_import.chain.result')

        log_pool = self.pool.get('ea_import.log')
        for chain in self.browse(cr, uid, ids, context=context):
            #print(chain)
            if not chain.type:
                raise Warning(('Error !'), ("No connection type specified!"))
            if chain.type == 'csv' and not csv_reader:
                csv_reader = unicode_csv_reader(StringIO(base64.b64decode(chain.input_file)), delimiter=str(chain.separator), quoting=(not chain.delimiter and csv.QUOTE_NONE) or csv.QUOTE_MINIMAL, quotechar=chain.delimiter and str(chain.delimiter) or None, charset=chain.charset)
            elif chain.type == 'mysql' and not csv_reader:
                input_data = self.get_mysql_data(chain.mysql_config_id)
                csv_reader = unicode_csv_reader(StringIO(input_data), delimiter=str(chain.separator), quoting=(not chain.delimiter and csv.QUOTE_NONE) or csv.QUOTE_MINIMAL, quotechar=chain.delimiter and str(chain.delimiter) or None, charset=chain.charset)
            elif chain.type == 'ftp' and not csv_reader:
                self.get_ftp_data(cr, uid, ids, context=context)
                continue

            if chain.header:
                csv_reader.next()
            result = {}
            if any([True for template in chain.template_ids for line in template.line_ids if line.field_type == 'many2one' and line.many2one_rel_type == 'active_id']):
                self.check_active_ids(context=context)
            for template in chain.template_ids:
                model_name = template.target_model_id.model
                result.update({model_name: {'ids': set([]), 'post_import_hook': template.post_import_hook}})

            for row_number, record_list in enumerate(csv_reader):

                if len(record_list) < max([template_line.sequence for template_line in template.line_ids for template in chain.template_ids]):
                    raise Warning(('Error !'), ("Invalid File or template definition. You have less columns in file than in template. Check the file separator or delimiter or template."))
                #print(row_number)
                #print(chain.template_ids)
                for template in sorted(chain.template_ids, key=lambda k: k.sequence):

                    model_name = template.target_model_id.model
                    #print(model_name)
                    result_id = template.generate_record(record_list, row_number, context=context)
                    fields = []
                    for template_line in template.line_ids:
                        field_name = template_line.target_field.name
                        fields.append(field_name)
                    result[model_name]['lines'] = fields
                    result[model_name]['ids'] = result[model_name]['ids'] | set(result_id)

            for name, imported_ids, post_import_hook,lines in [(name, value['ids'], value['post_import_hook'],value['lines']) for name, value in result.iteritems()]:

                if post_import_hook and hasattr(self.pool.get(name), post_import_hook):
                    getattr(self.pool.get(name), post_import_hook)(cr, uid, list(imported_ids), context=context)


                Model=request.session.model(name)
                import_data = Model.export_data(list(imported_ids), lines, True, context=context).get('datas',[])
                #print(self.from_data(lines,import_data))
                result_ids_file = base64.b64encode(self.from_data(lines,import_data))
                result_ids_ids = base64.b64encode(str(list(imported_ids)))
                # print(result_ids_file)
                #result_ids_file = base64.b64encode(str(list(imported_ids)))
                result_ids = result_pool.create(cr, uid, {
                    'chain_id': chain.id,
                    'result_ids_file': result_ids_ids,
                    'result_ids_csv': result_ids_file,
                        'name': name,
                    'import_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                context['result_ids'].append(result_ids)

            log_id = log_pool.create(cr, uid, {
                'chain_id': chain.id,
                'import_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

            result_pool.write(cr, uid, context.get('result_ids', []), {'log_id': log_id}, context=context)
            log_line_obj = self.pool.get('ea_import.log.line')
            for line in context.get('import_log', []):
                log_line_obj.create(cr, uid, {
                'log_id': log_id,
                'name': line
            })
            context['log_id'].append(log_id)
        return True

    def from_data(self, fields, rows):
        #print('1111')
        fp = StringIO()
        writer = csv.writer(fp, quoting=csv.QUOTE_ALL)

        writer.writerow([name.encode('utf-8') for name in fields])

        for data in rows:
            #print(data)
            row = []
            for d in data:

                if isinstance(d, basestring):
                    d = d.replace('\n',' ').replace('\t',' ')

                    try:
                        d = d.encode('utf-8')
                    except UnicodeError:
                        pass
                if d is False: d = None
                row.append(d)
            writer.writerow(row)

        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool.get('ir.actions.act_window')
        for chain in self.browse(cr, uid, ids, context=context):
            model_name = chain.model_id.model
            button_name = 'Import from CSV (%s)' % chain.name
            vals['ir_act_window_id'] = action_obj.create(cr, uid, {
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'import_wizard',
                'src_model': model_name,
                'view_type': 'form',
                'context': "{'import_chain_id': %d}" % chain.id,
                'view_mode': 'form,tree',
                'res_id': chain.id,
                'target': 'new',
                'auto_refresh': True,
            }, context)
            vals['ir_value_id'] = self.pool.get('ir.values').create(cr, uid, {
                 'name': button_name,
                 'model': model_name,
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(vals['ir_act_window_id']),
                 'object': True,
             }, context)
        self.write(cr, uid, ids, {
                    'ir_act_window_id': vals.get('ir_act_window_id', False),
                    'ir_value_id': vals.get('ir_value_id', False),
                }, context)
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        for chain in self.browse(cr, uid, ids, context=context):
            if chain.ir_act_window_id:
                self.pool.get('ir.actions.act_window').unlink(cr, uid, chain.ir_act_window_id.id, context)
            if chain.ir_value_id:
                ir_values_obj = self.pool.get('ir.values')
                ir_values_obj.unlink(cr, uid, chain.ir_value_id.id, context)
        return True

ea_import_chain()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
