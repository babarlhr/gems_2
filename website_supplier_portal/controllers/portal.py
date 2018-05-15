# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from collections import OrderedDict
import logging
_logger = logging.getLogger(__name__)


class PortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['purchase_count'] = request.env['purchase.order'].sudo().search_count([
            '|', '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('partner_id', '=', partner.id),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ])
        return values

    @http.route(['/my/purchase', '/my/purchase/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_purchase_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        _logger.info("Move to Web Interface from Partal Interface")
        return request.redirect('/web')
        
        
        #values = self._prepare_portal_layout_values()
        #partner = request.env.user.partner_id
        #PurchaseOrder = request.env['purchase.order']

        #domain = [
            #'|', '|',
            #('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            #('partner_id', '=', partner.id),
            #('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        #]

        #archive_groups = self._get_archive_groups('purchase.order', domain)
        #if date_begin and date_end:
            #domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        #searchbar_sortings = {
            #'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            #'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            #'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        #}
        ## default sort by value
        #if not sortby:
            #sortby = 'date'
        #order = searchbar_sortings[sortby]['order']

        #searchbar_filters = {
            #'all': {'label': _('All'), 'domain': []},
            #'purchase': {'label': _('Purchase Order'), 'domain': []},
            #'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            #'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        #}
        ## default filter by value
        #if not filterby:
            #filterby = 'all'
        #domain += searchbar_filters[filterby]['domain']

        ## count for pager
        #purchase_count = PurchaseOrder.sudo().search_count(domain)
        ## make pager
        #pager = portal_pager(
            #url="/my/purchase",
            #url_args={'date_begin': date_begin, 'date_end': date_end},
            #total=purchase_count,
            #page=page,
            #step=self._items_per_page
        #)
        ## search the purchase orders to display, according to the pager data
        #orders = PurchaseOrder.sudo().search(
            #domain,
            #order=order,
            #limit=self._items_per_page,
            #offset=pager['offset']
        #)
        #request.session['my_purchases_history'] = orders.ids[:100]

        #values.update({
            #'date': date_begin,
            #'orders': orders,
            #'page_name': 'purchase',
            #'pager': pager,
            #'archive_groups': archive_groups,
            #'searchbar_sortings': searchbar_sortings,
            #'sortby': sortby,
            #'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            #'filterby': filterby,
            #'default_url': '/my/purchase',
        #})
        #return request.render("purchase.portal_my_purchase_orders", values)
