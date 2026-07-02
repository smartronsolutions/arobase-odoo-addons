{
    'name': 'My Vehicles Portal',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Display vehicles linked to portal users in their portal.',
    'depends': ['base', 'portal', 'website', 'fleet'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/my_vehicles_portal/static/src/js/vehicle_portal.js',
            '/my_vehicles_portal/static/src/css/portal_vehicles.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
