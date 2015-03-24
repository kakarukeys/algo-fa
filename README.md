algo-fa
=======

Algorithmic Fundamental Analysis Tool


Setting up the development environment
---------------------------------------
The instructions are designed for Ubuntu/Linux Mint.

1. sudo apt-get install python3.3, python3-pip, tk-dev, python3-tk, libpng12-dev (The last 3 are for matplotlib)
2. sudo pip3 install virtualenvwrapper
3. export WORKON_HOME=~/virtualenvs
4. source /usr/local/bin/virtualenvwrapper.sh (You may want to put these two lines inside your ~/.bashrc)
5. mkvirtualenv -p /usr/bin/python3.3 algo-fa
6. pip install -r requirements.txt
7. add2virtualenv /path/to/project_root (where this file is found)

Downloading data
-----------------
First activate the virtual environment and go to project directory,

    cd examples
	vim settings.py

change *db_path* and *log\_file\_path* to suitable values and save the file. To create the database tables,

	python create_tables.py

To download the data,

	python update_price_data.py
	python update_financial_data.py

To enrich the data,

	python enrich.py

Performing analysis
--------------------
To plot some graphs to explore fundamental metrics,

	python explore.py

Running unit-tests
------------------
Go to project directory,

    python -m unittest
