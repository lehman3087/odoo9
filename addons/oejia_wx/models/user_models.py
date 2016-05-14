# coding=utf-8

from openerp import models, fields, api
from ..controllers import client
from openerp.http import request
from ..controllers import utils


class wx_user(models.Model):
    _name = 'wx.user'
    _description = u'微信用户'
    #_order = 
    _inherits = {
         'res.partner':"member_id",
    }

    city = fields.Char(u'城市', )
    country = fields.Char(u'国家', )
    group_id = fields.Selection('_get_groups', string=u'所属组', default='0')
    headimgurl = fields.Char(u'头像', )
    nickname = fields.Char(u'昵称', )
    openid = fields.Char(u'用户标志', )
    province = fields.Char(u'省份', )
    sex = fields.Selection([(1,u'男'),(2,u'女')], string=u'性别', )
    subscribe = fields.Boolean(u'关注状态', )
    subscribe_time = fields.Char(u'关注时间', )
    member_id=fields.Many2one(
        'res.partner',
        string='Member',
        required=True,
        ondelete='cascade')

    headimg= fields.Html(compute='_get_headimg', string=u'头像')

    #_defaults = {
    #}

    @api.model
    def sync(self):
        next_openid = 'init'
        c_total = 0
        c_flag = 0
        g_flag = True
        objs = self.env['wx.user.group'].search([])
        group_list = [ e.group_id for e in objs]
        while next_openid:
            if next_openid=='init':next_openid = None
            followers_dict= client.wxclient.get_followers(next_openid)
            c_total = followers_dict['total']
            m_count = followers_dict['count']
            next_openid = followers_dict['next_openid']
            print 'get %s users'%m_count
            if next_openid:
                m_openids = followers_dict['data']['openid']
                for openid in m_openids:
                    c_flag +=1
                    print 'total %s users, now sync the %srd %s .'%(c_total, c_flag, openid)
                    rs = self.search( [('openid', '=', openid)] )
                    if rs.exists():
                        info = client.wxclient.get_user_info(openid)
                        info['group_id'] = str(info['groupid'])
                        if g_flag and info['group_id'] not in group_list:
                            self.env['wx.user.group'].sync()
                            g_flag = False
                        rs.write(info)
                    else:
                        info = client.wxclient.get_user_info(openid)
                        info['group_id'] = str(info['groupid'])
                        if g_flag and info['group_id'] not in group_list:
                            self.env['wx.user.group'].sync()
                            g_flag = False
                        # print info
                        self.create({
                            'member_id':self.env['res.partner'](dict({'member_id':self.env['res.partner'].create({'display_name':info['nickname'],'name':info['nickname']}).id},**info))
                        })
                        # self.create(info)

        print 'total:',c_total

    @api.multi
    def updateWxMember(self,phone):
        openid=utils.get_openid()
        print openid+'|'+phone
        rs = self.sudo().search([('openid', '=', openid)])
        if len(rs)>0:
            print phone
            rs.sudo().write({'name':phone,'mobile':phone})

    # @api.multi
    # def updateWxMember1(self):
    #     #openid=request.session['openid']
    #     rs = self.sudo().search( [('openid', '=', 'oplFas86MrbetIA2vBzIV08Ryqhk')] )
    #     print len(rs)
    #     if len(rs)>0:
    #         rs.sudo().write({'mobile':'123'})

    @api.multi
    def hasbinded(self):
        openid=request.session['openid']
        print openid
        rs = self.search( [('openid', '=', openid)])
        print rs.member_id.name
        if rs.member_id.mobile==False:
            return 0
        else:
            return rs


    @api.one
    def createWxMember(self,info):
        self.create({'member_id':self.env['res.partner'].create({'name':'1111'}).id}.join(info))

    @api.one
    def _get_headimg(self):
        self.headimg= '<img src=%s width="100px" height="100px" />'%self.headimgurl
        
    #@api.one
    def _get_groups(self):
        Group = self.env['wx.user.group']
        objs = Group.search([])
        return [(str(e.group_id), e.group_name) for e in objs]


class wx_user_group(models.Model):
    _name = 'wx.user.group'
    _description = u'微信用户组'
    #_order = 
    #_inherit = []

    count = fields.Integer(u'用户数', )
    group_id = fields.Integer(u'组编号', )
    group_name = fields.Char(u'组名', )
    user_ids = fields.One2many('wx.user', 'group_id', u'用户', )

    #_defaults = {
    #}
    
    @api.model
    def sync(self):
        groups =  client.wxclient.get_groups()
        for group in groups['groups']:
            rs = self.search( [('group_id', '=', group['id']) ] )
            if rs.exists():
                rs.write({
                             'group_name': group['name'],
                             'count': group['count'],
                             })
            else:
                self.create({
                             'group_id': str(group['id']),
                             'group_name': group['name'],
                             'count': group['count'],
                             })
            
