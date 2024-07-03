from codaio import Cell, Coda, Document

from app.config import config
from app.db.repos.arrival import ArrivalRepo
from app.schemas.feeder.arrival import Arrival, ArrivalResponse


if not config.TESTING:
    ARRIVALS = "grid--SMbvhP-1c"
else:
    ARRIVALS = "Arrivals"


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
        row_id = exist.coda_index
        if row_id:
            new_data = exist.model_dump()
            new_data.update(data.model_dump(exclude_none=True))
            new_row = [
                Cell(column=self.ArrivalMapping.badge, value_storage=new_data["badge"].hex),
                Cell(column=self.ArrivalMapping.status, value_storage=new_data["status"].value),
                Cell(column=self.ArrivalMapping.arrival_date, value_storage=new_data["arrival_date"].isoformat()),
                Cell(column=self.ArrivalMapping.arrival_transport, value_storage=new_data["arrival_transport"].value),
                Cell(column=self.ArrivalMapping.departure_date, value_storage=new_data["departure_date"].isoformat()),
                Cell(
                    column=self.ArrivalMapping.departure_transport, value_storage=new_data["departure_transport"].value
                ),
            ]

            result = self.arrivals.update_row(row_id, new_row)
            coda_index = result.get('id')
        else:
            new_row = [
                Cell(column=self.ArrivalMapping.badge, value_storage=data.badge_id.hex),
                Cell(column=self.ArrivalMapping.status, value_storage=data.status.value),
                Cell(column=self.ArrivalMapping.arrival_date, value_storage=data.arrival_date.isoformat()),
                Cell(column=self.ArrivalMapping.arrival_transport, value_storage=data.arrival_transport.value),
                Cell(column=self.ArrivalMapping.departure_date, value_storage=data.departure_date.isoformat()),
                Cell(column=self.ArrivalMapping.departure_transport, value_storage=data.departure_transport.value),
            ]
            result = self.arrivals.upsert_row(new_row)
            coda_index = result.get('addedRowIds')[0]
        return coda_index

    async def delete_arrival(self, coda_index):
        self.arrivals.delete_row_by_id(coda_index)