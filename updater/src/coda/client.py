from codaio import Coda, Document, Row


class CodaClient:
    def __init__(self, api_key: str, doc_id: str) -> None:
        coda = Coda(api_key)
        self.doc = Document(doc_id, coda=coda)

    def list_tables(self):
        return self.doc.list_tables()

    def get_table(self, table_id: str, object: bool = False):
        def row_to_dict(row: Row):
            row_dict = row.to_dict()
            row_dict.update({"id": row.index})
            return row_dict

        table = self.doc.get_table(table_id)
        return table if object else [row_to_dict(x) for x in table.rows()]
