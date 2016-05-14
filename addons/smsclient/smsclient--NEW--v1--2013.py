# -*- coding: utf-8 -*-
import time
import urllib
from openerp.osv import fields, orm
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)
try:
    from SOAPpy import WSDL
except :
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install it:"
    " e.g.: apt-get install python-soappy")

# //!!!!!!!+++++++++++++++++ avs3@i.ua
import os, urllib2
from threading import Thread
import smpplib.client, smpplib.gsm, smpplib.consts


class partner_sms_send(orm.Model):
    _name = "partner.sms.send"

    def _default_get_mobile(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        partner_pool = self.pool.get('res.partner')
        active_ids = fields.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(cr, uid, active_ids, context=context): 
            i += 1           
            res = partner.mobile
        if i > 1:
            raise orm.except_orm(_('Error'), _('You can only select one partner'))
        return res

    def _default_get_gateway(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_ids = sms_obj.search(cr, uid, [], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False

    def onchange_gateway(self, cr, uid, ids, gateway_id, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        if not gateway_id:
            return {}
        gateway = sms_obj.browse(cr, uid, gateway_id, context=context)
        return {
            'value': {
                'validity': gateway.validity, 
                'classes': gateway.classes,
                'deferred': gateway.deferred,
                'priority': gateway.priority,
                'coding': gateway.coding,
                'tag': gateway.tag,
                'nostop': gateway.nostop,
            }
        }

    _columns = {
        'mobile_to': fields.char('To', size=256, required=True),
        'app_id': fields.char('API ID', size=256),
        'user': fields.char('Login', size=256),
        'password': fields.char('Password', size=256),
        'text': fields.text('SMS Message', required=True),
        'gateway': fields.many2one('sms.smsclient', 'SMS Gateway', required=True),
        'validity': fields.integer('Validity',
            help='the maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='the time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0','0'),
                ('1','1'),
                ('2','2'),
                ('3','3')
            ], 'Priority', help='The priority of the message'),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256, help='an optional tag'),
        'nostop': fields.selection([
                ('0', '0'),
                ('1', '1')
            ], 'NoStop',
            help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
    }

    _defaults = {
        'mobile_to': _default_get_mobile,
        'gateway': _default_get_gateway,        
    }
    
    def sms_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        client_obj = self.pool.get('sms.smsclient')
        for data in self.browse(cr, uid, ids, context=context):
            if not data.gateway:
                raise orm.except_orm(_('Error'), _('No Gateway Found'))
            else:
                client_obj._send_message(cr, uid, data, context=context)
        return {}


class SMSClient(orm.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    _columns = {
        'name': fields.char('Gateway Name', size=256, required=True),
        'url': fields.char('Gateway URL', size=256,
            required=True, help='Base url for message'),
        'property_ids': fields.one2many('sms.smsclient.parms',
            'gateway_id', 'Parameters'),
        'history_line': fields.one2many('sms.smsclient.history',
            'gateway_id', 'History'),
        'method': fields.selection([
                ('http', 'HTTP Method'),
                ('smpp', 'SMPP Method')
                
                # //+++++++++++++++++ avs3@i.ua
                ,('http_atompark_xml', 'HTTP (AtomPark XML)')
                ,('smpp_real', 'SMPP (real)')
                
            ], 'API Method', select=True),
        'state': fields.selection([
                ('new', 'Not Verified'),
                ('waiting', 'Waiting for Verification'),
                ('confirm', 'Verified'),
            ], 'Gateway Status', select=True, readonly=True),
        'users_id': fields.many2many('res.users',
            'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'code': fields.char('Verification Code', size=256),
        'body': fields.text('Message',
            help="The message text that will be send along with the email which is send through this server"),
        'validity': fields.integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class',
            help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message '),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ],'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256, help='an optional tag'),
        'nostop': fields.selection([
                ('0', '0'),
                ('1', '1')
            ], 'NoStop',
            help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
    }

    _defaults = {
        'state': 'new',
        'method': 'http',
        'validity': 10,
        'classes': '1',
        'deferred': 0, 
        'priority': '3',
        'coding': '1',
        'nostop': '1',
    }

    def _check_permissions(self, cr, uid, id, context=None):
        cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    # //+++++++++++++++++ avs3@i.ua
    # def _prepare_smsclient_queue(self, cr, uid, data, name, context=None):
    def _prepare_smsclient_queue(self, cr, uid, data, name, params, context=None):
        return {
            'name': name,
            
            # //+++++++++++++++++ avs3@i.ua
            'params': params,
            
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': data.validity, 
            'classes': data.classes, 
            'deffered': data.deferred, 
            'priorirty': data.priority, 
            'coding': data.coding, 
            'tag': data.tag, 
            'nostop': data.nostop,
        }

    def _send_message(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        gateway = data.gateway
        if gateway:
            if not self._check_permissions(cr, uid, gateway.id, context=context):
                raise orm.except_orm(_('Permission Error!'), _('You have no permission to access %s ') % (gateway.name,))
            url = gateway.url
            name = url
            
            # //+++++++++++++++++ avs3@i.ua
            params = {}
            
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway.property_ids:
                     if p.type == 'user':
                         prms[p.name] = p.value
                     elif p.type == 'password':
                         prms[p.name] = p.value
                     elif p.type == 'to':
                         prms[p.name] = data.mobile_to
                     elif p.type == 'sms':
                         prms[p.name] = data.text
                     elif p.type == 'extra':
                         prms[p.name] = p.value
                params = urllib.urlencode(prms)
                name = url + "?" + params
            
            # //+++++++++++++++++ avs3@i.ua
            if gateway.method == 'http_atompark_xml':
                _username = _password = _sender = _text = _number = ''
                for p in data.gateway.property_ids:
                    if   p.type == 'user':
                        _username = p.value
                    elif p.type == 'password':
                        _password = p.value
                    elif p.type == 'sender':
                        _sender = p.value
                    elif p.type == 'sms':
                        _text = data.text
                    elif p.type == 'to':
                        _number = data.mobile_to
                params = '''<?xml version="1.0" encoding="UTF-8"?>
<SMS>
<operations>
<operation>SEND</operation>
</operations>
<authentification>
<username>%s</username>
<password>%s</password>
</authentification>
<message>
<sender>%s</sender>
<text>%s</text>
</message>
<numbers>
<number>%s</number>
</numbers>
</SMS>''' % (_username, _password, _sender, _text, _number)
                params = [('XML', params.encode('utf-8'))]
                params = urllib.urlencode(params)
                
                name = url
            
            queue_obj = self.pool.get('sms.smsclient.queue')
            
            # //+++++++++++++++++ avs3@i.ua
            # vals = self._prepare_smsclient_queue(cr, uid, data, name, context=context)
            vals = self._prepare_smsclient_queue(cr, uid, data, name, params, context=context)
            
            queue_obj.create(cr, uid, vals, context=context)
        return True

    def _check_queue(self, cr, uid, context=None):
        if context is None:
            context = {}
        
        # //!!!!!!!+++++++++++++++++ avs3@i.ua
        check_smpp_work()
        
        queue_obj = self.pool.get('sms.smsclient.queue')
        history_obj = self.pool.get('sms.smsclient.history')
        sids = queue_obj.search(cr, uid, [
                ('state', '!=', 'send'),
                ('state', '!=', 'sending')
            ], limit=30, context=context)
        queue_obj.write(cr, uid, sids, {'state': 'sending'}, context=context)
        error_ids = []
        sent_ids = []
        for sms in queue_obj.browse(cr, uid, sids, context=context):
            if len(sms.msg) > 160:
                error_ids.append(sms.id)
                continue
            if sms.gateway_id.method == 'http':
                try:
                    urllib.urlopen(sms.name)
                except Exception, e:
                    raise orm.except_orm('Error', e)
            
            # //+++++++++++++++++ avs3@i.ua
            if sms.gateway_id.method == 'http_atompark_xml':
                try:
                    req = urllib2.Request(sms.name, sms.params)
                    req.add_header("Content-type", "application/x-www-form-urlencoded")
                    urllib2.urlopen(req)
                except Exception, e:
                    raise orm.except_orm('http_atompark_xml - Error:', e)
            
            ### New Send Process OVH Dedicated ###
            ## Parameter Fetch ##
            if sms.gateway_id.method == 'smpp':
                for p in sms.gateway_id.property_ids:
                    if p.type == 'user':
                        login = p.value
                    elif p.type == 'password':
                        pwd = p.value
                    elif p.type == 'sender':
                        sender = p.value
                    elif p.type == 'sms':
                        account = p.value
                try:
                    soap = WSDL.Proxy(sms.gateway_id.url)
                    result = soap.telephonySmsUserSend(str(login), str(pwd),
                        str(account), str(sender), str(sms.mobile), str(sms.msg),
                        int(sms.validity), int(sms.classes), int(sms.deferred),
                        int(sms.priority), int(sms.coding), int(sms.nostop))
                    ### End of the new process ###
                except Exception, e:
                    raise orm.except_orm('Error', e)
            
            # //!!!!!!!!!!!!!+++++++++++++++++ avs3@i.ua
            if sms.gateway_id.method == 'smpp_real':
                sender = 'OpenERP'
                for p in sms.gateway_id.property_ids:
                    if p.type == 'sender':
                        sender = str(p.value)
                phone = str(sms.mobile)
                text = unicode(sms.msg)
                try:
                    check_smpp_work()
                    smpp_work.send(sender, phone, text)
                except Exception, e:
                    raise orm.except_orm('smpp_real - Error:', e)
            
            history_obj.create(cr, uid, {
                            'name': _('SMS Sent'),
                            'gateway_id': sms.gateway_id.id,
                            'sms': sms.msg,
                            'to': sms.mobile,
                        }, context=context)
            sent_ids.append(sms.id)
        queue_obj.write(cr, uid, sent_ids, {'state': 'send'}, context=context)
        queue_obj.write(cr, uid, error_ids, {
                                        'state': 'error',
                                        'error': 'Size of SMS should not be more then 160 char'
                                    }, context=context)
        return True
    
    # //!!!!!!!+++++++++++++++++ avs3@i.ua
    def write(self, cr, uid, ids, vals, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if 'method' in vals:
            _method = vals['method']
        else:
            _method = obj.method
        if 'url' in vals:
            _url = vals['url']
        else:
            _url = obj.url
        if _method == 'smpp_real':
            host = port = username = password = ''
            if ':' in _url:
                host, port = _url.split(':')
            cr.execute('SELECT value, type FROM sms_smsclient_parms WHERE gateway_id=%s', (ids[0],))
            for p in cr.dictfetchall():
                if   p['type'] == 'user':
                    username = p['value']
                elif p['type'] == 'password':
                    password = p['value']
            f = open(os.path.dirname(__file__) + '/smpp.conf', 'wb')
            for s in (host, port, username, password):
                try:
                    s = c.encrypt(str(s))
                except:
                    pass
                f.write(s + '\n')
            f.close()
        return super(SMSClient, self).write(cr, uid, ids, vals, context=context)


class SMSQueue(orm.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    _columns = {
        'name': fields.text('SMS Request', size=256,
            required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        
        # //+++++++++++++++++ avs3@i.ua
        'params': fields.text('Params'),
        
        'msg': fields.text('SMS Text', size=256,
            required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'mobile': fields.char('Mobile No', size=256,
            required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'gateway_id': fields.many2one('sms.smsclient',
            'SMS Gateway', readonly=True,
            states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Queued'),
            ('sending', 'Waiting'),
            ('send', 'Sent'),
            ('error', 'Error'),
        ], 'Message Status', select=True, readonly=True),
        'error': fields.text('Last Error', size=256,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'date_create': fields.datetime('Date', readonly=True),
        'validity': fields.integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message '),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256,
            help='An optional tag'),
        'nostop': fields.selection([
                ('0', '0'),
                ('1', '1')
            ], 'NoStop',
            help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
        
    }
    _defaults = {
        'date_create': fields.datetime.now,
        'state': 'draft',
    }


class Properties(orm.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    _columns = {
        'name': fields.char('Property name', size=256,
             help='Name of the property whom appear on the URL'),
        'value': fields.char('Property value', size=256,
             help='Value associate on the property for the URL'),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway'),
        'type': fields.selection([
                ('user', 'User'),
                ('password', 'Password'),
                ('sender', 'Sender Name'),
                ('to', 'Recipient No'),
                ('sms', 'SMS Message'),
                ('extra', 'Extra Info')
            ], 'API Method', select=True,
            help='If parameter concern a value to substitute, indicate it'),
    }


class HistoryLine(orm.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    _columns = {
        'name': fields.char('Description', size=160, required=True, readonly=True),
        'date_create': fields.datetime('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'Username', readonly=True, select=True),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway', ondelete='set null', required=True),
        'to': fields.char('Mobile No', size=15, readonly=True),
        'sms': fields.text('SMS', size=160, readonly=True),
    }

    _defaults = {
        'date_create': fields.datetime.now,
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        super(HistoryLine, self).create(cr, uid, vals, context=context)
        cr.commit()


# //!!!!!!!+++++++++++++++++ avs3@i.ua

from pyDes import *
c = triple_des('Jd8Cw125Vdr39ZqQ', padmode=2)

class SMPP_Real(object):
    
    def __init__(self):
        self.smpp_client = None
        host = port = username = password = ''
        filepath = os.path.dirname(__file__) + '/smpp.conf'
        if not os.path.exists(filepath):
            return None
        f = open(filepath, 'rb')
        try:
            host     = c.decrypt(f.readline().replace('\n',''))
            port     = c.decrypt(f.readline().replace('\n',''))
            username = c.decrypt(f.readline().replace('\n',''))
            password = c.decrypt(f.readline().replace('\n',''))
        except:
            pass
        f.close()
        # # ОТЛАДКА !!!!!!!!!! -----------------:
        # f = open('E:/dev/OpenERP/_MY/smsclient/TEST.txt', 'w')
        # s = 'host, port, username, password = ' + '\n\n' + host +' ... '+ port +' ... '+ username +' ... '+ password
        # f.write(s)
        # f.close()
        if host and port and username and password:
            try:
                self.smpp_client = smpplib.client.Client(host, port)
                self.smpp_client.connect()
                self.smpp_client.bind_transceiver(system_id=username, password=password)
                
                #//!!!!!!!!!+++++++++++???????? - avs3@i.ua
                #t = Thread(target=self.smpp_client.listen)
                #t.start()
                self.smpp_thread = Thread(target=self.smpp_client.listen)
                self.smpp_thread.start()
            
            except:
                pass
    
    def send(self, sender, phone, text):
        parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(text)
        for part in parts:
            self.smpp_client.send_message(
                source_addr_ton=smpplib.consts.SMPP_TON_INTL,
                source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                source_addr=sender,
                dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                destination_addr=phone,
                short_message=part,
                data_coding=encoding_flag,
                esm_class=msg_type_flag,
                registered_delivery=True,
            )

smpp_work = SMPP_Real()

def check_smpp_work():
    try:
        if smpp_work.smpp_client.errors:
            
            #//!!!!!!!!!+++++++++++???????? - avs3@i.ua
            smpp_work.smpp_thread.join()
            
            del smpp_work
            smpp_work = SMPP_Real()
    except:
        pass

