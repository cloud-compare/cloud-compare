#!/bin/sh

# Check all python for pep8 compliance

find . -name '*.py' | grep -v '/migrations/' | grep -v 'settings.py' | xargs pep8 
