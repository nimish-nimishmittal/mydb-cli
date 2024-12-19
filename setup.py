from setuptools import setup, find_packages

setup(
    name='mydb-cli',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'mysql.connector',
        'prettytable',
        'tabulate',
        'json',
        'os',
        'datetime',
        'csv',
        'history_manager',
        'typing',
        'reportlab'
    ],
    entry_points='''
        [console_scripts]
        mydb-cli=main:cli
    ''',
)