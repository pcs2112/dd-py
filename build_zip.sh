#!/bin/bash

_cwd="$PWD"
_targetRoot="$HOME/Downloads"
_rootDirName="dd-py"

rm -rf "$_targetRoot/$_rootDirName"
rm -rf "$_targetRoot/$_rootDirName.zip"
mkdir "$_targetRoot/$_rootDirName"
mkdir "$_targetRoot/$_rootDirName/in"
cp -r "$_cwd/src" "$_targetRoot/$_rootDirName/src"
cp -v "$_cwd/.example.env." "$_targetRoot/$_rootDirName/.env"
cp "$_cwd/app.py" "$_targetRoot/$_rootDirName/app.py"
cp "$_cwd/requirements.txt" "$_targetRoot/$_rootDirName/requirements.txt"
find "$_targetRoot/$_rootDirName" | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
cd "$_targetRoot/${_rootDirName}"
zip -r "$_targetRoot/$_rootDirName.zip" .
