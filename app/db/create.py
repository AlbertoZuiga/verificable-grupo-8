import pymysql

from app.db.utils import database_exists
from config import Config


def create_database():
    conn = pymysql.connect(host=Config.DB_HOST, user=Config.DB_USER, password=Config.DB_PASSWORD)
    cursor = conn.cursor()
    print("Creando base de datos...")

    result = database_exists(cursor)

    if result:
        print(f"Base de datos '{Config.DB_NAME}' ya existe.\n")
    else:
        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
            """
        )
        print(f"Base de datos '{Config.DB_NAME}' creada.\n")

    conn.close()


if __name__ == "__main__":
    create_database()
