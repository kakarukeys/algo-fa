algo-fa
=======

Algorithmic Fundamental Analysis Tool


Setting up the development environment on Ubuntu/Linux Mint
-----------------------------------------------------------

1. sudo apt-get install python3.3, python3-pip, tk-dev, python3-tk, libpng12-dev (The last 3 are for matplotlib)
2. sudo pip3 install virtualenvwrapper
3. export WORKON_HOME=~/virtualenvs
4. source /usr/local/bin/virtualenvwrapper.sh (You may want to put these two lines inside your ~/.bashrc)
5. mkvirtualenv -p /usr/bin/python3.3 algo-fa
6. pip install -r requirements.txt
7. add2virtualenv /path/to/project_root (where this file is found)
