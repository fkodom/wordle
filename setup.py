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
    "benchmark": ["matplotlib", "tqdm"],
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
    install_requires=["colorama", "gdown"],
    extras_require=extras_require,
    data_files=[("data", ["data/words.txt"])],
    entry_points={
        "console_scripts": [
            "play-wordle=wordle.game:main_wordle",
            "play-multi-wordle=wordle.game:main_multi_wordle",
            "play-dordle=wordle.game:main_dordle",
            "play-quordle=wordle.game:main_quordle",
            "play-octordle=wordle.game:main_octordle",
            "solve-wordle=wordle.solver:main_wordle",
            "solve-multi-wordle=wordle.solver:main_multi_wordle",
            "solve-dordle=wordle.solver:main_dordle",
            "solve-quordle=wordle.solver:main_quordle",
            "solve-octordle=wordle.solver:main_octordle",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
