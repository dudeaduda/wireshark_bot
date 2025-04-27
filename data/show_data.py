import sqlite3
import json
from tabulate import tabulate

def fetch_user_progress(db_path="data/user_progress.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_progress")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    # Преобразование JSON в читаемый список
    readable_rows = []
    for row in rows:
        row = list(row)
        try:
            idx = column_names.index("completed_modules")
            row[idx] = json.loads(row[idx]) if row[idx] else []
        except:
            pass
        readable_rows.append(row)

    conn.close()
    return column_names, readable_rows

if __name__ == "__main__":
    headers, data = fetch_user_progress()
    print(tabulate(data, headers=headers, tablefmt="grid"))
