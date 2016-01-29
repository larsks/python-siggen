from setuptools import setup, find_packages

with open('requirements.txt') as fd:
    requires = fd.readlines()

setup(name='siggen',
      author='Lars Kellogg-Stedman',
      author_email='lars@oddbit.com',
      url='https://github.com/larsks/siggen',
      version='0.1',
      packages=find_packages(),
      install_requires=requires,
      entry_points={'console_scripts': ['siggen = siggen.main:main']})
