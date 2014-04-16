from setuptools import setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='sc2bank',
    version='0.3',
    description='Validate SC2Bank XML document signatures.',
    long_description=long_description,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
    ],
    url='https://github.com/winny-/sc2bank',
    author='Winston Weinert',
    author_email='sc2bank@fastmail.fm',
    license='MIT / BSD 3-clause',
    packages=['sc2bank', 'sc2bank.test'],
    tests_require='mock',
    test_suite='sc2bank.test',
)
