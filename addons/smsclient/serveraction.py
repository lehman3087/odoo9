# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
import time
import logging

_logger = logging.getLogger('smsclient')

class ServerAction(orm.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    _columns = {
        'sms_server': fields.many2one('sms.smsclient', 'SMS Server',
            help='Select the SMS Gateway configuration to use with this action'),
    }

    def run(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        act_ids = []
        for action in self.browse(cr, uid, ids, context=context):
            obj_pool = self.pool.get(action.model_id.model)
	    
	    #//+++++++++++++ Fix Error "Run MyCurrentTimeSheet"
            #obj = obj_pool.browse(cr, uid, context['active_id'], context=context)
	    obj = obj_pool.browse(cr, uid, context['uid'], context=context)
	    
            cxt = {
                'context': context,
                'object': obj,
                'time': time,
                'cr': cr,
                'pool': self.pool,
                'uid': uid
            }
            expr = eval(str(action.condition), cxt)
            if not expr:
                continue
            if action.state == 'sms':
                _logger.info('Send SMS')
                sms_pool = self.pool.get('sms.smsclient')
                mobile = str(action.mobile)
                to = None
                try:
                    cxt.update({'gateway': action.sms_server})
                    if mobile:
                        to = eval(action.mobile, cxt)
                    else:
                        _logger.error('Mobile number not specified !')

                    text = eval(action.sms, cxt)
                    #TODO: Fix it, this can't be working
#                    vals = {
#                        'gateway': action.sms_server.id,
#                        'mobile_to': to,
#                    }
#                    sms_id = sms_pool.create(cr, uid, vals, context=context)
#                    sms = sms_pool.browse(cr, uid, sms_id, context=context)
#                    if sms_pool._send_message(cr, uid, sms, context=context) == True:
#                        _logger.info('SMS successfully send to : %s' % (to))
#                    else:
#                        _logger.error('Failed to send SMS to : %s' % (to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
            else:
                act_ids.append(action.id)

        if act_ids:
            return super(ServerAction, self).run(cr, uid, act_ids, context=context)
        return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
