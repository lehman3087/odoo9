# -*- coding: utf-8 -*-

# import models
from openerp.http import request
import werkzeug
import client
from openerp import http

# def get_wx_reply_from_aciton(action):
#     _name = action._name
#     if _name==models.wx_action_act_text._name:
#         return action.content
#     elif _name==models.wx_action_act_article._name:
#         articles = action.article_ids
#         return ''
#     elif _name==models.wx_action_act_custom._name:
#         return ''

def isWeixinBrowser():
    wsgienv = request.httprequest.environ
    environ = request.httprequest.headers.environ
    user_agent=environ['HTTP_USER_AGENT']
    # print(user_agent)
    # print(user_agent.find('Mozilla/5.0'))
    if user_agent.find('icroMessenger')==-1:

        return False

    # return  wsgienv.get('HTTP_REFERER', False)

def get_openid():

    openid=request.session.get('openid','')

    if openid!='':
        return openid

    code = request.params.get("code", '')

    if code!='':
        print "getcode="
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (client.wxclient.appid, client.wxclient.appsecret, code)
        data = client.wxclient.get(url)
        openid = data.get("openid")
        return openid

    # if isWeixinBrowser()!=False:
    #     curUrl=getCurUrl()
    #     # print(curUrl)
    #     OAuthWeixin(curUrl)
def Wxauh():
    if isWeixinBrowser()!=False:
        curUrl=getCurUrl()
        print(curUrl)
        return OAuthWeixin(curUrl)


def getCurUrl():
    return  request.httprequest.url

def OAuthWeixin(callback):
    par={}
    param={}
    getOpenId = request.params.get('getOpenId') or None
    if(getOpenId==None):



        par['state']=123
        par['scope']='snsapi_base'
        par['response_type']='code'
        par['redirect_uri']=callback+'?getOpenId=1'
        par ['appid'] = client.wxclient.appid
        url='https://open.weixin.qq.com/connect/oauth2/authorize?'+werkzeug.url_encode(par)+'#wechat_redirect'
        #webrequest.redirect(url)
        print url+'fuck'
        return  url
        #werkzeug.utils.redirect(url)

        # http.redirect_with_hash(url,303)
        # http.local_redirect(url)
        print 'redirectend1'
    elif (request.params.get('state')!=''):
        print('get_stated')
        param['appid'] = client.wxclient.appid
        param['secret'] = client.wxclient.appsecret
        param['code']=request.params.get('code')
        # param['code'] = request.params.get('code')
        param['grant_type'] = 'authorization_code'
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' +werkzeug.url_encode(param)
        data1 = client.get(url)
        openid = data1.get("openid")
        print 'state_Get'+openid
        http.local_redirect(callback +'&openid=' +openid)



# def get_user_openid(appid,app_secret):
#     '''微网站获取用户openid'''
#     code = request.param.get("code", '')
#     url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (appid, app_secret, code)
#     data = method_get_api(url)
#     openid = data.get("openid")
#     return openid
