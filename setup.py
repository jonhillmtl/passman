from distutils.core import setup

setup(name='passman',
    version='0.1',
    description='',
    author='Jon Hill',
    author_email='jon@jonhill.ca',
    url='',
    packages = ['passman'],
    license='MIT',

    install_requires=[
        'cryptography',
        'termcolor',
        'str2bool',
        'pyperclip'
    ],

    entry_points={
        'console_scripts': [
            'passman = passman:main'
        ]
    }
)
