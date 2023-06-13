### Native DB-GPT-PLUGIN Provide simple report analysis through natural language for the specified database

#### 1.The current plug-in will be automatically loaded when DB-GPT starts, choose to use it in plug-in mode，Currently only supported [MYSQL, DUCKDB]
#### 2.The plug-in contains a test database with users and corresponding order information, which can be tested based on users and orders
#### 3.If you need to use the local database, please configure the database information in the .env of DB-GPT, as follows:
```
    # mysql config like this
    DB_TYPE=MYSQL
    DB_DATABASE=gpt-user
    DB_HOST=127.0.0.1
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=aa123456
```
# Use Cases:
```
    Plugin Mode -> [select dashboard plugin] -> [say to ai]:Use a histogram to analyze the total order amount of users in different cities
```

*There are still Chinese adaptation problems in the currently displayed charts to be resolved