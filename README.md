# Tekken 7 Leaderboard Scraper
Automatic scraper for the Tekken 7 PC leaderboard

Sample usage video: https://www.youtube.com/watch?v=ezfaczOPmww

This program is written in python3 and uses opencv and OCR to scrape the Tekken 7 PC Leaderboard

All of the dependency / imports can be installed from pip, with the extra small step of installing the binary for the pytesseract OCR library: https://pypi.org/project/pytesseract/

The program works as follows:

* 

The program works as follows:

- Run Tekken 7 in Borderless mode, open the online leaderboard menu
- Start the python program by typing 'python tekken_rankings.py'
- Switch back to Tekken 7 in the next 3 seconds so that the window has focus
- Watch as the program parses the leaderboard

