from setuptools import setup

setup(name='taskflaskapi',
        version = '0.1.2',
        description = 'tasks app with api in flask',
        author = 'Voytek Krudysz',
        author_email = 'voytek@voytek.io',
        packages = ['taskflask'],
        #package_dir={'taskflask': 'src'},
        #data_files=[('', ['src/four.vvv'])],
		install_requires=[
		#	'Flask',
			'python-dateutil',
		],
        license = 'BSD',
        url = 'https://github.com/voytekio/flask_task',
)
