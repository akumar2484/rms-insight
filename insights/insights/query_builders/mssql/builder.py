from sqlalchemy import Column
from sqlalchemy.sql import func, literal

from ..sql_builder import ColumnFormatter, Functions, SQLQueryBuilder


class MSSQLColumnFormatter(ColumnFormatter):
    @classmethod
    def format_date(cls, format, column: Column):
        match format:
            case "Minute":
                return func.format(column, 'yyyy-MM-dd HH:mm')
            case "Hour":
                return func.format(column, 'yyyy-MM-dd HH:00')
            case "Day" | "Day Short":
                return func.format(column, 'yyyy-MM-dd 00:00')
            case "Week":
                return func.dateadd(literal('day'), -func.datepart(literal('dw'), column) + 1, column)
            case "Month" | "Mon":
                return func.format(column, 'yyyy-MM-01')
            case "Year":
                return func.format(column, 'yyyy-01-01')
            case "Minute of Hour":
                return func.format(column, 'mm')
            case "Hour of Day":
                return func.format(column, 'HH')
            case "Day of Week":
                return func.format(column, 'dddd')
            case "Day of Month":
                return func.format(column, 'dd')
            case "Day of Year":
                return func.format(column, 'ddd')
            case "Month of Year":
                return func.format(column, 'MM')
            case "Quarter of Year":
                return func.datepart(literal('quarter'), column)
            case "Quarter":
                return func.datefromparts(
                    func.year(column),
                    (func.datepart(literal('quarter'), column) * 3) - 2,
                    1
                )
            case _:
                return func.format(column, format)


class MSSQLQueryBuilder(SQLQueryBuilder):
    def __init__(self, engine):
        super().__init__(engine)
        self.engine = engine
        self.functions = Functions
        self.column_formatter = MSSQLColumnFormatter
