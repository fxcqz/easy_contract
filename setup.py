from setuptools import setup
from codes import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='easy_contract',
    version='0.1.0',
    description='Easy contract-based programming',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # TODO upload to github before pypi
    #url='',
    author='Matt Rawcliffe',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        # TODO check these
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='contract programming',
    py_modules=['easy_contract', 'test_contract'],
)
