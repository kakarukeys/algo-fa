from datetime import datetime
import os


""" Settings for the project """

symbols = ("C6L", "J7X", "S53", "C52", "N03", "Z74", "CC3", "B2F")
start_date = datetime(2004, 3, 1)
end_date = datetime(2014, 3, 1)

archive_directory = "/home/kakarukeys/ownCloud/Fundamental Analysis project/test_archive"
yahoo_archive_directory = os.path.join(archive_directory, "yahoo")
wsj_archive_directory = os.path.join(archive_directory, "wsj")
