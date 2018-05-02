from setuptools import setup

setup(name='chatta',
      version='0.1',
      description='A small chat service for friends to talk',
      url='https://github.com/meritzio/chatta',
      author='Samuel Woodhead',
      author_email='sam@blueforge.xyz',
      license='MIT',
      packages=['chatta'],
      install_requires=[
        'pycryptodome',
        'future',
        ],
      zip_safe=False)

