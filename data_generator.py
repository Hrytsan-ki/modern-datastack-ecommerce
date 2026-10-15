import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
import random
fake = Faker()
Faker.seed(42)
def generate_users(num=1000):
    users = []
    for i in range(1, num + 1):
        email = fake.email() if random.random() > 0.1 else None # 10% пропущених email
        users.append({
        'user_id': i,
        'name': fake.name(),
        'email': email,
        'registration_date': fake.date_between(start_date='-2y', end_date='today')
        })
    return pd.DataFrame(users)
def generate_products(num=50):
    products = []
    for i in range(1, num + 1):
        products.append({
        'product_id': i,
        'name': fake.word().capitalize() + " " + fake.word(),
        'price': round(random.uniform(10.0, 500.0), 2),
        'category': random.choice(['Electronics', 'Clothing', 'Home', 'Toys'])
        })
    return pd.DataFrame(products)
def generate_orders(users_df, products_df, num=5000):
    orders = []
    user_ids = users_df['user_id'].tolist()
    product_ids = products_df['product_id'].tolist()

    for i in range(1, num + 1):
        orders.append({
        'order_id': i,
        'user_id': random.choice(user_ids),
        'product_id': random.choice(product_ids),
        'quantity': random.randint(1, 5),
        'order_date': fake.date_time_between(start_date='-1y', end_date='now')
        })
    return pd.DataFrame(orders)

def generate_reviews(users_df, products_df, num=2000):
    reviews = []
    user_ids = users_df['user_id'].tolist()
    product_ids = products_df['product_id'].tolist()

    for i in range(1, num + 1):
        # 20% записів залишаємо пустими (None) для поля comment
        comment = None if random.random() < 0.2 else fake.sentence()
        reviews.append({
            'review_id': i,
            'product_id': random.choice(product_ids),
            'user_id': random.choice(user_ids),
            'rating': random.randint(1, 5),
            'comment': comment
        })
    return pd.DataFrame(reviews)    
# Генерація і збереження в пам'яті (можна також зберегти в CSV)
df_users = generate_users()
df_products = generate_products()
df_orders = generate_orders(df_users, df_products)
df_reviews = generate_reviews(df_users, df_products, num=2000)
print(f"Згенеровано: {len(df_users)} users, {len(df_products)} products, {len(df_orders)} orders, {len(df_reviews)} reviews.")


# Рядок підключення до PostgreSQL (з docker-compose.yml)
DB_URL = "postgresql://admin:adminpassword@localhost:5432/ecommerce_dwh"
engine = create_engine(DB_URL)
def load_data_to_dwh():
    with engine.connect() as conn:
        # Створення "сирої" схеми, якщо вона не існує
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()
        # Завантаження DataFrames у базу (Extract & Load)
        # параметр if_exists='replace' імітує повне перезавантаження (Full Load)
        print("Завантаження users...")
        df_users.to_sql('users', engine, schema='raw', if_exists='replace', index=False)

        print("Завантаження products...")
        df_products.to_sql('products', engine, schema='raw', if_exists='replace',
        index=False)

        print("Завантаження orders...")
        df_orders.to_sql('orders', engine, schema='raw', if_exists='replace',
        index=False)

        print("Завантаження reviews...")
        df_reviews.to_sql('reviews', engine, schema='raw', if_exists='replace', index=False)

        print("Дані успішно завантажені у схему 'raw'!")

if __name__ == "__main__":
    load_data_to_dwh()