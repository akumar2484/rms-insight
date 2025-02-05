<script>
export default {
  data() {
    return {
      showPrintBuilder: false, // Toggles the modal
      availableColumns: [
        { label: "Name", key: "name" },
        { label: "Age", key: "age" },
        { label: "Email", key: "email" },
      ],
      selectedColumns: ["name", "email"], // Default selected columns
      customHeader: "",
      customFooter: "",
    };
  },
  methods: {
    generatePrintPreview() {
      // Get selected columns
      const filteredTableData = this.tableData.map((row) =>
        Object.fromEntries(
          Object.entries(row).filter(([key]) => this.selectedColumns.includes(key))
        )
      );

      // Build print content
      const printContent = `
        <div>
          <h3>${this.customHeader || "Table Report"}</h3>
          <table border="1" style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr>
                ${this.selectedColumns
                  .map(
                    (col) =>
                      `<th style="padding: 8px; text-align: left;">${this.getColumnLabel(
                        col
                      )}</th>`
                  )
                  .join("")}
              </tr>
            </thead>
            <tbody>
              ${filteredTableData
                .map(
                  (row) =>
                    `<tr>${this.selectedColumns
                      .map((col) => `<td style="padding: 8px;">${row[col]}</td>`)
                      .join("")}</tr>`
                )
                .join("")}
            </tbody>
          </table>
          <footer>${this.customFooter || ""}</footer>
        </div>
      `;

      // Open print preview
      const printWindow = window.open("", "_blank");
      printWindow.document.write(printContent);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    },
    getColumnLabel(key) {
      const column = this.availableColumns.find((col) => col.key === key);
      return column ? column.label : key;
    },
  },
};
</script>
