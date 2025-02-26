import re
import frappe
from sqlalchemy import column as Column
from sqlalchemy import inspect
from sqlalchemy import select as Select
from sqlalchemy import table as Table
from sqlalchemy.engine.base import Connection
import pyodbc
from insights.insights.query_builders.mssql.builder import MSSQLQueryBuilder

from .base_database import BaseDatabase
from .utils import create_insights_table, create_insights_view, get_sqlalchemy_engine

IGNORED_TABLES = ["__.*"]

MSSQL_TO_GENERIC_TYPES = {
    "int": "Integer",
    "bigint": "Long Int",
    "decimal": "Decimal",
    "nvarchar": "String",
    "varchar": "String",
    "date": "Date",
    "datetime": "Datetime",
    "time": "Time",
    "text": "Text",
    "bit": "Boolean",  # Change to Boolean for MSSQL
}


class MSSQLTableFactory:
    """Fetches tables and columns from database and links from doctype"""

    def __init__(self, data_source) -> None:
        self.db_conn: Connection
        self.data_source = data_source

    def sync_tables(self, connection, tables, force=False):
        self.db_conn = connection
        for table in self.get_tables(table_names=tables):
            # when force is true, it will overwrite the existing columns & links
            create_insights_table(table, force=force)

    def sync_views(self, connection, views, force=False):
        self.db_conn = connection
        for view in self.get_views(view_names=views):
            # When force is true, it will overwrite the existing columns & links
            create_insights_view(view, force=force)


    def get_tables(self, table_names=None):
        tables = []
        for table in self.get_db_tables(table_names):
            table.columns = self.get_table_columns(table.table)
            # TODO: process foreign keys as links
            tables.append(table)
        return tables

    def get_views(self, view_names=None):
        views = []
        for view in self.get_db_views(view_names):
            view_obj = frappe._dict({
                "view": view,
                "label": frappe.unscrub(view),
                "data_source": self.data_source,
            })
            view_obj.columns = self.get_view_columns(view_obj.view)
            views.append(view_obj)
        return views

    def get_db_tables(self, table_names=None):
        inspector = inspect(self.db_conn)
        # Retrieve all regular table names
        tables = set(inspector.get_table_names())
        # Retrieve foreign key information and collect foreign tables
        foreign_tables = set()
        for table in tables:
            # Get foreign keys of the current table
            foreign_keys = inspector.get_foreign_keys(table)
            # Add the referred tables from the foreign keys
            for fk in foreign_keys:
                referred_table = fk.get('referred_table')
                if referred_table:
                    foreign_tables.add(referred_table)
        # Combine regular tables and foreign tables
        all_tables = tables | foreign_tables
        if table_names:
            all_tables = {table for table in all_tables if table in table_names}
        return [self.get_table(table) for table in all_tables if not self.should_ignore(table)]

    def get_db_views(self, view_names=None):
        inspector = inspect(self.db_conn)
        views = set(inspector.get_view_names())
        if view_names:
            views = {view for view in views if view in view_names}
        return views

    def should_ignore(self, table_name):
        return any(re.match(pattern, table_name) for pattern in IGNORED_TABLES)

    def get_table(self, table_name):
        return frappe._dict({
            "table": table_name,
            "label": frappe.unscrub(table_name),
            "data_source": self.data_source,
        })
    
    def get_view(self, view_name):
        return frappe._dict({
            "view": view_name,
            "label": frappe.unscrub(view_name),
            "data_source": self.data_source,
        })

    def get_all_columns(self):
        inspector = inspect(self.db_conn)
        tables = inspector.get_table_names()
        columns_by_table = {}
        for table in tables:
            columns = inspector.get_columns(table)
            for col in columns:
                columns_by_table.setdefault(table, []).append(self.get_column(col["name"], col["type"]))
        return columns_by_table

    def get_all_view_columns(self):
        inspector = inspect(self.db_conn)
        views = inspector.get_view_names()
        columns_by_view = {}
        for view in views:
            columns = inspector.get_columns(view)
            for col in columns:
                columns_by_view.setdefault(view, []).append(self.get_view_column(col["name"], col["type"]))
        return columns_by_view

    def get_table_columns(self, table):
        if not hasattr(self, "_all_columns") or not self._all_columns:
            self._all_columns = self.get_all_columns()
        return self._all_columns.get(table, [])

    def get_view_columns(self, view):
        if not hasattr(self, "_all_view_columns") or not self._all_view_columns:
         self._all_view_columns = self.get_all_view_columns()  # Fetch view columns properly
        return self._all_view_columns.get(view, [])

    def get_column(self, column_name, column_type):
        return frappe._dict({
            "column": column_name,
            "label": frappe.unscrub(column_name),
            "type": MSSQL_TO_GENERIC_TYPES.get(str(column_type), "String"),
        })

    def get_view_column(self, column_name, column_type):
        return frappe._dict({
            "column": column_name,
            "label": frappe.unscrub(column_name),
            "type": MSSQL_TO_GENERIC_TYPES.get(str(column_type), "String"),
        })


class MSSQLDatabase(BaseDatabase):
    def __init__(self, **kwargs):
        connect_args = {"connect_timeout": 1}
        self.data_source = kwargs.pop("data_source")
        if connection_string := kwargs.pop("connection_string", None):
            self.engine = get_sqlalchemy_engine(
                connection_string=connection_string, connect_args=connect_args
            )
        else:
            self.engine = get_sqlalchemy_engine(
                dialect="mssql",
                driver="pyodbc{ODBC Driver 17 for SQL Server}",
                username=kwargs.pop("username"),
                password=kwargs.pop("password"),
                database=kwargs.pop("database_name"),
                host=kwargs.pop("host"),
                port=kwargs.pop("port"),
                connect_args=connect_args,
            )
        self.query_builder: MSSQLQueryBuilder = MSSQLQueryBuilder(self.engine)
        self.table_factory: MSSQLTableFactory = MSSQLTableFactory(self.data_source)

    def sync_tables(self, tables=None, force=False):
        with self.engine.begin() as connection:
            self.table_factory.sync_tables(connection, tables, force)

    def sync_views(self, views=None, force=False):
        with self.engine.begin() as connection:
            self.table_factory.sync_views(connection, views, force)

    def get_table_preview(self, table, limit=100):
        data = self.execute_query(f"""SELECT TOP {limit} * FROM [{table}]""", cached=True)
        # length = self.execute_query(f'''SELECT COUNT(*) FROM [{table}]''', cached=True)[0][0]
        length = self.execute_query(f'SELECT COUNT(*) AS total_count FROM [{table}]', cached=True)[0][0]
        return {
            "data": data or [],
            "length": length or 0,
        }
    def get_table_preview_with_filter(self, table, column=None,value=None):
        data = self.execute_query(f"SELECT * FROM [{table}] WHERE [{column}] = '{value}'", cached=True)
        length = self.execute_query(f"SELECT COUNT(*) AS total_count FROM [{table}] WHERE [{column}] = '{value}'", cached=True)[0][0]
        return {
            "data": data or [],
            "length": length or 0,
        }

    def get_table_columns(self, table):
        with self.connect() as connection:
            self.table_factory.db_conn = connection
            return self.table_factory.get_table_columns(table)

    def get_column_options(self, table, column, search_text=None, limit=50):
        query = Select(Column(column)).select_from(Table(table)).distinct().limit(limit)
        if search_text:
            query = query.where(Column(column).like(f"%{search_text}%"))
        query = self.compile_query(query)
        return self.execute_query(query, pluck=True)

    def get_view_columns(self, view):
        with self.connect() as connection:
            self.table_factory.db_conn = connection
            return self.table_factory.get_view_columns(view)

