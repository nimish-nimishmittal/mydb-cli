from setuptools import setup, find_packages

setup(
    name="mydb-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'mysql-connector-python',
        'tabulate',
        'streamlit'
    ],
    entry_points={
        'console_scripts': [
            'mydb-cli=main:cli',
        ],
    },
)