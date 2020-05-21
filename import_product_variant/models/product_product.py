# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api
from odoo.exceptions import UserError



import logging

LOGGER = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    vendor_num = fields.Char(string="Vendor Number", required=False, )
    categ_name = fields.Char(string="Category Name", required=False, )
    vendor_color = fields.Char(string="Vendor Color", required=False, )
    categ_num = fields.Char(string="Category Number", required=False, )
    sale_price =fields.Float("Sales Price2")
    has_seller = fields.Boolean('Has seller' , compute='_get_seller',)
    # seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', string='Vendors',compute='_get_seller',store=True, help="Define vendor pricelists.")
    # variant_seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id',compute='_onchange_vendor_num',store=True,)

    un_edit = fields.Boolean(string="UN Edit",compute='_compute_un_edit' )

    def _compute_un_edit(self):
        for rec in self:
            sale = self.env['sale.order.line'].search([('product_id','=',rec.id)])
            pur = self.env['purchase.order.line'].search([('product_id','=',rec.id)])
            pos = self.env['pos.order.line'].search([('product_id','=',rec.id)])
            inv = self.env['account.invoice.line'].search([('product_id','=',rec.id)])
            if sale or pur or inv or pos:
                self.un_edit = True
            else:
                self.un_edit = False


    @api.depends('sale_price')
    def _compute_product_price_extra(self):
        for product in self:
            product.price_extra = product.sale_price

    @api.multi
    @api.depends('vendor_num')
    def _get_seller(self):
        print(" ** has_seller **")
        for rec in self:
            seller_id = []
            temp = rec.product_tmpl_id
            if rec.vendor_num:
                vendor = self.env['res.partner'].search([('ref', '=', rec.vendor_num)], limit=1)
                if vendor:
                    seller_obj = self.env['product.supplierinfo']
                    seller = self.env['product.supplierinfo'].create({
                        'product_tmpl_id': temp.id,
                        'product_id': rec.id,
                        'name': vendor.id,
                    })
                    rec.seller_ids= [(6,0,seller.ids)]
                    rec.has_seller =True
                else:raise UserError('This Number not belong to any vendor')
            else:rec.has_seller=False


    def _assin_seller(self):
        seller_id = []
        temp = self.product_tmpl_id
        if self.vendor_num and temp:
            vendor = self.env['res.partner'].search([('ref', '=', self.vendor_num)], limit=1)
            if vendor:
                seller_obj = self.env['product.supplierinfo']
                seller = seller_obj.search([('product_id', '=', self.id), ('name', '=', vendor.id)], limit=1)
                if not seller:
                    seller = self.env['product.supplierinfo'].create({
                        'product_tmpl_id': temp.id,
                        'product_id': self.id,
                        'name': vendor.id,
                    })
                    seller_id= [(6,0,seller.ids)]
                else:
                    seller_id= [(6,0,seller.ids)]
            else:return False

        if seller_id:
            return seller_id
        else: return False


    @api.multi
    @api.depends('vendor_num')
    def _onchange_vendor_num(self):
        for rec in self:
            try:

                seller = rec._assin_seller()
                print('seller ==',seller)
                rec.variant_seller_ids = seller
            except:
                return True

    @api.one
    @api.depends('variant_seller_ids')
    def _onchange_seller(self):
        for rec in self:
            if rec.variant_seller_ids:
                rec.seller_ids = rec.variant_seller_ids

    @api.multi
    def write(self,vals):
        if 'vendor_num' in vals:
            seller = self._assin_seller()
            self.product_tmpl_id.variant_seller_ids = seller
            self.product_tmpl_id.seller_ids = seller
            self.variant_seller_ids = seller
            self.seller_ids = seller

        super(ProductProduct, self).write(vals)
        return True


    # @api.model
    # def create(self,vals):
    #
    #     new_record = super(ProductProduct, self).create(vals)
    #     self._onchange_vendor_num()
    #     return new_record

    # @api.one
    # @api.depends('vendor_num')
    # def _compute_get_seller(self):
    #     for rec in self:
    #         if rec.vendor_num:
    #             vendor = self.env['res.partner'].search([('ref','=',rec.vendor_num)],limit=1)
    #             if vendor:
    #                 seller_obj = self.env['product.supplierinfo']
    #                 seller = seller_obj.search([('product_id','=',rec.id),('name','=',vendor.id)],limit=1)
    #                 if not seller:
    #                     seller = self.env['product.supplierinfo'].create({
    #                                                     'product_id':rec.id,
    #                                                     'product_tmpl_id':rec.product_tmpl_id.id,
    #                                                     'name':vendor.id,
    #                 })
    #                 rec.seller_ids = [(6,0,seller.ids)]
    #
    #                 # if not rec.seller_ids:
    #                 #     rec.write({'seller_ids':[(6,0,seller.ids)]})
    #             else: rec.seller_ids = False
    #         else:
    #             rec.seller_ids = False

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vendor_num = fields.Char(string="Vendor Number", required=False, )
    vendor_color = fields.Char(string="Vendor Color", required=False, )
    categ_num = fields.Char(string="Category Number", required=False, )
    sale_price =fields.Float("Sales Price2")
    # custom_attribute_lines = fields.Many2many(comodel_name='product.template.attribute.line', string='Product Attributes')
    # attribute_line_ids = fields.One2many()
    variant_price = fields.Float(string="Sale Price", compute='compute_variant_price' )

    @api.multi
    def create_variant_ids(self):

        return True

    @api.depends('product_variant_ids','product_variant_ids.sale_price')
    def compute_variant_price(self):
        for rec in self:
            if len(rec.product_variant_ids) > 1:
                rec.variant_price = 0
            elif len(rec.product_variant_ids) == 1:
                rec.variant_price = rec.product_variant_ids[0].sale_price

    @api.model
    def clear_list_price(self):
        self._cr.execute("update product_template set list_price = 0")
        # products = self.search([])
        # for p in products:
        #     p.write({'list_price': 0.0})


    # def assign_attribute_lines(self):
    #         self.write({'attribute_line_ids' : self.custom_attribute_lines})
    #
    #         if self.custom_attribute_lines and not self.attribute_line_ids:
    #             ids =self.custom_attribute_lines.ids
    #             self.write({'attribute_line_ids': [(6,0,ids)]})

class productAtt(models.Model):
    _inherit = 'product.template.attribute.line'

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade', required=False, index=True)

class product_att_val(models.Model):
    _inherit = 'product.template.attribute.value'
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template',
        required=False, ondelete='cascade', index=True)


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"
    product_uom = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        related='product_id.uom_po_id',
        help="This comes from the product form.")
