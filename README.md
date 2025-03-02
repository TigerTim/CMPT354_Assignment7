# DataManager

## Overview
DataManager is a Python-based application enabling users to interact with various relational databases. It involves information retrieval and database modifications by executing queries. 

## Features
- **User Login:** Authenticate users based on their user ID
- **Search Business:** Filter businesses based on name, city, star rating and display ordered results
- **Search Users:** Find users based on name, review count, and average star rating.
- **Make Friend:** Establish friendships between users and store the relationship in the database.
- **Review Business:** Allow users to submit business reviews and update the business’s rating and review count.

## Installation
### Setup Steps
### 1. Clone the repository
```sh
git clone https://github.com/TigerTim/DataManager.git
```
### 2. Install required Python dependencies
```sh
pip install pyodbc
```
### 3. Configure the database connection by updating the credentials
```sh
conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=cypress.csil.sfu.ca;'
        'DATABASE=gpd354;'
        'UID=s_gpd;'
        'PWD=Mr43Fdrnahnjye74;'
        'Encrypt=yes;'
        'TrustServerCertificate=yes;'
    )
```
### 4. Run the application
```sh
python main.py
```

## Contributing
Feel free to fork and contribute improvements. Submit a pull request with detailed explanations of your changes.

## License
This project is licensed under the MIT License.
