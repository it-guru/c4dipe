from .base import DataObj

class DataObjSQLDB(DataObj):
    def __init__(self):
        super().__init__()
#        self.db_connection_string = db_connection_string
        self.is_connected = False
#        print(f"init with connectstr {db_connection_string}.")
        
        self.records = {}

    def insert_record(self, record_id: int, data: dict) -> bool:
        if record_id in self.records:
            print(f"Fehler: Datensatz {record_id} existiert bereits.")
            return False

        self.records[record_id] = data
        print(f"Datensatz {record_id} erfolgreich eingefuegt.")
        return True

    def update_record(self, record_id: int, new_data: dict) -> bool:
        if record_id not in self.records:
            print(f"Fehler: Datensatz {record_id} nicht gefunden.")
            return False

        # Aktualisiert die Werte im Dictionary
        self.records[record_id].update(new_data)
        print(f"Datensatz {record_id} erfolgreich aktualisiert.")
        return True

    def delete_record(self, record_id: int) -> bool:
        if record_id not in self.records:
            print(f"Fehler: Datensatz {record_id} existiert nicht.")
            return False

        del self.records[record_id]
        print(f"Datensatz {record_id} erfolgreich geloescht.")
        return True

