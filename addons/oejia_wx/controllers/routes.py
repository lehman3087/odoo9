# coding=utf-8
import logging
import os
import utils

from werobot.robot import BaseRoBot
from werobot.parser import parse_user_msg
from werobot.reply import create_reply
from werobot.logger import enable_pretty_logging
import werkzeug
from werobot.session.filestorage import FileStorage
import json
import openerp
from openerp import http
from openerp.http import request
import client

_logger = logging.getLogger(__name__)
data_dir = openerp.tools.config['data_dir']
session_storage = FileStorage(filename=os.path.join(data_dir, 'werobot_session') )

def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')


class WeRoBot(BaseRoBot):
    pass

robot = WeRoBot(token='K5Dtswptelehman', enable_session=True, logger=_logger, session_storage=session_storage)
enable_pretty_logging(robot.logger)
    
class WxController(http.Controller):

    ERROR_PAGE_TEMPLATE = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf8" />
            <title>Error: {{e.status}}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd;
                    padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error: {{e.status}}</h1>
            <p>微信机器人不可以通过 GET 方式直接进行访问。</p>
            <p>想要使用本机器人，请在微信后台中将 URL 设置为 <pre>{{request.url}}</pre> 并将 Token 值设置正确。</p>
        </body>
    </html>
    """
    token=''
    def __init__(self):
        import client
        Param = request.env()['ir.config_parameter']
        robot.config["TOKEN"] = Param.get_param('wx_token') or 'K5Dtswptelehman'
        self.token=Param.get_param('wx_token') or 'K5Dtswptelehman'
        client.wxclient.appid = Param.get_param('wx_appid')  or 'wxd548cbdc841c83e9'
        client.wxclient.appsecret = Param.get_param('wx_AppSecret')  or '47aa81e196e4f73c25d4a0816c8eb159'

        #print(openid+'fuck') 不会每次欧答应



    # @http.route('/wx/', auth='public',type='http',methods=['GET'],csrf=False)
    # def index(self, **kw):
    #     return "Hello, world"

    @http.route('/wx_handler', type='http', auth="none", methods=['GET'],csrf=False)
    def echo(self, **kw):
        if not robot.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)

        return request.params.get("echostr")

    @http.route('/wx/bind', type='http', auth="none", methods=['GET'])
    def echo2(self, **kw):
        getOpenId = request.params.get('getOpenId') or None
        openid=request.session.get('openid','')

        if(getOpenId==None and openid==''):
            url = utils.Wxauh()
            return werkzeug.utils.redirect(url)

        openid=utils.get_openid()
        request.session['openid']=openid
        # return openid

        return http.request.render('oejia_wx.bind', {

        })


    @http.route('/wx_handler', type='http', auth="none", methods=['POST'],csrf=False)
    def handle(self, **kwargs):
        if not robot.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)

        body = request.httprequest.data
        message = parse_user_msg(body)
        robot.logger.info("Receive message %s" % message)
        reply = robot.get_reply(message)
        if not reply:
            robot.logger.warning("No handler responded message %s"
                                % message)
            return ''
        #response.content_type = 'application/xml'
        return create_reply(reply, message=message)

    @http.route('/wx_veryfy', type='http', auth="none", methods=['POST'],csrf=False)
    def veryfy(self, veryfy,phone):
        veryfy_session=''
        try:
            veryfy_session=request.session[phone]
            print veryfy+'|'+veryfy_session
        except Exception:
            return json.dumps({'code':0})
        # print veryfy+'|'+veryfy_session
        if veryfy==veryfy_session:
            request.env['wx.user'].updateWxMember(phone)
            return json.dumps({'code':1})


    # @http.route('/test1', type='http', auth="none")
    # def veryfy1(self,**kv):
    #     request.env['wx.user'].updateWxMember1()
    #     return '1'

    @http.route('/wx/test11', type='http', auth="none", methods=['GET'],csrf=False)
    def t11(self,**kv):
        return utils.get_openid()