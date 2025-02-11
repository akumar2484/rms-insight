# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InsightsView(Document):
    def on_update(self):
        if not self.columns:
            self.update_columns()

    @frappe.whitelist()
    def sync_table(self):
        """Sync the data source with the view's table"""
        source = frappe.get_doc("Insights Data Source", self.data_source)
        source.sync_tables([self.table], force=True)

    @frappe.whitelist()
    def update_visibility(self, hidden):
        """Update visibility of the view"""
        self.hidden = hidden
        self.save()

    @frappe.whitelist()
    def get_preview(self):
        """Preview the first rows of the table data"""
        if self.is_query_based:
            return []
        data_source = frappe.get_doc("Insights Data Source", self.data_source)
        return data_source.get_table_preview(self.view)

    def get_columns(self):
        """Fetch and return the columns for this insights view"""
        if not self.columns:
            self.update_columns()
        return self.columns

    def update_columns(self):
        """Update the columns for the view based on the data source"""
        if self.is_query_based:
            return
        data_source = frappe.get_doc("Insights Data Source", self.data_source)
        if columns := data_source.get_table_columns(self.table):
            self.columns = []
            for column in columns:
                self.append(
                    "columns",
                    {
                        "column": column.get("column"),
                        "label": column.get("label"),
                        "type": column.get("type"),
                    },
                )

    @frappe.whitelist()
    def update_column_type(self, column, newtype):
        """Allow column type change in the view"""
        for col in self.columns:
            if col.column == column and col.type != newtype:
                col.type = newtype
                break
        self.save()

def on_doctype_update():
    """Create an index on `data_source` and `table` for faster lookup"""
    fields = ["data_source", "table"]
    if frappe.db.db_type == "mariadb":
        fields = ["`data_source`", "`table`"]
    frappe.db.add_index("Insights View", fields, "data_source_table_index")

