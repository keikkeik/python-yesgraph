"""
Python wrapper for the YesGraph API.
"""
import re

from setuptools import setup

dependencies = ['requests', 'six']

version = ''
with open('yesgraph.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

setup(
    name='yesgraph',
    version=version,
    url='https://github.com/yesgraph/python-yesgraph',
    author='YesGraph',
    author_email='team@yesgraph.com',
    description='Python wrapper for the YesGraph API.',
    long_description=__doc__,
    py_modules=['yesgraph'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
)
