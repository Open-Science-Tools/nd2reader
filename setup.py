from setuptools import setup

VERSION = '3.0.3'

if __name__ == '__main__':
    setup(
        name='nd2reader',
        packages=['nd2reader'],
        install_requires=[
            'numpy>=1.6.2',
            'six>=1.4',
            'xmltodict>=0.9.2',
            'pims>=0.3.0'
        ],
        version=VERSION,
        description='A tool for reading ND2 files produced by NIS Elements',
        author='Ruben Verweij',
        author_email='verweij@physics.leidenuniv.nl',
        url='https://github.com/rbnvrw/nd2reader',
        download_url='https://github.com/rbnvrw/nd2reader/tarball/%s' % VERSION,
        keywords=['nd2', 'nikon', 'microscopy', 'NIS Elements'],
        classifiers=['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Science/Research',
                     'License :: Freely Distributable',
                     'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.4',
                     'Topic :: Scientific/Engineering',
                     ]
    )
