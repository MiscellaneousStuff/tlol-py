# MIT License
# 
# Copyright (c) 2021 MiscellaneousStuff
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module setuptools script."""
from setuptools import setup

description = """TLoL-py - League of Legends Deep Learning Library

TLoL-py is the Python component of the TLoL League of
Legends deep learning library. It provides a set of utility methods and classes
to deal with League of Legends game playing, deep learning datasets and provides
a library to build a deep learning agent which can play League of Legends.
Read the README at https://github.com/MiscellaneousStuff/tlol-py for more information.
"""

setup(
    name='tlol',
    version='1.0.0',
    description='TLoL-py League of Legends deep learning library',
    long_description=description,
    long_description_content_type="text/markdown",
    author='MiscellaneousStuff',
    author_email='raokosan@gmail.com',
    license='MIT License',
    keywords=[
        'League of Legends',
        'Machine Learning',
        'Reinforcement Learning',
        'Supervised Learning',
        'TLoL',
        'Dataset Generation',
        'Data Scraping'
    ],
    url='https://github.com/MiscellaneousStuff/tlol-py',
    packages=[
        'tlol',
        'tlol.bin',
        'tlol.datasets',
        'tlol.replays',
        'tlol.stats'
    ],
    install_requires=[
        'absl-py',
        'requests',
        'psutil'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)
