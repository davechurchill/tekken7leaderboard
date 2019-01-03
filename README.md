# Tekken 7 Leaderboard Scraper
Automatic scraper for the Tekken 7 PC leaderboard

Sample usage video: https://www.youtube.com/watch?v=ezfaczOPmww

This program is written in python3 and uses opencv and OCR to scrape the Tekken 7 PC Leaderboard

All of the dependency / imports can be installed from pip, with the extra small step of installing the binary for the pytesseract OCR library: https://pypi.org/project/pytesseract/

The program works as follows:
- Run Tekken 7 in Borderless mode, open the online leaderboard menu
- Start the python program by typing 'python tekken_rankings.py'
- Switch back to Tekken 7 in the next 3 seconds so that the window has focus
- The python program will do the following in an infinite loop:
  - Take a screenshot of a predefined area of the monitor which contains the ranking table
  - Loop through each row of the ranking table, doing the following for each row:
    - Form a box around the name, character, and rank icon of that given player
    - Attempt to use OCR to determine the player name
    - Attempt to match the character icon to a list of named character images
    - Attempt to match the rank icon to a list of named rank images
    - Output the calculated information to the end of a given file
  - Press the 'D' key on the keyboard so Tekken loads the next page of rankings
- Loops infinitely until you stop the program

This program will not work until you do the following:
- Generate a list of character / rank images of the correct size (sample code for doing this is given at the bottom of the program). I am not putting my images online here because they are copyrighted.
- Change the hard-coded player name, character icon, and rank icon rectangle size / locations to fit your monitor / tekken resolution. 

Have fun! Pull requests gladly accepted (especially for things like different resolution box values)
