from datetime import datetime
import logging


""" Settings for the project """

# path to sqlite database
db_path = "/home/kakarukeys/Documents/plan/projects/Fundamental Analysis project/algo-fa.db"

# path to log file
log_file_path = "/home/kakarukeys/Documents/plan/projects/Fundamental Analysis project/algo-fa.log"
log_level = logging.INFO

# there is data available between these two dates:
start_date = datetime(1986, 1, 1)
end_date = datetime(2014, 12, 15)
