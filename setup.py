from setuptools import setup

setup(name='taskflaskapi',
        version = '0.0.4',
        description = 'tasks app api in flask',
        author = 'voytek',
        author_email = 'meh@meh.com',
        packages = ['taskflask'],
        install_requires = [
            'Flask',
        ],
        license = 'BSD',
        url = 'https://github.com/voytekio/flask_task',
)


