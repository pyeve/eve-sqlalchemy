import codecs
import os

from setuptools import find_packages, setup


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r', 'utf-8').read()


# Import the project's metadata
metadata = {}
exec(read('eve_sqlalchemy', '__about__.py'), metadata)

test_dependencies = [
    'mock',
    'pytest',
]

setup(
    name=metadata['__title__'],
    version=metadata['__version__'],
    description=(metadata['__summary__']),
    long_description=read('README.rst') + "\n\n" + read('CHANGES'),
    keywords='flask sqlalchemy rest',
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    url=metadata['__url__'],
    license=metadata['__license__'],
    platforms=['any'],
    packages=find_packages(),
    test_suite='eve_sqlalchemy.tests',
    install_requires=[
        'Eve<0.8',
        'Flask-SQLAlchemy>=2.4,<2.999',
        'SQLAlchemy>=1.3',
    ],
    tests_require=test_dependencies,
    extras_require={
        # This little hack allows us to reference our test dependencies within
        # tox.ini. For details see http://stackoverflow.com/a/41398850 .
        'test': test_dependencies,
    },
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
