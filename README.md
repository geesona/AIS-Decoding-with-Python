# AIS-Decoding-with-Python
Python code written on ubuntu to receive coded AIS messages that are decoded and displayed.
Each hour the code write to a number of files to record what has happed during that hour.
The "ais.txt" file is a history of the screen contents after each hour of listening to messages.
The "master.txt" file keeps a record of the ship's MMSI number and associated ship's name for A class ships.
The "bmast.txt" file keeps a record of the ship's MMSI number and associated ship's name for B class ships.
The "error.txt" file is mainly for messages received with errors in the ship's position.
The "graph.txt" file is a comma delimited file of hourly staistics that can be displayed as graphs.

