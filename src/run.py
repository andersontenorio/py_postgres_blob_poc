import sys
import os
import pickle

import psycopg2
import numpy as np
from sklearn.linear_model import LinearRegression


queue_id = "1000"


def run():
    create_table()
    insert_model()
    select_model()


def create_table():
    print("CREATING TABLE IF NOT EXISTS...")
    try:
        conn = psycopg2.connect(database="python_serialization", user="user", password="password", host="localhost",
                                port="6432")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS models (queue_id varchar(10) NOT NULL, model BYTEA);")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        sys.exit(error)

    finally:
        cur.close()
        conn.close()


def insert_model():
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3

    print("TRAINING MODEL...")
    model = LinearRegression().fit(X, y)

    print("SAVING MODEL")
    pickle.dump(model, open("model.pkl", 'wb'))

    print("INSERTING MODEL...")
    try:
        conn = psycopg2.connect(database="python_serialization", user="user", password="password", host="localhost",
                                port="6432")
        cur = conn.cursor()

        dumped_model = open("model.pkl", 'rb').read()

        cur.execute("INSERT INTO models (queue_id, model) " +
                    "VALUES (%s, %s)",
                    (queue_id, psycopg2.Binary(dumped_model)))

        conn.commit()
        count = cur.rowcount
        print(count, "MODEL INSERTED SUCCESSFULLY")

        print("DELETING FILE...")
        if os.path.exists("model.pkl"):
            os.remove("model.pkl")

    except (Exception, psycopg2.DatabaseError) as error:
        sys.exit(error)

    finally:
        cur.close()
        conn.close()


def select_model():
    print("SELECTING MODEL...")
    try:
        conn = psycopg2.connect(database="python_serialization", user="user", password="password", host="localhost",
                                port="6432")
        cur = conn.cursor()

        cur.execute("SELECT model " +
                    "FROM models " +
                    "WHERE queue_id = %s",
                    (queue_id,))

        blob = cur.fetchone()
        open("model.pkl", 'wb').write(blob[0])
        loaded_model = pickle.load(open("model.pkl", 'rb'))
        print("PREDICTIONS: " + str(loaded_model.predict(np.array([[3, 5]]))))

    except (Exception, psycopg2.DatabaseError) as error:
        sys.exit(error)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run()
