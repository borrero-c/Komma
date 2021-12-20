import psycopg2
import pandas as pd
import psycopg2.extras as extras

def insert_rows(conn, table, df):
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))

    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)

    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        row_len = len(tuples)

        print("inserted " + str(row_len) + " rows into " + table)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()

    cursor.close()


