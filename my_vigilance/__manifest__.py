# -*- coding: utf-8 -*-
{
	'name': 'Vigilance',
	'version': '12.0.1.0.0',
	'summary': 'Vigilance',
	'category': 'Tools',
	'author': 'Dexciss Technologies Pvt Ltd(@ RGupta)',
	'maintainer': 'dexciss Techno Solutions',
	'company': 'dexciss Techno Solutions',
	'website': 'https://www.dexciss.com',
	'depends': ['base','mail'],
	'data': [
		'security/ir.model.access.csv',
		'security/security.xml',
        'wizard/reason_wizard.xml',
        'views/my_vigilance.xml',
	],
	'images': [],
	'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}