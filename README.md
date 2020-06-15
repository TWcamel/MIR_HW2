###### tags: MIR, NTHU, music-information-retrieval, tempo estimation

Homework 2 for Music Information Retrieval
==
- [Homework 2 for Music Information Retrieval](#homework-2-for-music-information-retrieval)
  - [Environment](#environment)
  - [Dataset](#dataset)
  - [Prerequisite](#prerequisite)
  - [Usages](#usages)
  - [Discussions of HW](#discussions-of-hw)

## Environment
- Ubuntu 18.04.1 #5.3.0-46-generic
- Python 3.6.9 (using NeoVim v0.3.8)
- Extra packages: see `requirements.txt`

## Dataset
1. Download the `.wav` files.
2. Download the `tempo` and `beat` annotations.
3. Modified the `DB` variables to where you decomposition the data.

## Prerequisite
In this repo, the `pipenv` python package was used to manage this project's python package. `pipenv` provides a handy way to deploy projects. To use `pipenv`, first, you need to install it.
```
$ sudo apt-get install pipenv
```
Once you have done the installation, run below code to install the packages that you need in this HW:
```
$ pipenv sync 
```
## Usages
The source `JCM` files are `.mp3` format. The intuitive way to implement the MIR is to utilize `.wav` files. Here, we also provided the converting program: `mp3Towav.sh`. To convet from `.mp3` to `.wav`, you first need to install `ffmepg` tool.
```
$ sudo apt-get install ffmepg
```
Second, you need to modify the target file variable in the `mp3Towav.sh` file.
```
JCMFILES=./JCS/JCS_audio
```

## Discussions of HW
We have done the Task1-Task2. The discussion and the results was showed on [here](https://www.notion.so/twcamel/Mir_hw2-9099d1c00d844bc1af3e3e09307b1e5e). Enjoy it!