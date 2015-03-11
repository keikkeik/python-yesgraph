"""
Python wrapper for the YesGraph API.
"""
from setuptools import setup


dependencies = ['requests']

setup(
    name='yesgraph',
    version='0.1.0',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
)
