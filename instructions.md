# Getting Started
* Clone the repo to your documents folder with the **git clone** command through the terminal
* Make sure you're in the main directory of the project where the requirements.txt file is located
* Start up your virtual environment with **python3 -m venv venv** and then **source venv/bin/activate**
* Install dependencies from the requirements file with **pip install -r requirements.txt**
* Set your environment to development with **export FLASK_ENV=development**
* Download postgreSQL from https://www.postgresql.org/
* From your terminal create your db with: **createdb dbname**
* ## Set up the following env variables with **export var=value**:
  * DATABASE_URL=postgresql:///yourdb 
  * SECRET_KEY=yoursecretkey 
  * MAIL_USERNAME=youremail@email.com 
  * MAIL_PASSWORD=youremailpassword 
* Download the relevant spacy model with: **python3 -m spacy download en_core_web_sm**
* Update spacy symlink with **python -m spacy link en_core_web_sm**
* Use **flask run** command to start up your project on localhost:5000
* Enjoy!