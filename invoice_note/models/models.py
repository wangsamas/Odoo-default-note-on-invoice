# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    inv_note = fields.Text(string='Default Terms and Conditions', translate=True)
	
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
	
    inv_note = fields.Text(related='company_id.inv_note', string="Terms & Conditions")
    use_inv_note= fields.Boolean(
        string='Default Invoice Terms & Conditions')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_pricelist_setting = ICPSudo.get_param('sale.sale_pricelist_setting')
        sale_portal_confirmation_options = ICPSudo.get_param('sale.sale_portal_confirmation_options', default='none')
        default_deposit_product_id = literal_eval(ICPSudo.get_param('sale.default_deposit_product_id', default='False'))
        if default_deposit_product_id and not self.env['product.product'].browse(default_deposit_product_id).exists():
            default_deposit_product_id = False
        res.update(
            auth_signup_uninvited='b2c' if ICPSudo.get_param('auth_signup.allow_uninvited', 'False').lower() == 'true' else 'b2b',
            use_sale_note=ICPSudo.get_param('sale.use_sale_note', default=False),
            use_inv_note=ICPSudo.get_param('sale.use_inv_note', default=False),
            auto_done_setting=ICPSudo.get_param('sale.auto_done_setting'),
            default_deposit_product_id=default_deposit_product_id,
            sale_show_tax=ICPSudo.get_param('sale.sale_show_tax', default='subtotal'),
            multi_sales_price=sale_pricelist_setting in ['percentage', 'formula'],
            multi_sales_price_method=sale_pricelist_setting in ['percentage', 'formula'] and sale_pricelist_setting or False,
            sale_pricelist_setting=sale_pricelist_setting,
            portal_confirmation=sale_portal_confirmation_options in ('pay', 'sign'),
            portal_confirmation_options=sale_portal_confirmation_options if sale_portal_confirmation_options in ('pay', 'sign') else False,
        )
        return res
	
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('auth_signup.allow_uninvited', repr(self.auth_signup_uninvited == 'b2c'))
        ICPSudo.set_param("sale.use_sale_note", self.use_sale_note)
        ICPSudo.set_param("sale.use_inv_note", self.use_inv_note)
        ICPSudo.set_param("sale.auto_done_setting", self.auto_done_setting)
        ICPSudo.set_param("sale.default_deposit_product_id", self.default_deposit_product_id.id)
        ICPSudo.set_param('sale.sale_pricelist_setting', self.sale_pricelist_setting)
        ICPSudo.set_param('sale.sale_show_tax', self.sale_show_tax)
        ICPSudo.set_param('sale.sale_portal_confirmation_options', self.portal_confirmation_options if self.portal_confirmation_options in ('pay', 'sign') else 'none')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
	
    def _default_comment(self):
        invoice_type = self.env.context.get('type', 'out_invoice')
        if invoice_type == 'out_invoice' and self.env['ir.config_parameter'].sudo().get_param('sale.use_inv_note'):
            return self.env.user.company_id.inv_note

    @api.onchange('partner_id', 'company_id')
    def _onchange_delivery_address(self):
        addr = self.partner_id.address_get(['delivery'])
        self.partner_shipping_id = addr and addr.get('delivery')
        if self.env.context.get('type', 'out_invoice') == 'out_invoice':
            company = self.company_id or self.env.user.company_id
            self.comment = company.with_context(lang=self.partner_id.lang).inv_note

			
