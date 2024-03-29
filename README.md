<div align="center">
    <a href="https://www.youtube.com/watch?v=Mz7NbIgJqsc"
       target="_blank">
       <img src="http://img.youtube.com/vi/Mz7NbIgJqsc/0.jpg"
            alt="League of Legends Deep Analysis - Setup and Extraction (Part 1)"
            width="240" height="180" border="10" />
    </a>
</div>

# TLoL-py - League of Legends Deep Learning Library

TLoL-py is the Python component of the TLoL League of Legends deep learning library.
It provides a set of utility methods and classes to deal with League of Legends
game playing, deep learning datasets and provides a library to build a deep learning
agent which can play League of Legends.

This module is currently updated to patch `13.23`.

To use this module, go to the `releases` section of the
[TLoL Scraper](https://github.com/MiscellaneousStuff/tlol-scraper)
repo and download the most recent release.

Refer to [TLoL](https://github.com/MiscellaneousStuff/tlol)
for information relating to large scale training and analysis
datasets which are compatible with this module.

A full explanation of how this repository works can be found in
[this](https://miscellaneousstuff.github.io/project/2021/11/19/tlol-part-6-dataset-generation.html)
blog post.

## About

Disclaimer: This project is not affiliated with Riot Games in any way.

If you are interested in using this project or are just curious, send an email to
[raokosan@gmail.com](mailto:raokosan@gmail.com).

# Quick Start Guide

## Get TLoL-py

### From Source

You can install the TLoL python module from a local clone of the git repo:

```bash
git clone https://github.com/MiscellaneousStuff/tlol-py.git
pip install --upgrade tlol-py/
```

## Usage

To run an agent, make sure that your client is set to automatically log-in
when it's opened.

## Config

This module requires the `EnableReplayApi=1` flag to be added to `.\Config\game.cfg`
within the League of Legends installation directory, underneath the `[General]`
section so it should look like:

```config
[General]
...
EnableReplayApi=1
```

It may also be necessary to add this to `.\DATA\cfg\game.cfg` if this file
exists.