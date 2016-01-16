from setuptools import setup

VERSION = '2.1.0'

if __name__ == '__main__':
    setup(
        name='nd2reader',
        packages=['nd2reader', 'nd2reader.model', 'nd2reader.driver', 'nd2reader.parser', 'nd2reader.common'],
        install_requires=[
            'numpy>=1.6.2, <2.0',
            'six>=1.4, <2.0',
            'xmltodict>=0.9.2, <1.0'
        ],
        version=VERSION,
        description='A tool for reading ND2 files produced by NIS Elements',
        author='Jim Rybarski',
        author_email='jim@rybarski.com',
        url='https://github.com/jimrybarski/nd2reader',
        download_url='https://github.com/jimrybarski/nd2reader/tarball/%s' % VERSION,
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
