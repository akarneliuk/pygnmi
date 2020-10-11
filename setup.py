from distutils.core import setup

with open('README.rst') as fh:
    long_description = fh.read()

setup(
  name = 'pygnmi',
  packages = ['pygnmi', 'pygnmi.spec', 'pygnmi.artefacts'],
  version = '0.1.8',
  license='bsd-3-clause',
  description = 'This repository contains pure Python implementation of the gNMI client to interact with the network functions.',
  long_description = long_description,
  long_description_content_type = 'text/x-rst',
  author = 'Anton Karneliuk',
  author_email = 'anton@karneliuk.com',
  url = 'https://github.com/akarneliuk/pygnmi',
  download_url = 'https://github.com/akarneliuk/pygnmi/archive/v0.1.8.tar.gz',
  keywords = ['gnmi', 'automation', 'grpc', 'network'], 
  install_requires=[
          'grpcio',
          'grpcio-tools'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Telecommunications Industry',
    'Operating System :: OS Independent',
    'Topic :: System :: Networking',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)