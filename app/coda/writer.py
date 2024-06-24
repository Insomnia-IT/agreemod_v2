from codaio import Cell, Coda, Document

from app.db.repos.arrival import ArrivalRepo
from app.models.arrival import Arrival
from app.schemas.feeder.arrival import ArrivalResponse


ARRIVALS = "grid--SMbvhP-1c"


class CodaWriter:
    class ArrivalMapping:
        badge = "c-98ZAsW_Ihv"
        status = "c-rQDeCNsfuB"
        arrival_date = "c-aFMNg5JucD"
        arrival_transport = "c-BgCQgCkVJi"
        departure_date = "c-lnrpyyjzVO"
        departure_transport = "c-eqJEucEFRi"

    def __init__(self, api_key: str, doc_id: str) -> None:
        coda = Coda(api_key)
        self.doc = Document(doc_id, coda=coda)
        self.arrivals = self.doc.get_table(ARRIVALS)

    async def update_arrival(self, repo: ArrivalRepo, data: ArrivalResponse):
        exist: Arrival = await repo.retrieve(data.id)
        if exist:
            row_id = exist.coda_index
            new_data = exist.model_dump().update(data.model_dump(exclude_none=True))
            new_row = [
                Cell(column=self.ArrivalMapping.badge, value_storage=new_data["badge"]),
                Cell(column=self.ArrivalMapping.status, value_storage=new_data["status"].value),
                Cell(column=self.ArrivalMapping.arrival_date, value_storage=new_data["arrival_date"]),
                Cell(column=self.ArrivalMapping.arrival_transport, value_storage=new_data["arrival_transport"].value),
                Cell(column=self.ArrivalMapping.departure_date, value_storage=new_data["departure_date"]),
                Cell(
                    column=self.ArrivalMapping.departure_transport, value_storage=new_data["departure_transport"].value
                ),
            ]

            result = self.arrivals.update_row(row_id, new_row)
            coda_index = result.get('id')
        else:
            new_row = [
                Cell(column=self.ArrivalMapping.badge, value_storage=data.badge),
                Cell(column=self.ArrivalMapping.status, value_storage=data.status.value),
                Cell(column=self.ArrivalMapping.arrival_date, value_storage=data.arrival_date),
                Cell(column=self.ArrivalMapping.arrival_transport, value_storage=data.arrival_transport.value),
                Cell(column=self.ArrivalMapping.departure_date, value_storage=data.departure_date),
                Cell(column=self.ArrivalMapping.departure_transport, value_storage=data.departure_transport.value),
            ]
            result = self.arrivals.upsert_row(new_row)
            coda_index = result.get('addedRowIds')[0]
        return coda_index
