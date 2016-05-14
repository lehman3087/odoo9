# coding=utf-8
from .. import client
from ..routes import robot
from openerp.http import request



@robot.click
def onclick(message, session):
    openid = message.source
    request.session['openid']=openid
    _name, action_id = message.key.split(',')
    action_id = int(action_id)
    if _name:
        action = request.env()[_name].sudo().browse(action_id)
        return action.get_wx_reply()
