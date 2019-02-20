from setuptools import setup, find_packages
setup(
    name='hass_server',
    version='0.0.1',
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask==1.0.2',
        'requests==2.20.0',
        'psycopg2==2.7.4',
        'Flask-Cors==3.0.6',
        'apscheduler==3.5.1',
        'SQLAlchemy==1.2.0',
        'flask_sqlalchemy',
	    'kafka==1.3.5',
    	'azure-storage-file',
        'lxml',

	    'pymongo==3.7.1',
	    'azure==4.0.0',
        'python-ldap',
	'pyyaml',
	'ConfigParser'

    ],

    classifiers=[
        'Environment :: Web Environment'
           ]
)



