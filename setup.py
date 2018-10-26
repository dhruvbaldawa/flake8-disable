#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = [
    'pytest',
    'pytest-cov==2.5.1',
    # TODO: put package test requirements here
]

setup(
    name='flake8-disable',
    version='0.1.0',
    description="Helper to disable all the current flake8 violations in a project",
    long_description=readme + '\n\n' + history,
    author="Dhruv Baldawa",
    author_email='dhruv@dhruvb.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',

        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='flake8_disable',
    packages=find_packages(include=['flake8_disable']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/dhruvbaldawa/flake8_disable',
    zip_safe=False,
    entry_points={
        'console_scripts': [
                'flake8-disable = flake8_disable.main:main',
        ],
    },
)
