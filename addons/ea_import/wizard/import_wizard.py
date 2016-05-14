# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 ENNAPS LTD (<http://www.enapps.co.uk>).
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


class import_wizard(osv.osv_memory):

    _name = 'import_wizard'
    _description = 'Simple import wizard'

    _columns = {
        'chain_id': fields.many2one('ea_import.chain', 'Import Chain', ),
        'import_file': fields.binary('Importing file', ),
        'type': fields.selection([
                            ('csv', 'CSV Import'),
                            ('ftp', 'Import from ftp server'),
                            ('mysql', 'MySql Import'),
                            ], 'Import Type',
                            required=True,
                            readonly=True,
                            help="Type of connection import will be done from"),
    }

    _defaults = {
         'chain_id': lambda cr, uid, ids, context: context.get('import_chain_id'),
         'type': lambda self, cr, uid, ctx={}: ctx.get('import_chain_id') and self.pool.get('ea_import.chain').browse(cr, uid, ctx['import_chain_id'], context=ctx).type,
    }

    def do_import(self, cr, uid, ids, context={}):
        for wizard in self.browse(cr, uid, ids, context=context):
            wizard.chain_id.write({'input_file': wizard.import_file})
            cr.commit()
            wizard.chain_id.import_to_db()
        return {'type': 'ir.actions.act_window_close'}

import_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
