from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='courseraresearchexports',
    version='0.0.1',
    description='Command line tool for convenient access to '
    'Coursera Research Data Exports.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='coursera',
    url='https://github.com/coursera/courseraresearchexports',
    author='Timothy Lee',
    author_email='tlee@coursera.org',
    license='Apache',
    entry_points={
        'console_scripts': [
            'courseraresearchexports = courseraresearchexports.main:main',
        ],
    },
    packages=['courseraresearchexports', 'courseraresearchexports.commands'],
    install_requires=[
        'courseraoauth2client>=0.0.1',
        'requests>=2.7.0',
        'docker-py>=1.2.3',
        'tqdm>=4.8.4',
        'tabulate>=0.7.5',
        'python-dateutil'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    include_package_data=True,
    zip_safe=False
)
