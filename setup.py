from setuptools import find_packages, setup


setup(
    name='pygolf',
    version='0.0.1',
    description='Golf card game',
    long_description='Golf card game',
    author='Jake Bell',
    author_email='sigterm01@gmail.com',
    packages=find_packages(),
    install_requires=[
        'clint',
    ],
    extras_require={
        'dev': [
            'bpython',
            'flake8',
        ]
    },
    entry_points={
        'console_scripts': [
            'pygolf=pygolf.cli:main',
        ],
    },
)
