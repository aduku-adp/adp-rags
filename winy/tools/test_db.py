import logging
import os

import psycopg2

logger = logging.getLogger(__name__)

PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", 5432),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "postgres"),
    "dbname": os.getenv("PG_NAME", "wine_db"),
}

with psycopg2.connect(**PG_CONFIG) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT wine FROM wine_links")
        result = cursor.fetchall()
        wine_names = [row[0] for row in result]
        logger.info(wine_names)
        print(wine_names)
