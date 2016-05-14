# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.exceptions import AccessError, UserError
# class jewelry(models.Model):
#     _name = 'jewelry.jewelry'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


# class JewelryProduct(models.Model):
#     """ Products available to order. A product is linked to a specific vendor. """
#     _name = 'jewelry.product'
#     _inherit =['website_sale.product.template']
#     _description = 'jewelry product'
#
#     name = fields.Char('Product', required=True)
#     description = fields.Text('Description')
#     percentage=fields.Char('成色')
#     remarks =fields.Text("备注")
#     huohao=fields.Char("货号")
#     process_cost=fields.Char("加工费")
#     hand=fields.Char("手寸")
#     store_weight=fields.Char("石重")
#     side_store_weight=fields.Char("副石")
#     brand=fields.Many2one('brand',string="品牌",ondelete="cascade")
#
#
#
#
# class brand(models.Model):
#     _name = "brand"
#
#     name=fields.Char("品牌名")
#     company=fields.Many2one("res.partner",'Vendor')
#     brand_ids=fields.One2many("jewelry.product","brand")



