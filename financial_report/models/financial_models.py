# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from openerp.exceptions import UserError


# class pembayaran_line(models.Model):
#     _name = "report.type"

#     name = fields.Char(string='Name')
#     type_report = fields.Char(string='Type Report')


class financial_report(models.Model):
	_inherit = "account.financial.html.report.line"
	# _description = "Financial Report Line"

	type_report = fields.Selection([
        ('accounts', 'Accounts'),
        ('group_id', 'Accounts Group'),
        ('account_type', 'Account Type'),
        ('account_report', 'Report Value'),
        ], 'Line Type', default='accounts')
	# custom_children_ids = fields.One2many('res.partner', 'custom_parent_id', string='Children')
	# account_ids = fields.One2many('account.account', 'account_id' string='Accounts')
	# account_report_ids = fields.One2many('account.financial.html.report.line', 'parent_id', string='Report Value')
	# account_type_ids = fields.One2many('account.account.type', string='Account Types')
	# group_ids = fields.One2many('account.group', string='Accounts Group ')
	account_ids = fields.Many2many('account.account', 'account_account_financial_report', 'report_line_id', 'account_id')
	account_report_ids = fields.Many2many('account.financial.html.report.line', 'account_account_financial_html_report_value', 'report_value', 'children_ids', 'Report Value')
	account_type_ids = fields.Many2many('account.account.type', 'account_account_financial_html_report_type_ids', 'report_id', 'account_type_id', 'Account Types')
	group_ids = fields.Many2many('account.group','account_account_financial_html_report_group', 'report_group_id', 'group_id', 'Accounts Group ')
	detail_report = fields.Selection([
        ("detail", "Detail"),
        ("total", "Total")
    ], default='total', string="Line")
	formula = fields.Selection([
		('*1', 'Positif'),
		('*-1', 'Negatif'),
		], 'Formula', default='*1'
		)
	jreport = fields.Selection([
        ("detail", "Detail"),
        ("total", "Total")
    ], default='detail', string="Detail/Total")
	generate_value = fields.Boolean(default = False)

	def cek_query(self):
		#======================== isi Value Report ========================
		print('Report_Value')
		self._cr.execute('''SELECT a.parent_id, a.id
							from account_financial_html_report_line as a
							where a.parent_id notnull''')
		rec_report = self._cr.fetchall()
		print(rec_report)		
		for a in rec_report:
			self._cr.execute('''INSERT INTO public.account_account_financial_html_report_value(report_value, children_ids) 
								VALUES (%s,%s)
								ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_value_children_ids_key DO NOTHING''' %(a[0],a[1]))
		
		self._cr.execute("""UPDATE account_financial_html_report_line
							SET type_report = 'account_report'
							where formulas not like '%sum.%'""")

		
		print('Group_id')
		self._cr.execute("""SELECT a.id, b.id as group_id
							from account_financial_html_report_line as a
							inner join account_group as b on a.name = b.name
							where a.formulas like '%sum.%' and a.domain like '%account_id.group_id%'""")
		rec_group_id = self._cr.fetchall()
		print(rec_group_id)

		for a in rec_group_id:
			self._cr.execute('''INSERT INTO public.account_account_financial_html_report_group(report_group_id, group_id) 
								VALUES (%s,%s)
								ON CONFLICT ON CONSTRAINT account_account_financial_html_rep_report_group_id_group_id_key DO NOTHING''' %(a[0],a[1]))
		
		self._cr.execute("""UPDATE account_financial_html_report_line
							SET type_report = 'group_id'
							where formulas like '%sum.%' and domain like '%account_id.group_id%'""")
		
		
		print('Account Type')
		self._cr.execute("""SELECT a.id, a.domain, a.formulas,  a.groupby, a.name, a.parent_id
							from account_financial_html_report_line as a
							where a.formulas like '%sum.%' and a.domain like '%account_id.user_type_id%'""")
		rec_account_type = self._cr.fetchall()	
		print(rec_account_type)
		
		for a in rec_account_type:
			to_s =str(a[1])
			value_name = to_s.find("'account_id.user_type_id.name'")
			if value_name != -1:
				x = to_s.find("'in', ")
				if x != -1:
					to_s2 = to_s[x:]
					y = to_s2.find(")]")
					hasil = to_s[x+5:x+y]
					# import ipdb; ipdb.set_trace()
					s = hasil[2:len(hasil) -1].split(", ")
					for recs in s:
						self._cr.execute("""SELECT a.id
											from account_account_type as a
											where a.name like '%s'""" %(str(recs[1:len(recs)-1])))
						rec_hasil = self._cr.fetchall()
						for recs in rec_hasil:
							print(to_s + " : " + str(recs[0]))
							self._cr.execute('''INSERT INTO public.account_account_financial_html_report_type_ids(report_id, account_type_id) 
												VALUES (%s,%s)
												ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs[0])))
				else:
					x = to_s.find("'=', ")
					to_s2 = to_s[x:]
					y = to_s2.find(")]")
					hasil = to_s[x+5:x+y]
					self._cr.execute("""SELECT a.id
										from account_account_type as a
										where a.name like '%s'""" %(str(hasil[1:len(hasil)-1])))
					rec_hasil = self._cr.fetchall()
					for recs in rec_hasil:
						print(to_s + " : " + str(recs[0]))
						self._cr.execute('''INSERT INTO public.account_account_financial_html_report_type_ids(report_id, account_type_id) 
											VALUES (%s,%s)
											ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs[0])))
			else:
				x = to_s.find("'in', ")
				if x != -1:
					to_s2 = to_s[x:]
					y = to_s2.find(")]")
					hasil = to_s[x+5:x+y]
					# import ipdb; ipdb.set_trace()
					s = hasil[2:len(hasil) -1].split(", ")
					for recs in s:
						if recs.isdigit():
							print(to_s + " : " + str(recs))
							self._cr.execute('''INSERT INTO public.account_account_financial_html_report_type_ids(report_id, account_type_id) 
												VALUES (%s,%s)
												ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs)))
						else:
							print(to_s + " : " + str(recs[1:len(recs)-1]))
							self._cr.execute('''INSERT INTO public.account_account_financial_html_report_type_ids(report_id, account_type_id) 
												VALUES (%s,%s)
												ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs[1:len(recs)-1])))
				else:
					to_s =str(a[1])
					x = to_s.find("'=', ")
					to_s2 = to_s[x:]
					cek_data = to_s.find("'not in',")
					if cek_data != -1:
						y = to_s2.find(")]")
					else:
						y = to_s2.find("), ")
					hasil = to_s[x+5:x+y]
					if hasil.isdigit():					
						print(to_s + " : " + str(hasil))
						self._cr.execute('''INSERT INTO public.account_account_financial_html_report_type_ids(report_id, account_type_id) 
											VALUES (%s,%s)
											ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],hasil))
					else:
						if hasil.find("'") == -1:
							self._cr.execute("""SELECT a.id
												from account_account_type as a
												where a.type like '%s'""" %(str(hasil)))					
						else:
							self._cr.execute("""SELECT a.id
												from account_account_type as a
												where a.type like '%s'""" %(str(hasil[1:len(hasil)-1])))						
						rec_hasil = self._cr.fetchall()
						for recs in rec_hasil:
							print(to_s + " : " + str(recs[0]))
							self._cr.execute('''INSERT INTO public.account_account_financial_html_report_type_ids(report_id, account_type_id) 
												VALUES (%s,%s)
												ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs[0])))
		# import ipdb; ipdb.set_trace()		


		print('Account')
		self._cr.execute("""SELECT a.formulas, a.domain, a.groupby, a.name, a.parent_id, a.id
							from account_financial_html_report_line as a
							where a.formulas like '%sum.%' and a.domain like '%account_id.code%'""")
		rec_account = self._cr.fetchall()
		print(rec_account)

		for a in rec_account:
			to_s =str(a[1])
			value_name = to_s.find("'account_id.code', 'in'")
			if value_name != -1:
				x = to_s.find("'in', ")
				if x != -1:
					to_s2 = to_s[x:]
					y = to_s2.find(")]")
					hasil = to_s[x+5:x+y]
					# import ipdb; ipdb.set_trace()
					s = hasil[2:len(hasil) -1].split(", ")
					for recs in s:
						if recs.isdigit():
							print(to_s + " : " + str(recs))
							self._cr.execute('''INSERT INTO public.account_account_financial_report(report_line_id, account_id) 
												VALUES (%s,%s)
												ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs)))
						else:
							print(to_s + " : " + str(recs[1:len(recs)-1]))
							self._cr.execute('''INSERT INTO public.account_account_financial_report(report_line_id, account_id) 
												VALUES (%s,%s)
												ON CONFLICT ON CONSTRAINT account_account_financial_html_re_report_id_account_type_id_key DO NOTHING''' %(a[0],str(recs[1:len(recs)-1])))

		
		# for a in rec_account:
		# 	self._cr.execute('''INSERT INTO public.account_account_financial_report(report_line_id, account_id) VALUES (%s,%s)''' %(a[0],a[1]))

		# self._cr.execute("""UPDATE account_financial_html_report_line
		# 					SET type_report = 'accounts'
		# 					where a.formulas like '%sum.%' and a.domain like '%account_id.code%'""")
		print('done')
		# insert = self._cr.execute('''INSERT INTO public.account_account_financial_html_report_value( report_value, children_ids) VALUES (91,98);''')

	
	@api.onchange('name')
	def set_code_name(self):
		name_tmp = self.name
		if name_tmp != False:
			name_tmp = name_tmp.replace(" ", "_")
		self.update({'code' : name_tmp})
		# self.code = name_tmp

	
	
	@api.onchange('account_ids', 'account_type_ids', 'group_ids', 'account_report_ids')
	def _add_value(self):
		value={}
		for rec in self:
			if rec.type_report == "accounts":
				value = self._set_account_id()
			elif rec.type_report == "account_type":
				value = self._set_account_type()
			elif rec.type_report == "group_id":
				value = self._set_group_id()
			elif rec.type_report == "account_report":
				value = self._set_account_report()
				if rec.jreport =='detail':
					self.update({'children_ids' : self.account_report_ids})					
			if value:		
				self.update({'formulas' : value['formulas'],
							'domain' : value['domain'],
							'groupby' : value['groupby']})
				# self.formulas = value['formulas'] 
				# self.domain = value['domain']
				# self.groupby = value['groupby']


	def _set_account_id(self):
		formulas = ''
		domain = ''
		groupby = ''
		for rec in self:
			if rec.type_report == "accounts":
				domain_rec = ""
				# [('account_id.code', 'in', ['611.01.002','761.01.006','761.01.007'])]
				for rec2 in rec.account_ids:
					if domain_rec == "":
						domain_rec = str(rec2.code)
					else:
						domain_rec = domain_rec + "', '" + str(rec2.code)
				formulas = "balance = sum.balance"  + str(rec.formula)
				domain = "[('account_id.code', 'in', ['" + domain_rec + "'])]"
				groupby = "account_id"

		values = {'formulas' : formulas,
				 'domain' : domain,
				 'groupby' : groupby,
				 }
		return values

	
	def _set_account_type(self):
		formulas = ''
		domain = ''
		groupby = ''
		for rec in self:
			if rec.type_report == "account_type":
				domain_rec = ""
				# [('account_id.user_type_id.name', 'in', ['Pendapatan Sewa','Pendapatan Sewa Bank Lain'])]
				for rec2 in rec.account_type_ids:
					if domain_rec == "":
						domain_rec = (str(rec2.id.origin) if rec2.id.origin else rec2.id)
					else:
						domain_rec = domain_rec + "', '" + (str(rec2.id.origin) if rec2.id.origin else rec2.id)
				formulas = "balance = sum.balance" + str(rec.formula)
				domain = "[('account_id.user_type_id', 'in', ['" + domain_rec + "'])]"
				groupby = "account_id"

		values = {'formulas' : formulas,
				 'domain' : domain,
				 'groupby' : groupby,
				 }
		return values

	
	def _set_group_id(self):
		formulas = ''
		domain = ''
		groupby = ''
		for rec in self:
			if rec.type_report == "group_id":
				domain_rec = ""
				# [('account_id.group_id.name', '=', 'Biaya Pegawai')]
				for rec2 in rec.group_ids:
					if domain_rec == "":
						domain_rec = (str(rec2.id.origin) if rec2.id.origin else rec2.id)
					else:
						domain_rec = domain_rec + "', '" + (str(rec2.id.origin) if rec2.id.origin else rec2.id)
				formulas = "balance = sum.balance" + str(rec.formula)
				domain = "[('account_id.group_id.id', 'in', ['" + domain_rec + "'])]"
				groupby = "account_id"

		values = {'formulas' : formulas,
				 'domain' : domain,
				 'groupby' : groupby,
				 }
		return values

	
	def _set_account_report(self):
		formulas = ''
		domain = ''
		groupby = ''
		formulas_rec = ""
		for rec in self:
			if rec.type_report == "account_report":
				for rec2 in rec.account_report_ids:
					if formulas_rec == "":
						formulas_rec = str(rec2.code) + ".balance"
					else:
						formulas_rec = formulas_rec + " + " + str(rec2.code) + ".balance"
				formulas = "balance = " + formulas_rec + str(rec.formula)
				domain = ""
				groupby = ""

		values = {'formulas' : formulas,
				 'domain' : domain,
				 'groupby' : groupby,
				 }
		return values

	@api.model
	def generate_report(self):
		report_vals = self.env['account.financial.html.report.line'].search_read([('type_report', '!=', False)])
		for b in report_vals:        		
			if b['type_report'] == 'accounts':
				self._loop_account_ids(b, b['id'], b['level'] + 1)
			if b['type_report'] == 'group_id':
				self._loop_group_ids(b, b['id'], b['level'] + 1)
			if b['type_report'] == 'account_type':
				self._loop_account_type_ids(b, b['id'], b['level'] + 1)
			if b['type_report'] == 'account_report':
				self._loop_account_report_ids(b, b['id'], b['level'] + 1)

	def _loop_account_ids(self,line_id,parent_ids,level):
		for a in line_id['account_ids']:
			self._write_vals(a, parent_ids, level)

	def _loop_group_ids(self,line_id,parent_ids,level):
		for a in line_id['group_ids']:
			self._write_vals(a,parent_ids, level)

	def _loop_account_type_ids(self,line_id,parent_ids,level):
		for a in line_id['account_type_ids']:
			self._write_vals(a,parent_ids, level)

	def _loop_account_report_ids(self,line_id,parent_ids,level):
		for a in line_id['account_report_ids']:
			self._write_vals(a,parent_ids, level)

	def _write_vals(self, line_id, parent_ids, level):
		vals = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
		value =  {
		            # 'parent_id': parent_ids,
		            'level': level,
		            # 'sequence': self.date,
		          }
		write_value = vals.update(value)
		return write_value

















#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

# from odoo import models, fields, api, _
# from openerp.exceptions import UserError


# class financial_models(models.Model):
# 	_inherit = "account.financial.html.report.line"
# 	_description = "Financial Report Line"
# 	# account_ids = fields.Many2many('account.account', 'account_account_financial_html_report_line', 'report_line_id', 'account_id', 'Accounts')
# 	# account_report_id = fields.Many2many('account.financial.html.report.line', 'account_account_financial_report_reporting','parent_id','parent_id', 'Report Value')
# 	# account_report_id = fields.One2many('account.financial.html.report.line', 'parent_id')
# 	# children_ids = fields.One2many('account.financial.html.report.line', 'parent_id', string='Children')

# 	type_report = fields.Selection([
#         ('accounts', 'Accounts'),
#         ('group_id', 'Accounts Group'),
#         ('account_type', 'Account Type'),
#         ('account_report', 'Report Value'),
#         ], 'Type', default='accounts')
# 	account_ids = fields.Many2many('account.account', 'account_account_financial_report', 'report_line_id', 'account_id', 'Accounts')
# 	account_report_ids = fields.Many2many('account.financial.html.report.line', 'account_account_financial_html_report_value', 'report_value', 'children_ids', 'Report Value')
# 	account_type_ids = fields.Many2many('account.account.type', 'account_account_financial_html_report_type', 'report_id', 'account_type_id', 'Account Types')
# 	group_ids = fields.Many2many('account.group','account_account_financial_html_report_group', 'report_group_id', 'group_id', 'Accounts Group ')
# 	formula = fields.Selection([
#         ('*1', 'Positif'),
#         ('*-1', 'Negatif'),
#     ], 'Formula', default='*1'
#     )
	
# 	@api.onchange('name')
# 	def set_code_name(self):
# 		name_tmp = self.name
# 		if name_tmp != False:
# 			name_tmp = name_tmp.replace(" ", "_")
# 		self.code = name_tmp

 #    def _set_accounts_domain(self):
 #    	domain_rec = ""
	# 	# [('account_id.code', 'in', ['611.01.002','761.01.006','761.01.007'])]
	# 	for rec2 in rec.account_ids:
	# 		if domain_rec == "":
	# 			rec.name=rec2.name
	# 			rec.code = rec2.name
	# 			domain_rec = str(rec2.code)
	# 		else:
	# 			domain_rec = domain_rec + "', '" + str(rec2.code)
	# 	rec.formulas = "balance = sum.balance"  + str(rec.formula)
	# 	rec.domain = "[('account_id.code', 'in', ['" + domain_rec + "'])]"
	# 	rec.groupby = "account_id"









	# # @api.model
	# @api.model
	# @api.onchange('formula','account_report_ids','account_type_ids','group_ids','type_report')
	# def set_formula(self):		
	# 	for rec in self:
	# 		if rec:	
	# 			kodeid = ""
	# 			try:
	# 				kodeid = rec.id.origin
	# 			except ValueError:
	# 				kodeid = ""
	# 				pass
	# 			formulas_rec = ""
	# 			if rec.type_report == "account_report":
	# 				for rec2 in rec.account_report_ids:
	# 					kodeid = ""
	# 					if rec.id.origin == False:							
	# 						kodeid = ""
	# 					else:
	# 						kodeid = rec.id.origin
	# 					rec2.parent_id = kodeid
	# 					rec2.code = rec2.name
	# 					rec2.level = int(rec.level) + 1
	# 					if formulas_rec == "":
	# 						formulas_rec = str(rec2.code) + ".balance"
	# 					else:
	# 						formulas_rec = formulas_rec + " + " + str(rec2.code) + ".balance"
	# 				rec.formulas = "balance = " + formulas_rec + str(rec.formula)
	# 				rec.domain = ""
	# 				rec.groupby = ""
	# 			elif rec.type_report == "account_type":
	# 				domain_rec = ""
	# 				# [('account_id.user_type_id.name', 'in', ['Pendapatan Sewa','Pendapatan Sewa Bank Lain'])]
	# 				for rec2 in rec.account_type_ids:
	# 					if domain_rec == "":
	# 						rec.name=rec2.name
	# 						rec.code = rec2.name
	# 						domain_rec = str(rec2.name)
	# 					else:
	# 						domain_rec = domain_rec + "', '" + str(rec2.name)
	# 					print("================account_type_ids===================")
	# 					print(rec2)
	# 					print("=============================================")

	# 				rec.formulas = "balance = sum.balance" + str(rec.formula)
	# 				rec.domain = "[('account_id.user_type_id.name', 'in', ['" + domain_rec + "'])]"
	# 				rec.groupby = "account_id"				
	# 			elif rec.type_report == "group_id":
	# 				domain_rec = ""
	# 				# [('account_id.group_id.name', '=', 'Biaya Pegawai')]
	# 				for rec2 in rec.group_ids:
	# 					if domain_rec == "":
	# 						rec.name=rec2.name
	# 						rec.code = rec2.name
	# 						domain_rec = str(rec2.name)
	# 					else:
	# 						domain_rec = domain_rec + "', '" + str(rec2.name)
	# 					print("================group_ids===================")
	# 					print(rec2)
	# 					print("=============================================")
	# 				rec.formulas = "balance = sum.balance" + str(rec.formula)
	# 				rec.domain = "[('account_id.group_id.name', 'in', ['" + domain_rec + "'])]"
	# 				rec.groupby = "account_id"				
	# 			elif rec.type_report == "accounts":
	# 				domain_rec = ""
	# 				# [('account_id.code', 'in', ['611.01.002','761.01.006','761.01.007'])]
	# 				for rec2 in rec.account_ids:
	# 					if domain_rec == "":
	# 						rec.name=rec2.name
	# 						rec.code = rec2.name
	# 						domain_rec = str(rec2.code)
	# 					else:
	# 						domain_rec = domain_rec + "', '" + str(rec2.code)
	# 					print("================account_ids===================")
	# 					print(rec2)
	# 					print("=============================================")
	# 				rec.formulas = "balance = sum.balance"  + str(rec.formula)
	# 				rec.domain = "[('account_id.code', 'in', ['" + domain_rec + "'])]"
	# 				rec.groupby = "account_id"					
	# 			elif rec.type_report == "":
	# 				rec.formulas = ""
	# 				rec.domain = ""
	# 				rec.groupby = ""