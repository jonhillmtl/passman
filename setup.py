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

    # TODO JHILL: this isn't working
    dependency_links = [
        'git+ssh://git@gitlab.com/f2m-data-science/lambda_package.git',
        'git+ssh://git@gitlab.com/f2m-data-science/lambda_verify.git',
    ],

    entry_points={
        'console_scripts': [
            'passman = passman:main'
        ]
    }
)
