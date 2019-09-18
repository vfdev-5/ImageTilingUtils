import os
from codecs import open as codecs_open
import re
from setuptools import setup, find_packages


def read(*names):
    with codecs_open(os.path.join(os.path.dirname(__file__), *names),
                     encoding="utf-8") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


long_description = read("README.md")
version = find_version('tiling', '__init__.py')


setup(
    name="tiling",
    version=version,
    description=u"Minimalistic set of image reader agnostic tools to easily iterate over large images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="vfdev-5",
    author_email="vfdev.5@gmail.com",
    url="https://github.com/vfdev-5/ImageTilingUtils",
    packages=find_packages(exclude=['tests', 'examples']),
    install_requires=[
        'six',
    ],
    license='MIT',
    test_suite="tests",
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov'
        ]
    }
)
