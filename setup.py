from setuptools import setup, find_packages

setup(
    name='mydb-cli',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['history_manager'],
    install_requires=[
        'click==8.1.7',
        'mysql-connector-python==8.0.33',
        'tabulate==0.9.0',
        'pandas==2.0.3',
        'reportlab==4.0.4',
        'streamlit==1.29.0',
        'plotly==5.18.0',
        'networkx==3.2.1',
        'google-generativeai==0.3.2'
    ],
    entry_points='''
        [console_scripts]
        mydb-cli=main:cli
    ''',
)