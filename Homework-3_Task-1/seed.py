import os
import random

os.environ["PGCLIENTENCODING"] = "UTF8"

import psycopg2
from faker import Faker
from psycopg2.extras import execute_values


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:242103resor@localhost:5432/task_manager"
)

fake = Faker()


def seed_database():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "TRUNCATE TABLE tasks, status, users RESTART IDENTITY CASCADE"
        )

        statuses = [
            ("new",),
            ("in progress",),
            ("completed",)
        ]

        execute_values(
            cursor,
            "INSERT INTO status (name) VALUES %s",
            statuses
        )

        users = []

        for i in range(10):
            if i < 3:
                email = f"user{i + 1}@example.com"
            else:
                email = fake.unique.email()

            users.append(
                (
                    fake.name(),
                    email
                )
            )

        execute_values(
            cursor,
            "INSERT INTO users (fullname, email) VALUES %s",
            users
        )

        cursor.execute(
            "SELECT id FROM users ORDER BY id"
        )

        user_ids = [
            row[0]
            for row in cursor.fetchall()
        ]

        cursor.execute(
            "SELECT id, name FROM status"
        )

        status_ids = {
            name: status_id
            for status_id, name in cursor.fetchall()
        }

        tasks = []

        for _ in range(25):
            description = (
                None
                if random.random() < 0.25
                else fake.text(max_nb_chars=150)
            )

            tasks.append(
                (
                    fake.sentence(nb_words=4).rstrip("."),
                    description,
                    random.choice(list(status_ids.values())),
                    random.choice(user_ids[:8])
                )
            )

        execute_values(
            cursor,
            """
            INSERT INTO tasks (
                title,
                description,
                status_id,
                user_id
            )
            VALUES %s
            """,
            tasks
        )

        connection.commit()

        print("Database seeded successfully")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    seed_database()