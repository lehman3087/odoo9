# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Enapps LTD (<http://www.enapps.co.uk>).
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

from openerp.osv import osv, fields
try:
    # We must use FTP_TLS if SSL required which is not available under python 2.6
    from ftplib import FTP_TLS
except:
    from ftplib import FTP


class ftp_config(osv.osv):
    _name = 'import.ftp_config'
    _rec_name = 'name'

    _columns = {
        'name': fields.char('Name', size=512),
        'host': fields.char('Host', size=512, required=True),
        'port': fields.integer('Port'),
        'username': fields.char('Username', size=512, required=True),
        'passwd': fields.char('Password', size=512, required=True),
    }

    _defaults = {
        'host': 'localhost',
        'port': 21,
    }

    def test_connection(self, cr, uid, ids, context={}):
        for ftp in self.browse(cr, uid, ids, context=context):
            conn = False
            try:
                # Perhaps to include timeout?
                conn = FTP_TLS(host=ftp.host, user=ftp.username, passwd=ftp.passwd)

            except:
                conn = FTP(host=ftp.host, user=ftp.username, passwd=ftp.passwd)

            if not conn:
                raise osv.except_osv(('Error!'), ("Connection can not be established!\nPlease, check you settings"))

            conn.quit()
        raise osv.except_osv(('!'), ("Connection Succeed!"))

ftp_config()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
