from datetime import datetime
import os


""" Settings for the project """

symbols = {
	"C6L": "Singapore Airlines",
	"J7X": "Tiger Airways",
	"S53": "SMRT",
	"C52": "ComfortDelGro",
	"N03": "Neptune Orient Lines",
	"Z74": "Singtel",
	"CC3": "Starhub",
	"B2F": "M1",
}
start_date = datetime(2004, 3, 1)
end_date = datetime(2014, 3, 1)

archive_directory = "/home/kakarukeys/ownCloud/Fundamental Analysis project/archive"
yahoo_archive_directory = os.path.join(archive_directory, "yahoo")
wsj_archive_directory = os.path.join(archive_directory, "wsj")
