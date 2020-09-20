from distutils.core import setup
setup(
  name = 'pygnmi',
  packages = ['pygnmi'],
  version = '0.1.0',
  license='bsd-3-clause',
  description = 'This repository contains pure Python implementation of the gNMI client to interact with the network functions.',
  author = 'Anton Karneliuk',
  author_email = 'anton@karneliuk.com',
  url = 'https://github.com/akarneliuk/pygnmi',
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['gnmi', 'automation', 'grpc'], 
  install_requires=[
          'asyncio',
          'grpcio',
          'grpcio-tools'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Network Engineers',
    'Intended Audience :: Engineers',   
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD 3-clause "New" license',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)