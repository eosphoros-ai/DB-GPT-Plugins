import random
import string
import os
import duckdb
from datetime import datetime, timedelta

default_db_path =  os.path.join(os.getcwd(), "mock_datas")
duckdb_path =os.getenv("DB_DUCKDB_PATH", default_db_path + "/db-gpt-test.db")

if __name__ == "__main__":

    def build_table(connection):
        connection.execute(
            """CREATE TABLE user (
              id INTEGER NOT NULL,
              name VARCHAR,
              email VARCHAR,
              mobile VARCHAR,
              gender VARCHAR,
              birth DATE,
              country VARCHAR,
              city VARCHAR,
              create_time TIMESTAMP,
              update_time TIMESTAMP,
              CONSTRAINT USER_PK PRIMARY KEY (id)
          );"""
        )

        connection.execute(
            """CREATE TABLE tran_order (
              id INTEGER NOT NULL,
              order_no VARCHAR,
              product_name VARCHAR,
              product_category VARCHAR,
              amount NUMERIC(10, 2),
              pay_status VARCHAR,
              user_id INTEGER  NOT NULL,
              user_name VARCHAR,
              create_time TIMESTAMP,
              update_time TIMESTAMP,
              CONSTRAINT ORDER_PK PRIMARY KEY (id)
          );"""
        )

    def user_build(names: [], country: str, grander: str = "Male") -> []:
        countries = ["China", "US", "India", "Indonesia", "Pakistan"]  # 国家列表
        cities = {
            "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Hangzhou"],
            "US": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
            "Indonesia": ["Jakarta", "Surabaya", "Medan", "Bandung", "Makassar"],
            "Pakistan": ["Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Multan"],
        }
        users = []
        for i in range(1, len(names) + 1):
            if grander == "Male":
                id = int(str(countries.index(country) + 1) + "10") + i
            else:
                id = int(str(countries.index(country) + 1) + "20") + i

            name = names[i - 1]
            email = f"{names}@example.com"
            mobile = "".join(random.choices(string.digits, k=10))
            gender = grander
            birth = f"19{random.randint(60, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            country = country
            city = random.choice(cities[country])

            now = datetime.now()
            year = now.year

            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31)
            random_date = start + timedelta(days=random.randint(0, (end - start).days))
            random_time = datetime.combine(
                random_date, datetime.min.time()
            ) + timedelta(seconds=random.randint(0, 24 * 60 * 60 - 1))

            random_datetime_str = random_time.strftime("%Y-%m-%d %H:%M:%S")
            create_time = random_datetime_str
            users.append(
                (id, name, email, mobile, gender, birth, country, city, create_time)
            )
        return users

    def gnerate_all_users(cursor):
        users = []
        users_f = ["ZhangWei", "LiQiang", "ZhangSan", "LiSi"]
        users.extend(user_build(users_f, "China", "Male"))
        users_m = ["Hanmeimei", "", "LiNa", "ZhangLi", "ZhangMing"]
        users.extend(user_build(users_m, "China", "Female"))

        users1_f = ["James", "John", "David", "Richard"]
        users.extend(user_build(users1_f, "US", "Male"))
        users1_m = ["Mary", "Patricia", "Sarah"]
        users.extend(user_build(users1_m, "US", "Female"))

        users2_f = ["Ravi", "Rajesh", "Ajay", "Arjun", "Sanjay"]
        users.extend(user_build(users2_f, "India", "Male"))
        users2_m = ["Priya", "Sushma", "Pooja", "Swati"]
        users.extend(user_build(users2_m, "India", "Female"))
        for user in users:
            cursor.execute(
                "INSERT INTO user (id, name, email, mobile, gender, birth, country, city, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                user,
            )
        cursor.commit()

        return users

    def gnerate_all_orders(users, cursor):
        orders = []
        orders_num = 200
        categories = ["Clothing", "Food", "Home Appliance", "Mother and Baby", "Travel"]

        categories_product = {
            "Clothing": ["T-shirt", "Jeans", "Skirt", "Other"],
            "Food": ["Snack", "Fruit"],
            "Home Appliance": ["Refrigerator", "Television", "Air conditioner"],
            "Mother and Baby": ["Diapers", "Milk Powder", "Stroller", "Toy"],
            "Travel": ["Tent", "Fishing Rod", "Bike", "Rawalpindi", "Multan"],
        }

        for i in range(1, orders_num + 1):
            id = i
            order_no = "".join(random.choices(string.ascii_uppercase, k=3)) + "".join(
                random.choices(string.digits, k=10)
            )
            product_category = random.choice(categories)
            product_name = random.choice(categories_product[product_category])
            amount = round(random.uniform(0, 10000), 2)
            pay_status = random.choice(["SUCCESS", "FAILD", "CANCEL", "REFUND"])
            user_id = random.choice(users)[0]
            user_name = random.choice(users)[1]

            now = datetime.now()
            year = now.year

            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31)
            random_date = start + timedelta(days=random.randint(0, (end - start).days))
            random_time = datetime.combine(
                random_date, datetime.min.time()
            ) + timedelta(seconds=random.randint(0, 24 * 60 * 60 - 1))

            random_datetime_str = random_time.strftime("%Y-%m-%d %H:%M:%S")
            create_time = random_datetime_str

            order = (
                id,
                order_no,
                product_category,
                product_name,
                amount,
                pay_status,
                user_id,
                user_name,
                create_time,
            )
            cursor.execute(
                "INSERT INTO tran_order (id, order_no, product_name, product_category, amount, pay_status, user_id, user_name, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                order,
            )

        cursor.commit()


    connection = duckdb.connect(duckdb_path)


    build_table(connection)

    connection.commit()

    cursor = connection.cursor()

    users = gnerate_all_users(cursor)


    gnerate_all_orders(users, cursor)

    connection.commit()

    cursor.execute("SELECT * FROM user")
    data = cursor.fetchall()
    print(data)

    cursor.execute("SELECT count(*) FROM tran_order")
    data = cursor.fetchall()
    print("orders:" + str(data))
