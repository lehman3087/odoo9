# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError
from openerp.tools import random_str
import requests
import json
import urllib
import urllib2

# class logistics(models.Model):
#     _name = 'logistics.logistics'
#
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


# class routes(models.Model):
#     _name = 'logistics.routes'
#
#     name = fields.Char()
#     car = fields.Many2one(comodel_name='fleet.vehicle.model')
#     # orgin = fields.One2many('res.partner.address', 'partner_id', 'Contacts')
#     #des_city=fields.Char(related='f.city',string='City',store=True)
#     #des_county=fields.Char(related="address.country_id", string='County',store=True)
#     # des_longitude=fields.Float()
#     # des_latitude=fields.Float()
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100




class package(models.Model):
    _name = 'logistics.package'

    # orgin = fields.Many2one(comodel_name='res.partner.address')
    # car = fields.Many2one(comodel_name='fleet.vehicle.model')
    # comprise=fields.One2many("logistics.comprise")
    phone=fields.Char()
    receiver_id=fields.Many2one('res.partner', string="Receiver")

    enter_id= fields.Many2one('res.partner', 'enter', required=True, readonly=True,
                              states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.uid)
    date = fields.Date('Date', required=True, readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=fields.Date.context_today)
    state = fields.Selection([('draft', 'To Submit'),
                              ('submit', 'Submitted'),
                              ('done', 'Paid'),
                              ('cancelled', 'Cancelled')],
                             'Status', readonly=True, select=True, default='draft')

    package_line_ids = fields.One2many('logistics.package.line', 'package_id', 'Package_items',
                                     ondelete="cascade", readonly=True, copy=True,
                                     states={'draft': [('readonly', False)], False: [('readonly', False)]})
    verycode=fields.Char(string="verycode",size=5)

    evaluate=fields.Text()
    evaluate_level=fields.Selection([('l0', 'cha'),
                              ('l1', 'yiban'),
                              ('l2', 'hao'),
                              ('l3', 'henhao')],
                             'Evaluate_level', readonly=True, select=True, default='l1')


    images1=fields.Binary("images1", attachment=True,
        help="")
    images2=fields.Binary("images2", attachment=True,
        help="")
    images3=fields.Binary("images3", attachment=True,
        help="")
    images4=fields.Binary("images4", attachment=True,
        help="")
    images5=fields.Binary("images5", attachment=True,
        help="")
    images6=fields.Binary("images6", attachment=True,
        help="")
    images7=fields.Binary("images7", attachment=True,
        help="")
    images8=fields.Binary("images8", attachment=True,
        help="")
    images9=fields.Binary("images9", attachment=True,
        help="")
    images10=fields.Binary("images10", attachment=True,
        help="")

    # @api.one
    # def _compute_code(self):
    #     self.verycode=random_str(5)

    @api.multi
    def sendm(self):
        if any(expense.state != 'draft' for expense in self):
            raise UserError(_("You can only submit draft expenses!"))
        for package in self:
            verycode=random_str.random_str(5)
            url="http://106.ihuyi.cn/webservice/sms.php?method=Submit"
            rowdata={
            "account": "cf_lehman",
            "password": "1513141981",
            "mobile": package.phone,
            "content":"您的验证码是："+verycode+"。请不要把验证码泄露给其他人。",
            }
            data=urllib.urlencode(rowdata)
            req=urllib2.Request(url,data)
            resp = urllib2.urlopen(req)
            # resp = json.load(urllib2.urlopen(req))
            package.write({'state': 'submit','verycode':verycode})
            # if(resp.SubmitResult.code=='2'):
            #     package.write({'state': 'submit','verycode':verycode})


    @api.multi
    def confirm(self):
        """
        confirm one or more order line, update order status and create new cashmove
        """
        if self.state != 'done':
            # values = {
            #     'user_id': self.user_id.id,
            #     'description': self.product_id.name,
            #     'order_id': self.id,
            #     'state': 'order',
            #     'date': self.date,
            # }
            # self.env['lunch.cashmove'].create(values)
            self.state = 'done'

    @api.multi
    def cancel(self):
        """
        cancel one or more order.line, update order status and unlink existing cashmoves
        """
        self.state = 'cancelled'
        # self.cashmove.unlink()

    @api.multi
    def check_code(self, code):
        if self.state != 'done':
            for recode in self:
                if recode.verycode != code:
                    return False
                self.state = 'done'

    @api.multi
    def hasUnreceived(self,uid):
        print uid
        rst=self.search(['&',('receiver_id','=',uid),('state','=','submit')])
        print len(rst)
        if len(rst)>0:
            return rst[0]
        else:
            return 0


class package_line(models.Model):
    _name = 'logistics.package.line'
    _description = 'package detail line'

    serial=fields.Char()
    poster_id=fields.Many2one(
        'res.partner',
        string='Postman',
        context={'default_is_postman': True},
        domain=[('is_postman', '=', True)]
    )
    company_id = fields.Many2one('res.company', related='poster_id.company_id', store=True)
    package_id = fields.Many2one('logistics.package', 'Items', ondelete='cascade', required=True)


class res_partner(models.Model):

    """"""

    _inherit = 'res.partner'

    is_postman = fields.Boolean(
        string='Is Postman?'
    )
