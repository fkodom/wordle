import os
from distutils.core import setup
from subprocess import getoutput
from typing import Dict, List

import setuptools


def get_version_tag() -> str:
    try:
        version = os.environ["WORDLE_VERSION"]
    except KeyError:
        version = getoutput("git describe --tags --abbrev=0")

    return version


extras_require: Dict[str, List[str]] = {
    "app": ["straemlit"],
    "benchmark": ["tqdm"],
    "test": ["black", "flake8", "isort", "pytest", "pytest-cov"],
}
all_require = set(r for requirements in extras_require.values() for r in requirements)


setup(
    name="wordle",
    version=get_version_tag(),
    author="Frank Odom",
    author_email="frank.odom.iii@gmail.com",
    url="https://github.com/fkodom/wordle",
    packages=setuptools.find_packages(exclude=["tests"]),
    description="A minimal Python library for playing and solving 'Wordle' problems",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["colorama"],
    extras_require=extras_require,
    entry_points={"console_scripts": ["play-wordle=wordle.game:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
