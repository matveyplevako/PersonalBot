from sqlalchemy import create_engine
import os

link = os.environ['DATABASE_URL']
conn = create_engine(link)


class DB:

    def __init__(self, table_name, **kwargs):
        self.table_name = table_name
        self.fields = kwargs
        columns = ", ".join([arg + " " + arg_type for (arg, arg_type) in kwargs.items()])
        request = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        conn.execute(request)

    def add_item(self, **kwargs):
        columns = " AND ".join([arg + " = " + f"'{arg_value}'" for (arg, arg_value) in kwargs.items()])
        request = f"SELECT COUNT(*) FROM {self.table_name} WHERE {columns}"
        count = conn.execute(request)
        count = list(count)[0][0]
        if count != 0:
            return False

        order = list(kwargs.keys())
        columns_to_choose = ', '.join(order)
        values = [f"'{kwargs[arg]}'" for arg in order]
        values = ', '.join(values)
        request = f"INSERT INTO {self.table_name} ({columns_to_choose}) VALUES ({values})"
        conn.execute(request)
        return True

    def delete_item(self, **kwargs):
        columns = " AND ".join([arg + " = " + f"'{arg_value}'" for (arg, arg_value) in kwargs.items()])
        request = f"DELETE FROM {self.table_name} WHERE {columns}"
        conn.execute(request)

    def get_items(self, **kwargs):
        columns = " AND ".join([arg + " = " + f"'{arg_value}'" for (arg, arg_value) in kwargs.items()])
        request = f"SELECT * FROM {self.table_name} WHERE {columns}"
        return [x for x in conn.execute(request)]

    def get_all_rows(self):
        request = f"SELECT * FROM {self.table_name}"
        return [x for x in conn.execute(request)]
