# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import cint

from insights.insights.doctype.insights_data_source.sources.query_store import (
    remove_stored_query,
)
from insights.insights.doctype.insights_query.insights_assisted_query import (
    DEFAULT_JSON,
)
from insights.insights.doctype.insights_query.patches.migrate_old_query_to_new_query_structure import (
    convert_classic_to_assisted,
)
from frappe.utils.pdf import get_pdf
from datetime import datetime

class InsightsQueryClient:
    @frappe.whitelist()
    def set_status(self, status):
        # since status is auto set based on the sql, we need some way to override it
        self.db_set("status", status)

    @frappe.whitelist()
    def duplicate(self):
        new_query = frappe.copy_doc(self)
        new_query.save()
        return new_query.name

    @frappe.whitelist()
    def add_transform(self, type, options):
        existing = self.get("transforms", {"type": type})
        if existing:
            existing[0].options = frappe.as_json(options)
        else:
            self.append(
                "transforms",
                {
                    "type": type,
                    "options": frappe.as_json(options),
                },
            )
        self.run()

    @frappe.whitelist()
    def reset_transforms(self):
        self.transforms = []
        self.run()

    @frappe.whitelist()
    def set_limit(self, limit):
        validated_limit = cint(limit)
        if not validated_limit or validated_limit < 0:
            frappe.throw("Limit must be a positive integer")
        self.limit = validated_limit
        self.save()

    @frappe.whitelist()
    def run(self):
        self.fetch_results()
        self.save()

    @frappe.whitelist()
    def reset_and_save(self):
        self.reset()
        self.save()

    @frappe.whitelist()
    def store(self):
        self.is_stored = 1
        self.save()

    @frappe.whitelist()
    def unstore(self):
        remove_stored_query(self)
        self.is_stored = 0
        self.save()

    @frappe.whitelist()
    def convert(self):
        self.is_native_query = not self.is_native_query
        self.save()

    @frappe.whitelist()
    def convert_to_native(self):
        if self.is_native_query:
            return
        self.is_native_query = 1
        self.save()

    @frappe.whitelist()
    def convert_to_assisted(self):
        if self.is_assisted_query:
            return
        self.is_assisted_query = 1
        self.save()

    @frappe.whitelist()
    def save_as_table(self):
        return self.update_insights_table(force=True)

    @frappe.whitelist()
    def delete_linked_table(self):
        return self.delete_insights_table()

    @frappe.whitelist()
    def switch_query_type(self):
        if self.is_assisted_query:
            self.is_assisted_query = 0
        else:
            self.is_native_query = 0
            self.is_script_query = 0
            self.is_assisted_query = 1
            self.json = convert_classic_to_assisted(self) or self.json
        self.save()

    @frappe.whitelist()
    def fetch_related_tables_columns(self, search_txt=None):
        if not self.is_assisted_query:
            return []
        if search_txt and not isinstance(search_txt, str):
            frappe.throw("Search query must be a string")

        tables = self.variant_controller.get_selected_tables()
        table_names = [table["table"] for table in tables if table["table"]]
        if not table_names:
            return []

        related_table_names = get_related_table_names(table_names, self.data_source)
        selected_table_cols = get_matching_columns_from(table_names, self.data_source, search_txt)
        related_table_cols = get_matching_columns_from(
            related_table_names, self.data_source, search_txt
        )
        columns = []
        for col in selected_table_cols + related_table_cols:
            col_added = any(
                col["column"] == column["column"] and col["table"] == column["table"]
                for column in columns
            )
            if col_added:
                continue
            columns.append(
                {
                    "column": col.column,
                    "label": col.label,
                    "type": col.type,
                    "table": col.table,
                    "table_label": col.table_label,
                    "data_source": col.data_source,
                }
            )

        return columns
    
    @frappe.whitelist()
    def fetch_related_views_columns(self, search_txt=None,type=None):
        if not self.is_assisted_query:
            return []
        if search_txt and not isinstance(search_txt, str):
            frappe.throw("Search query must be a string")

        tables = self.variant_controller.get_selected_tables()
        table_names = [table["table"] for table in tables if table["table"]]
        if not table_names:
            return []
        
        related_table_names = get_related_view_names(table_names, self.data_source)
        selected_table_cols = get_matching_view_columns_from(table_names, self.data_source, search_txt)
        related_table_cols = get_matching_view_columns_from(
            related_table_names, self.data_source, search_txt
        )
        columns = []
        for col in selected_table_cols + related_table_cols:
            col_added = any(
                col["column"] == column["column"] and col["view"] == column["table"]
                for column in columns
            )
            if col_added:
                continue
            columns.append(
                {
                    "column": col.column,
                    "label": col.label,
                    "type": col.type,
                    "table": col.view,
                    "table_label": col.view_label,
                    "data_source": col.data_source,
                }
            )

        return columns
     
    @frappe.whitelist()
    def download_pdf(self,result=None):
        # Get current date and time dynamically
        current_date = datetime.now().strftime('%m/%d/%Y')
        current_time = datetime.now().strftime('%H:%M:%S')
        query = "SELECT * FROM [vw_HREmployeeMaster] WHERE [EmployeeNumber] = '332'"
        result = self.execute_query(query)
        columns = [item['label'] for item in result[0]]
        formatted_data = []
        for row in result[1:]:
         row_data = dict(zip(columns, row))  # Pair column headers with values
         formatted_data.append(row_data)
        # Dynamic title for the report
        report_title = "HR - Employee Master"  # This can be dynamic too
        # Render the HTML content with the dynamic values (we don’t include page numbers here)
        html_content = frappe.render_template(
            "insights/templates/report_pdf_template.html", 
            {
                "current_date": current_date,
                "current_time": current_time,
                "report_title": report_title,
                "formatted_data": formatted_data
            }
        )
        # Convert HTML to PDF
        pdf_data = get_pdf(html_content, options={
        'header-left': f'Date: {current_date}\nTime: {current_time}',  # Left side with date and time in different lines
        'header-right': 'Page [page] of [topage] \n Katalyst',  # Right side with company name and page number
        'no-outline': None,
        'disable-smart-shrinking': None,
        'page-size': 'A4',  # Page size
        'disable-javascript': None,
        'header-spacing': '0',  # Ensuring header-spacing is zero so that it doesn't override
        'header-font-size':9
    })

        return pdf_data
    
def get_related_table_names(table_names, data_source):
    insights_table = frappe.qb.DocType("Insights Table")
    insights_table_link = frappe.qb.DocType("Insights Table Link")

    referenced_tables = (
        frappe.qb.from_(insights_table)
        .left_join(insights_table_link)
        .on(insights_table.name == insights_table_link.parent)
        .where(
            (insights_table.data_source == data_source) & (insights_table.table.isin(table_names))
        )
        .select(insights_table_link.foreign_table)
        .groupby(insights_table_link.foreign_table)
        .run(pluck=True)
    )
    referencing_tables = (
        frappe.qb.from_(insights_table)
        .left_join(insights_table_link)
        .on(insights_table.name == insights_table_link.parent)
        .where(
            (insights_table.data_source == data_source)
            & (insights_table_link.foreign_table.isin(table_names))
        )
        .select(insights_table.table)
        .groupby(insights_table.table)
        .run(pluck=True)
    )

    return list(set(referenced_tables + referencing_tables) - set(table_names))

# added
def get_related_view_names(table_names, data_source):
    insights_view = frappe.qb.DocType("Insights View")
    insights_table_link = frappe.qb.DocType("Insights Table Link")

    referenced_tables = (
        frappe.qb.from_(insights_view)
        .left_join(insights_table_link)
        .on(insights_view.name == insights_table_link.parent)
        .where(
            (insights_view.data_source == data_source) & (insights_view.table.isin(table_names))
        )
        .select(insights_table_link.foreign_table)
        .groupby(insights_table_link.foreign_table)
        .run(pluck=True)
    )
    referencing_tables = (
        frappe.qb.from_(insights_view)
        .left_join(insights_table_link)
        .on(insights_view.name == insights_table_link.parent)
        .where(
            (insights_view.data_source == data_source)
            & (insights_table_link.foreign_table.isin(table_names))
        )
        .select(insights_view.view)
        .groupby(insights_view.view)
        .run(pluck=True)
    )

    return list(set(referenced_tables + referencing_tables) - set(table_names))


def get_matching_columns_from(tables, data_source, search_txt=None, limit=200):
    if not tables:
        return []
    if not search_txt or not isinstance(search_txt, str):
        search_txt = ""

    insights_table = frappe.qb.DocType("Insights Table")
    insights_table_column = frappe.qb.DocType("Insights Table Column")
    fields_to_select = [
        insights_table_column.column,
        insights_table_column.label,
        insights_table_column.type,
        insights_table.table,
        insights_table.data_source,
        insights_table.label.as_("table_label"),
    ]

    search_cond = insights_table.name.isnotnull()
    if search_txt:
        column_matches = insights_table_column.column.like(f"%{search_txt}%")
        label_matches = insights_table_column.label.like(f"%{search_txt}%")
        search_cond = column_matches | label_matches
    return (
        frappe.qb.from_(insights_table)
        .left_join(insights_table_column)
        .on(insights_table.name == insights_table_column.parent)
        .select(*fields_to_select)
        .where(
            (insights_table.data_source == data_source)
            & insights_table.table.isin(tables)
            & (search_cond)
        )
        .groupby(insights_table.table, insights_table_column.column)
        .limit(limit)
        .run(as_dict=True)
    )

# added
def get_matching_view_columns_from(tables, data_source, search_txt=None, limit=200):
    if not tables:
        return []
    
    if not search_txt or not isinstance(search_txt, str):
        search_txt = ""

    insights_view = frappe.qb.DocType("Insights View")
    insights_view_column = frappe.qb.DocType("Insights Table Column")  # Assuming correct table
    fields_to_select = [
        insights_view_column.column,
        insights_view_column.label,
        insights_view_column.type,
        insights_view.view,
        insights_view.data_source,
        insights_view.label.as_("view_label"),
    ]

    # Search condition
    search_cond = insights_view_column.column.like(f"%{search_txt}%") | insights_view_column.label.like(f"%{search_txt}%")

    return (
        frappe.qb.from_(insights_view)
        .left_join(insights_view_column)
        .on(insights_view.name == insights_view_column.parent)
        .select(*fields_to_select)
        .where(
            (insights_view.data_source == data_source)
            & insights_view.view.isin(tables)  # Fixing table column reference
            & search_cond
        )
        .groupby(insights_view.view, insights_view_column.column)
        .limit(limit)
        .run(as_dict=True)
    )