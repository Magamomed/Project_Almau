from docx import Document

def extract_tables_from_docx(docx_path):
    document = Document(docx_path)
    tables_data = []

    for table in document.tables:
        table_rows = []
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            table_rows.append(row_data)
        tables_data.append(table_rows)

    return tables_data