from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def assign_tax_repartition(self):

        for move in self:

            for line in move.line_ids:

                if line.tax_repartition_line_id:
                    continue

                # MPN Account
                tax_line = self.env['account.tax']
                if line.account_id.name == 'HUTANG PPN KELUARAN':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPN Keluaran')
                    ])[0].invoice_repartition_line_ids[1].id
                elif line.account_id.name == 'PPN MASUKAN':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPN Masukan')
                    ])[0].payment_repartition_line_ids[1].id
                elif line.account_id.name == 'PPH 23 DIBAYAR DIMUKA':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPh 23 Masukan')
                    ])[0].payment_repartition_line_ids[1].id
                elif line.account_id.name == 'PPH 25 DIBAYAR DIMUKA':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPh 25 Masukan')
                    ])[0].payment_repartition_line_ids[1].id
                elif line.account_id.name == 'HUTANG PAJAK PPH 29':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPh 29 Keluaran')
                    ])[0].invoice_repartition_line_ids[1].id

                # DSi Account
                elif line.account_id.name == 'Hutang Pajak - Pajak Keluaran':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPN Keluaran')
                    ])[0].invoice_repartition_line_ids[1].id
                elif line.account_id.name == 'PPh 23 Dibayar Di Muka':
                    tax_line = self.env['account.tax'].search([
                        ('name', '=', 'PPh 23 Dibayar Di Muka')
                    ])[0].payment_repartition_line_ids[1].id

                if tax_line:
                    line.tax_repartition_line_id = tax_line

    def remove_tax_repartition(self):

        for move in self:
            for line in move.line_ids:
                line.tax_repartition_line_id = False

    def assign_pph_23(self):
        pph_23 = self.env['account.tax'].search([('name', '=', 'PPh 23')])[0]

        for move in self:

            for line in move.invoice_line_ids:

                taxes = []
                for tax in line.tax_ids:
                    taxes.append(tax.name)

                if 'PPh 23' not in taxes:
                    line.with_context(bypass=True).write({'tax_ids': [(4, pph_23.id, 0)]})
