# ebayfinder
This is my early version of my product scraper utilizing Google Gemini to return the best prices on product based a certain criteria.

This project is a web application built using Flask.

Use this code as you please, this is meant to show the possibilities of using Generative AI for product scraping.

## Prerequisites

Ensure you have Python installed on your system. This project was developed using Python 3.9, but it should work with any version of Python 3.x.

## Installation

1. Clone the repository to your local machine:
    ```sh
    git clone https://github.com/MohammedAyesh/ebayfinder.git
    cd your-repo
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```sh
       pip install Flask Flask-WTF Jinja2 pandas google-generativeai scrapfly 
    ```
## Required Python Packages

Below are the necessary pip imports for this project:
- Flask
- Flask-WTF
- Jinja2
- Pandas
- Scrapfly
- Google Gemini

You can install these packages by running:
  ```
pip install Flask Flask-WTF Jinja2 pandas google-generativeai scrapfly 
  ```

**##Setting API Keys**

Go to finresult.py to line 9 where it says:
  ```
genai.configure(api_key="")
  ```
Insert you gemini api key

Go to ebay.py to line 15 where it says
  ```
SCRAPFLY_KEY = ""
  ```
Insert you Scrapfly Key here



To run the application, use the following command:
  ```
python app.py
  ```

![image](https://github.com/MohammedAyesh/ebayfinder/assets/46912003/4b9b562e-b092-4bb5-a057-3c6221d5a907)
![image](https://github.com/MohammedAyesh/ebayfinder/assets/46912003/8de9d05b-fd58-4048-b71a-80e954bd2836)


