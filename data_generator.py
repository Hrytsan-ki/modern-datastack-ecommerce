import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
import random

fake = Faker()
Faker.seed(42)

def generate_clients(num=1000):
    clients = []
    for i in range(1, num + 1):
        email = fake.email() if random.random() > 0.1 else None # 10% пропущених email
        clients.append({
            'client_id': i,
            'client_name': fake.name(),
            'email': email,
            'registration_date': fake.date_between(start_date='-2y', end_date='today')
        })
    return pd.DataFrame(clients)

def generate_bouquets(num=50):
    bouquets = []
    for i in range(1, num + 1):
        bouquets.append({
            'bouquet_id': i,
            'bouquet_name': fake.word().capitalize() + " " + fake.word(),
            'price': round(random.uniform(15.0, 250.0), 2),
            'category': random.choice(['Roses', 'Tulips', 'Mixed', 'Exotic'])
        })
    return pd.DataFrame(bouquets)

def generate_florists(num=20):
    florists = []
    for i in range(1, num + 1):
        florists.append({
            'florist_id': i,
            'florist_name': fake.name(),
            'experience_years': random.randint(1, 10)
        })
    return pd.DataFrame(florists)

def generate_deliveries(clients_df, bouquets_df, florists_df, num=5000):
    deliveries = []
    client_ids = clients_df['client_id'].tolist()
    bouquet_ids = bouquets_df['bouquet_id'].tolist()
    florist_ids = florists_df['florist_id'].tolist()

    for i in range(1, num + 1):
        deliveries.append({
            'delivery_id': i,
            'client_id': random.choice(client_ids),
            'bouquet_id': random.choice(bouquet_ids),
            'florist_id': random.choice(florist_ids),
            'quantity': random.randint(1, 5),
            'delivery_date': fake.date_time_between(start_date='-1y', end_date='now')
        })
    return pd.DataFrame(deliveries)

def generate_payments(clients_df, deliveries_df, num=5000):
    payments = []
    client_ids = clients_df['client_id'].tolist()
    delivery_ids = deliveries_df['delivery_id'].tolist()

    for i in range(1, num + 1):
        payments.append({
            'payment_id': i,
            'delivery_id': random.choice(delivery_ids),
            'client_id': random.choice(client_ids),
            'amount': round(random.uniform(15.0, 250.0), 2),
            'payment_date': fake.date_time_between(start_date='-1y', end_date='now')
        })
    return pd.DataFrame(payments)

def generate_reviews(clients_df, bouquets_df, num=2000):
    reviews = []
    client_ids = clients_df['client_id'].tolist()
    bouquet_ids = bouquets_df['bouquet_id'].tolist()

    for i in range(1, num + 1):
        # 20% записів залишаємо порожніми (None) для поля comment
        comment = None if random.random() < 0.2 else fake.sentence()
        reviews.append({
            'review_id': i,
            'bouquet_id': random.choice(bouquet_ids),
            'client_id': random.choice(client_ids),
            'rating': random.randint(1, 5),
            'comment': comment
        })
    return pd.DataFrame(reviews)    

# Генерація і збереження в пам'яті
df_clients = generate_clients()
df_bouquets = generate_bouquets()
df_florists = generate_florists()
df_deliveries = generate_deliveries(df_clients, df_bouquets, df_florists, num=5000)
df_payments = generate_payments(df_clients, df_deliveries, num=5000)
df_reviews = generate_reviews(df_clients, df_bouquets, num=2000)

print(f"Згенеровано: {len(df_clients)} clients, {len(df_bouquets)} bouquets, {len(df_florists)} florists, {len(df_deliveries)} deliveries, {len(df_payments)} payments, {len(df_reviews)} reviews.")

# Рядок підключення до PostgreSQL (з docker-compose.yml)
DB_URL = "postgresql://admin:adminpassword@localhost:5432/ecommerce_dwh"
engine = create_engine(DB_URL)

def load_data_to_dwh():
    with engine.connect() as conn:
        # Створення "сирої" схеми, якщо вона не існує
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()
        
        # Завантаження DataFrames у базу (Extract & Load)
        print("Завантаження clients...")
        df_clients.to_sql('clients', engine, schema='raw', if_exists='replace', index=False)

        print("Завантаження bouquets...")
        df_bouquets.to_sql('bouquets', engine, schema='raw', if_exists='replace', index=False)

        print("Завантаження florists...")
        df_florists.to_sql('florists', engine, schema='raw', if_exists='replace', index=False)

        print("Завантаження deliveries...")
        df_deliveries.to_sql('deliveries', engine, schema='raw', if_exists='replace', index=False)

        print("Завантаження payments...")
        df_payments.to_sql('payments', engine, schema='raw', if_exists='replace', index=False)

        print("Завантаження reviews...")
        df_reviews.to_sql('reviews', engine, schema='raw', if_exists='replace', index=False)

        print("Дані успішно завантажені у схему 'raw'!")

if __name__ == "__main__":
    load_data_to_dwh()