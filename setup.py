from setuptools import setup

setup(name='sc2bank',
      version='0.1',
      description='Validate SC2Bank XML document signatures.',
      url='https://githubl.com/winny-/sc2bank',
      author='Winston Weinert',
      author_email='sc2bank@fastmail.fm',
      license='ISC/BSD 3 clause',
      packages=['sc2bank'],
      zip_safe=False,
      extras_requires=['PyQt5'])
