# EA Graphics Manager
Program for parsing FSH, SSH, XSH, PSH, GSH and MSH files from EA games.

Technologies used: Python 3.11, tkinter

This program **<ins>is not finished yet</ins>**.
It may not support all image types.

<img src="src\data\img\usage_v0.14.1.gif">

More info about EA Image file format can be found on [Xentax Wiki](https://web.archive.org/web/20230817170521/http://wiki.xentax.com/index.php/EA_SSH_FSH_Image).


# Dependencies

* **[ReverseBox](https://github.com/bartlomiejduda/ReverseBox)**


# Building on Windows

1. Install  **[Python 3.11.6](https://www.python.org/downloads/release/python-3116/)**
2. Install **[PyCharm 2023 (Community Edition)](https://www.jetbrains.com/pycharm/download/other.html)**
3. Create virtualenv and activate it
   - python3 -m venv \path\to\new\virtual\environment
   - .\venv\Scripts\activate.bat
4. Install all libraries from requirements.txt
   - pip3 install -r requirements.txt
5. Run the src\main.py file


# Image formats support table

| Image format                | Preview support     | Export support     | Import support     | Example Games                                                                                                                                                                                                                                                                                                |
|-----------------------------|---------------------|--------------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <center>1 / 0x01</center>   | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2) <br> Def Jam: Fight for New York (PS2) <br> Golden Eye: Rogue Agent (PS2) <br> Harry Potter and the Chamber of Secrets (PS2) <br> Medal of Honor Frontline (PS2)                                                                                                  |
| <center>2 / 0x02</center>   | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2) <br> Def Jam: Fight for New York (PS2) <br> FIFA Street (PS2) <br> Fight Night: Round 3 (PS2) <br> Golden Eye: Rogue Agent (PS2) <br> Harry Potter and the Chamber of Secrets (PS2) <br> Medal of Honor Frontline (PS2) <br> NHL 2001 <br> NHL 2002 <br> NHL 2003 |
| <center>3 / 0x03</center>   | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2)                                                                                                                                                                                                                                                                   |
| <center>4 / 0x04</center>   | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2) <br> Golden Eye: Rogue Agent (PS2) <br> Harry Potter and the Chamber of Secrets (PS2) <br> Medal of Honor Frontline (PS2)                                                                                                                                         |
| <center>5 / 0x05</center>   | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2) <br> Def Jam: Fight for New York (PS2) <br> Golden Eye: Rogue Agent (PS2) <br> Medal of Honor Frontline (PS2)                                                                                                                                                     |
| <center>11 / 0x0B</center>  | <center>❌</center>  | <center>❌</center> | <center>❌</center> | Fight Night Round 3 (PS2)                                                                                                                                                                                                                                                                                    |
| <center>13 / 0x0D</center>  | <center>❌</center>  | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2)                                                                                                                                                                                                                                                                   |
| <center>14 / 0x0E</center>  | <center>❌</center>  | <center>❌</center> | <center>❌</center> | Cricket 2005 (PS2) <br> Cricket 2007 (PS2)  <br> FIFA Street (PS2)                                                                                                                                                                                                                                           |
| <center>35 / 0x23</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2000 (PS1)                                                                                                                                                                                                                                                                                              |
| <center>59 / 0x3B</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Madden NFL 08 (PSP)                                                                                                                                                                                                                                                                                          |
| <center>64 / 0x40</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2000 (PS1) <br> NBA Live 97 (PS1)                                                                                                                                                                                                                                                                       |
| <center>65 / 0x41</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2000 (PS1) <br> NBA Live 97 (PS1) <br> NHL 2001 (PS1)                                                                                                                                                                                                                                                   |
| <center>66 / 0x42</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | NBA Live 97 (PS1)                                                                                                                                                                                                                                                                                            |
| <center>67 / 0x43</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | ReBoot (PS1)                                                                                                                                                                                                                                                                                                 |
| <center>69 / 0x45</center>  | <center>❌</center>  | <center>❌</center> | <center>❌</center> | FIFA 2009 (PS2)  <br> Fight Night Round 3 (PSP)  <br> Madden NFL 06 (PSP)  <br> Madden NFL 08 (PSP)                                                                                                                                                                                                          |
| <center>88 / 0x58</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Need For Speed: Undercover (PSP)  <br>Need for Speed Carbon: Own the City (PSP/Zeebo)                                                                                                                                                                                                                        |
| <center>89 / 0x59</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2006 (PSP)                                                                                                                                                                                                                                                                                              |
| <center>90 / 0x5A</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2006 (PSP)                                                                                                                                                                                                                                                                                              |
| <center>91 / 0x5B</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2006 (PSP)                                                                                                                                                                                                                                                                                              |
| <center>92 / 0x5C</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 2006 (PSP) <br> Madden NFL 08 (PSP)                                                                                                                                                                                                                                                                     |
| <center>93 / 0x5D</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | FIFA 14 (PSP) <br> FIFA 2006 (PSP) <br> FIFA 2009 (PSP) <br> Fight Night Round 3 (PSP) <br> Madden NFL 08 (PSP)                                                                                                                                                                                              |
| <center>96 / 0x60</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | SimCity 4 Deluxe (PC)                                                                                                                                                                                                                                                                                        |
| <center>97 / 0x61</center>  | <center>✔️</center> | <center>❌</center> | <center>❌</center> | SimCity 4 Deluxe (PC)                                                                                                                                                                                                                                                                                        |
| <center>109 / 0x6D</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Need For Speed: Porsche Unleashed (PC)   <br>UEFA Euro 2004 (PC/XBOX)                                                                                                                                                                                                                                        |
| <center>115 / 0x73</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Need for Speed Carbon: Own the City (PSP/Zeebo)                                                                                                                                                                                                                                                              |
| <center>119 / 0x77</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Need for Speed Carbon: Own the City (PSP/Zeebo)                                                                                                                                                                                                                                                              |
| <center>120 / 0x78</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Need For Speed: Porsche Unleashed (PC)  <br>Need For Speed II (PC) <br>Need For Speed III: Hot Pursuit (PC) <br>Need For Speed: High Stakes (PC) <br>UEFA Euro 2004 (PC/XBOX)                                                                                                                                |
| <center>123 / 0x7B</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | SimCity 4 Deluxe (PC)                                                                                                                                                                                                                                                                                        |
| <center>125 / 0x7D</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | SimCity 4 Deluxe (PC)                                                                                                                                                                                                                                                                                        |
| <center>126 / 0x7E</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | Need For Speed III: Hot Pursuit (PC) <br> Need For Speed: High Stakes (PC)                                                                                                                                                                                                                                   |
| <center>127 / 0x7F</center> | <center>✔️</center> | <center>❌</center> | <center>❌</center> | SimCity 4 Deluxe (PC)                                                                                                                                                                                                                                                                                        |


# EA-Graph-Man Noesis Script

In the src\scripts directory there is an script
which can be used for viewing EA graphics in Noesis.
To use script with Noesis, please follow below steps:

1. Go to \src\scripts\ directory
2. Copy script to \noesis\plugins\python\ directory
3. Open any EA Image in Noesis

# Badges
![GitHub](https://img.shields.io/github/license/bartlomiejduda/EA-Graphics-Manager?style=plastic)
![GitHub repo size](https://img.shields.io/github/repo-size/bartlomiejduda/EA-Graphics-Manager?style=plastic)
![GitHub all releases](https://img.shields.io/github/downloads/bartlomiejduda/EA-Graphics-Manager/total)
![GitHub last commit](https://img.shields.io/github/last-commit/bartlomiejduda/EA-Graphics-Manager?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/bartlomiejduda/EA-Graphics-Manager?style=plastic)
