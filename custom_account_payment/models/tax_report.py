from odoo import models


class GenericTaxReport(models.AbstractModel):
    _inherit = 'account.generic.tax.report'

    def _sql_cash_based_taxes(self):
        sql = """SELECT id, sum(base) AS base, sum(net) AS net FROM (
                    SELECT tax.id,
                    SUM("account_move_line".balance) AS base,
                    0.0 AS net
                    FROM account_move_line_account_tax_rel rel, account_tax tax, %s
                    WHERE (tax.tax_exigibility IN ('on_payment', 'on_payment_custom'))
                    AND (rel.account_move_line_id = "account_move_line".id)
                    AND (tax.id = rel.account_tax_id)
                    AND ("account_move_line".tax_exigible)
                    AND %s
                    GROUP BY tax.id
                    UNION
                    SELECT tax.id,
                    0.0 AS base,
                    SUM("account_move_line".balance) AS net
                    FROM account_tax tax, %s
                    WHERE (tax.tax_exigibility IN ('on_payment', 'on_payment_custom'))
                    AND "account_move_line".tax_line_id = tax.id
                    AND ("account_move_line".tax_exigible)
                    AND %s
                    GROUP BY tax.id) cash_based
                    GROUP BY id;"""
        return sql

