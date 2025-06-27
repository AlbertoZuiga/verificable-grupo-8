from config import Config


def database_exists(cursor):
    cursor.execute(
        f"""
        SELECT SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE SCHEMA_NAME = '{Config.DB_NAME}';
        """
    )
    return cursor.fetchone()
