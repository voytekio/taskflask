from setuptools import setup

setup(name='taskflaskapi',
        version = '0.1.10',
        description = 'tasks app with api in flask',
        author = 'Voytek Krudysz',
        author_email = 'voytek@voytek.io',
        package_dir={'taskflask': 'src'},
        packages = ['taskflask'],
        #data_files=[('', ['src/four.vvv'])],
        install_requires=[
        # 'Flask',
            'python-dateutil',
        ],
        # scripts = ['taskflask/taskcmd'], # actual name of the file
        entry_points = {
            'console_scripts': ['taskcmd=taskflask.cmdline:main'],
        },
        license = 'BSD',
        url = 'https://github.com/voytekio/taskflask',
)
