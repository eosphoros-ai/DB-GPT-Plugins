import random
import string
import duckdb

if __name__ == '__main__':
    # 生成测试数据
    num_users = 10  # 用户数量
    countries = ['China', 'United States', 'India', 'Indonesia', 'Pakistan']  # 国家列表
    cities = {'China': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Hangzhou'],
              'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
              'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'],
              'Indonesia': ['Jakarta', 'Surabaya', 'Medan', 'Bandung', 'Makassar'],
              'Pakistan': ['Karachi', 'Lahore', 'Faisalabad', 'Rawalpindi', 'Multan']}  # 城市列表

    users = []  # 用户列表
    for i in range(1, num_users + 1):
        name = ''.join(random.choices(string.ascii_uppercase, k=5))
        email = f'user{i}@example.com'
        mobile = ''.join(random.choices(string.digits, k=10))
        gender = random.choice(['Male', 'Female'])
        birth = f'19{random.randint(60, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}'
        country = random.choice(countries)
        city = random.choice(cities[country])
        users.append((name, email, mobile, gender, birth, country, city))

    # 连接 DuckDB 数据库
    connection = duckdb.connect('db-gpt-test.db')

    # 插入测试数据
    cursor = connection.cursor()
    for user in users:
        cursor.execute('INSERT INTO user (name, email, mobile, gender, birth, country, city) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       user)

    # 提交事务
    connection.commit()

    # 查询测试数据
    cursor.execute('SELECT * FROM user')
    data = cursor.fetchall()
    print(data)
