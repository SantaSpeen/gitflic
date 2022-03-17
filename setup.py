#!python3
import os
import shutil
import sys

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

packages = ['gitflic']

requires = ['requests']

# 'setup.py publish' shortcut.
if 'publish' in sys.argv:
    # Only if packages == 1
    for dir in ("./dist", f"{packages[0]}.egg-info"):
        if os.path.isdir(dir):
            shutil.rmtree(dir)
    os.system('python3 -m build')
    os.system('python3 -m twine upload --repository testpypi dist/*')
    os.system('python3 -m twine upload --repository pypi dist/*')
    sys.exit(0)

about = {}
with open(os.path.join(here, 'gitflic', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'gitflic': 'gitflic'},
    include_package_data=True,
    install_requires=requires,
    license=about['__license__'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Documentation': 'https://anixart.readthedocs.io/',
        'Source': 'https://github.com/SantaSpeen/anixart',
    },
    python_requires=">=3.7",
)