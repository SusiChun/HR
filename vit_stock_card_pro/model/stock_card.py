from odoo import api, fields, models, _
from datetime import date
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

SC_STATES =[('draft','Draft'),('open','Open'), ('done','Done')]


class stock_card(models.Model):
    _name 		= "vit.stock_card"
    _rec_name 	= "product_id"

    @api.multi
    def unlink(self):
        for stock in self:
            if stock.state != 'draft' :
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus draft'))
        return super(stock_card, self).unlink()

    ref 			= fields.Char("Number", default="/")
    date_start		= fields.Date("Date Start", required=True, default=lambda *a : time.strftime("%Y-%m-%d") )
    date_end		= fields.Date("Date End", required=True, default=lambda *a : time.strftime("%Y-%m-%d") )
    location_id		= fields.Many2one('stock.location', 'Location', required=True)
    product_id		= fields.Many2one('product.product', 'Product', required=True)
    breakdown_sn	= fields.Boolean("Per Serial Number?")
    lot_id			= fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    expired_date	= fields.Datetime(string="Expired Date", type="date", related='lot_id.life_date')
    line_ids		= fields.One2many('vit.stock_card_line','stock_card_id','Details', ondelete="cascade")
    state			= fields.Selection(SC_STATES,'Status',readonly=True,required=True, default="draft")
    user_id			= fields.Many2one('res.users', 'Created', default=lambda self: self.env.user)


    @api.multi
    def action_calculate(self):
        location = self.location_id.id
        # obj_loc = self.env['stock.location'].search([('company_id', '=', self.location_id.company_id.id),('warehouse_id', '!=', False)])
        # mylist_loc = []
        # mylist_loc_int = []
        # mylist_loc.append(str(location))
        # mylist_loc_int.append(location)
        # for x in obj_loc:
        #     if x.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.location_id.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        #     elif x.location_id.location_id.location_id.location_id.location_id.location_id.location_id.location_id.location_id.location_id.id == location:
        #         mylist_loc.append(str(x.id))
        #         mylist_loc_int.append(x.id)
        # # import pdb;pdb.set_trace()
        # obj1 = ','.join(x for x in mylist_loc)

        locations = self.env['stock.location'].search([('id', 'child_of', [location])])
        ids_location = tuple(locations.ids)
        mylist_loc_int = ids_location
        obj1 = str(ids_location).replace(',)',')')

        # kosongkan stock_card_line
        # cari stock move product_id dan location_id, start_date to end_date
        # insert into stock_card_line
        # jika keluar dari location (source_id) maka isi ke qty_out
        # jika masu ke location (dest_id) maka isi ke qty_in
        # hitung qty_balance = qty_start + qty_in - qty_out
        # start balance dihitung dari total qty stock move sebelum start_date
        cr=self.env.cr

        stock_move = self.env['stock.move']
        stock_card_line = self.env['vit.stock_card_line']
        product = self.env['product.product']

        cr.execute("delete from vit_stock_card_line where stock_card_id=%s" % self.id)

        qty_start = 0.0
        qty_balance = 0.0
        qty_in = 0.0
        qty_out = 0.0
        product_uom = False
        lot_id =False

        ##############################################################
        ### cari stock moves milik lot_id atau milik product_id
        ##############################################################
        if self.breakdown_sn:
            lot_id = self.lot_id
            sql2 = "select move_id from stock_quant_move_rel qm " \
                "join stock_quant q on qm.quant_id = q.id where q.lot_id = %s" % (lot_id.id)
        else:
            sql2 = "select move_id from stock_quant_move_rel qm " \
                "join stock_quant q on qm.quant_id = q.id where q.product_id = %s" % ( self.product_id.id)

        cr.execute(sql2)
        res = cr.fetchall()
        move_ids = []
        move_ids_int = []
        if res and res[0]!= None:
            for move in res:
                move_ids.append(str(move[0]))
                move_ids_int.append(move[0])

        if move_ids:
            move_string = ','.join(x for x in move_ids)
            # move_string = "(" + "".join( [str(x) for x in move_ids] ) + ")"
            ##############################################################
            ## beginning balance in
            ##############################################################
            sql = "select sum(product_uom_qty) from stock_move where product_id=%s " \
                  "and date < '%s 24:00:00' and location_dest_id in %s " \
                  "and id in (%s) "\
                  "and state='done'" %(
                self.product_id.id, self.date_start, obj1, move_string)
            cr.execute(sql)
            res = cr.fetchone()
            if res and res[0]!= None:
                qty_start = res[0]

            ##############################################################
            ## beginning balance out
            ##############################################################
            sql = "select sum(product_uom_qty) from stock_move " \
                      "where product_id=%s " \
                      "and date < '%s 24:00:00' " \
                      "and location_id in %s " \
                      "and id in (%s) "\
                      "and state='done'" %(
                self.product_id.id, self.date_start, obj1, move_string )
            cr.execute(sql)
            res = cr.fetchone()
            if res and res[0]!= None:
                qty_start = qty_start - res[0]

        ## product uom
        prod = self.product_id
        product_uom = prod.uom_id

        data = {
            "stock_card_id"	: self.id,
            "date"			: self.date_start,# tanggal start sesuai start header
            "qty_start"		: False,
            "qty_in"		: False,
            "qty_out"		: False,
            "qty_balance"	: qty_start,
            "product_uom_id": product_uom.id,
            # tambah name beginning balance
            "name"          : "Beginning Balance"
        }
        stock_card_line.create(data)

        ##############################################################
        ## mutasi
        ##############################################################
        # fgh = stock_move.search(['|',('location_dest_id','in',mylist_loc_int),('location_id','in',mylist_loc_int),('product_id','=', self.product_id.id),('date','>=', self.date_start),('date','<=', self.date_end),('state','=','done'),('id','in', move_ids_int)], order='date asc')
        sm_ids = stock_move.search(['|',
            ('location_dest_id','in',mylist_loc_int),
            ('location_id','in',mylist_loc_int),
            ('product_id', 	'=' , self.product_id.id),
            ('date', 		'>=', self.date_start),
            ('date', 		'<=', self.date_end),
            ('state',		'=',  'done'),
            ('id',			'in', move_ids_int)

        ], order='date asc')


        for sm in sm_ids:
            qty_in = 0.0
            qty_out = 0.0

            #uom conversion factor
            if product_uom.id != sm.product_uom.id:
                factor =  product_uom.factor / sm.product_uom.factor
            else:
                factor = 1.0

            if sm.location_dest_id.id in mylist_loc_int:	#incoming, dest = location
                qty_in = sm.product_uom_qty  * factor
            elif sm.location_id.id in mylist_loc_int:		#outgoing, source = location
                qty_out = sm.product_uom_qty * factor

            qty_balance = qty_start + qty_in - qty_out

            name = sm.name if sm.name!=prod.display_name else ""
            partner_name = sm.partner_id.name if sm.partner_id else ""
            notes = sm.picking_id.note or ""
            po_no = sm.group_id.name if sm.group_id else ""
            origin = sm.origin or ""
            finish_product = ""

            # if "MO" in origin:
            #     mrp = self.env['mrp.production']
            #     mo_id = mrp.search([("name","=",origin)],limit=1)
            #     # mo = mrp.browse(mo_id)
            #     # di odoo 10 ga ada batch_number
            #     # finish_product = "%s:%s"%(mo[0].product_id.name,mo[0].batch_number) if mo else ""
            #     finish_product = "%s"%(mo_id.product_id.name) if mo_id else ""


            final_name = name
            name += ' ' + finish_product if finish_product else ''
            name += ' ' + partner_name if partner_name else ''
            name += ' ' + notes if notes else ''
            name += ' ' + origin if origin else ''

            data = {
                "stock_card_id"	: self.id,
                "move_id"		: sm.id,
                "picking_id"	: sm.picking_id.id,
                "lot_id"	    : self.find_lot_id(cr, sm.id ),
                "date"			: sm.date,
                "qty_start"		: qty_start,
                "qty_in"		: qty_in,
                "qty_out"		: qty_out,
                "qty_balance"	: qty_balance,
                "product_uom_id": product_uom.id,
                "name"			: final_name,
            }
            stock_card_line.create(data)
            qty_start = qty_balance
        return

    def action_draft(self):
        #set to "draft" state
        return self.write({'state':SC_STATES[0][0]})

    def action_confirm(self):
        #set to "confirmed" state
        return self.write({'state':SC_STATES[1][0]})

    def action_done(self):
        #set to "done" state
        return self.write({'state':SC_STATES[2][0]})

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('vit.stock_card')
        new_id = super(stock_card, self).create(vals)
        return new_id

    def find_lot_id(self, cr, move_id):

        lot_id = False

        sql = "select distinct(q.lot_id) from stock_quant_move_rel rel " \
                "join stock_quant q on rel.quant_id=q.id " \
                "where move_id=%s"

        cr.execute(sql, (move_id,))
        res = cr.fetchall()

        if res and res[0]!= None:
            lot_id = res[0]

        return lot_id


    def cron_action_calculate(self):
        stock_card_exist = self.search([('state','in',('done','open'))])
        for card in stock_card_exist :
            date_now = date.today()
            card.update({'date_end':date_now})
            card.action_calculate()
            info = 'Stock Card '+str(card.ref)+' Updated..'
            print info

class stock_card_line(models.Model):
    _name 			= "vit.stock_card_line"

    name			= fields.Char("Description")
    stock_card_id	= fields.Many2one('vit.stock_card_id', 'Stock Card')
    move_id			= fields.Many2one('stock.move', 'Stock Move')
    picking_id		= fields.Many2one('stock.picking', 'Picking')
    lot_id		= fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    date			= fields.Date("Date")
    qty_start		= fields.Float("Start")
    qty_in			= fields.Float("Qty In")
    qty_out			= fields.Float("Qty Out")
    qty_balance		= fields.Float("Balance")
    product_uom_id	= fields.Many2one('product.uom', 'UoM')