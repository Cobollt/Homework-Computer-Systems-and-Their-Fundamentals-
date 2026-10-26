from pymongo import MongoClient
from pymongo.errors import PyMongoError


MONGO_URL = "mongodb://localhost:27017/"

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client["cats_db"]
collection = db["cats"]


def check_connection():
    try:
        client.admin.command("ping")
        print("Підключення до MongoDB успішне")
        return True
    except PyMongoError as error:
        print(f"Помилка підключення до MongoDB: {error}")
        return False


def print_cat(cat):
    print(f"_id: {cat['_id']}")
    print(f"name: {cat['name']}")
    print(f"age: {cat['age']}")
    print(f"features: {cat['features']}")
    print()


def create_cat():
    try:
        name = input("Введіть ім'я кота: ").strip()

        if not name:
            print("Ім'я не може бути порожнім")
            return

        try:
            age = int(input("Введіть вік кота: "))
        except ValueError:
            print("Вік повинен бути цілим числом")
            return

        if age < 0:
            print("Вік не може бути від'ємним")
            return

        features_input = input(
            "Введіть характеристики через кому: "
        ).strip()

        features = [
            feature.strip()
            for feature in features_input.split(",")
            if feature.strip()
        ]

        cat = {
            "name": name,
            "age": age,
            "features": features
        }

        result = collection.insert_one(cat)

        print(
            f"Кота додано. ID: {result.inserted_id}"
        )

    except PyMongoError as error:
        print(f"Помилка створення запису: {error}")


def show_all_cats():
    try:
        cats = list(collection.find())

        if not cats:
            print("Колекція порожня")
            return

        for cat in cats:
            print_cat(cat)

    except PyMongoError as error:
        print(f"Помилка читання даних: {error}")


def find_cat_by_name():
    try:
        name = input("Введіть ім'я кота: ").strip()

        cat = collection.find_one(
            {"name": name}
        )

        if cat is None:
            print("Кота не знайдено")
            return

        print_cat(cat)

    except PyMongoError as error:
        print(f"Помилка пошуку: {error}")


def update_cat_age():
    try:
        name = input("Введіть ім'я кота: ").strip()

        try:
            age = int(
                input("Введіть новий вік: ")
            )
        except ValueError:
            print("Вік повинен бути цілим числом")
            return

        if age < 0:
            print("Вік не може бути від'ємним")
            return

        result = collection.update_one(
            {"name": name},
            {"$set": {"age": age}}
        )

        if result.matched_count == 0:
            print("Кота не знайдено")
        else:
            print("Вік кота оновлено")

    except PyMongoError as error:
        print(f"Помилка оновлення: {error}")


def add_cat_feature():
    try:
        name = input("Введіть ім'я кота: ").strip()

        feature = input(
            "Введіть нову характеристику: "
        ).strip()

        if not feature:
            print(
                "Характеристика не може бути порожньою"
            )
            return

        result = collection.update_one(
            {"name": name},
            {
                "$addToSet": {
                    "features": feature
                }
            }
        )

        if result.matched_count == 0:
            print("Кота не знайдено")
        else:
            print("Характеристику додано")

    except PyMongoError as error:
        print(f"Помилка оновлення: {error}")


def delete_cat_by_name():
    try:
        name = input("Введіть ім'я кота: ").strip()

        result = collection.delete_one(
            {"name": name}
        )

        if result.deleted_count == 0:
            print("Кота не знайдено")
        else:
            print("Запис видалено")

    except PyMongoError as error:
        print(f"Помилка видалення: {error}")


def delete_all_cats():
    try:
        confirmation = input(
            "Видалити всі записи? (yes/no): "
        ).strip().lower()

        if confirmation != "yes":
            print("Операцію скасовано")
            return

        result = collection.delete_many({})

        print(
            f"Видалено записів: "
            f"{result.deleted_count}"
        )

    except PyMongoError as error:
        print(f"Помилка видалення: {error}")


def show_menu():
    print()
    print("1. Додати кота")
    print("2. Показати всіх котів")
    print("3. Знайти кота за ім'ям")
    print("4. Оновити вік кота")
    print("5. Додати характеристику")
    print("6. Видалити кота")
    print("7. Видалити всіх котів")
    print("0. Вихід")
    print()


def main():
    if not check_connection():
        return

    while True:
        show_menu()

        choice = input(
            "Оберіть дію: "
        ).strip()

        if choice == "1":
            create_cat()
        elif choice == "2":
            show_all_cats()
        elif choice == "3":
            find_cat_by_name()
        elif choice == "4":
            update_cat_age()
        elif choice == "5":
            add_cat_feature()
        elif choice == "6":
            delete_cat_by_name()
        elif choice == "7":
            delete_all_cats()
        elif choice == "0":
            print("Роботу завершено")
            break
        else:
            print("Невірний вибір")

    client.close()


if __name__ == "__main__":
    main()