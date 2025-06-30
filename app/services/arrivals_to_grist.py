import logging
import asyncio
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import json
import urllib.parse

import aiohttp
from app.config import config
from app.models.arrival import Arrival
from app.schemas.feeder.arrival import ArrivalWithMetadata

logger = logging.getLogger(__name__)

class GristArrivalWriter:
    def __init__(self):
        self.server = config.grist.server
        self.doc_id = config.grist.doc_id
        self.api_key = config.grist.api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _date_to_timestamp(self, date_obj):
        """Convert datetime.date to Unix timestamp"""
        if not date_obj:
            return None
        return int(datetime.combine(date_obj, datetime.min.time()).timestamp())

    async def find_badge_id_by_uuid(self, badge_uuid: UUID) -> Optional[int]:
        """Find badge ID in Grist by its UUID (no dashes)"""
        try:
            uuid_no_dashes = str(badge_uuid).replace('-', '')
            filter_obj = {"UUID": [uuid_no_dashes]}
            filter_param = urllib.parse.quote(json.dumps(filter_obj))
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025/records?filter={filter_param}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching badges: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching badges: {resp.status} - {error_text}")
                    records = await resp.json()
                    badge_record = records.get('records', [None])[0] if records.get('records') else None
                    if badge_record:
                        return badge_record['id']
                    return None
        except Exception as e:
            logger.error(f"Error finding badge in Grist: {e}")
            raise

    async def update_arrival(self, arrival_tuple: Tuple[ArrivalWithMetadata, set]):
        """Update or create a arrival in Grist"""
        arrival, present_fields = arrival_tuple
        logger.info(f"Working on arrival:{arrival}")
        if arrival.data.id is None:
            return False
        try:
            corresponding_badge_id = None
            # Find corresponding badge ID in Grist
            if arrival.data.badge_id:
                corresponding_badge_id = await self.find_badge_id_by_uuid(arrival.data.badge_id) if arrival.data.badge_id else None
                if not corresponding_badge_id:
                    logger.error(f"Could not find corresponding badge in Grist for arrival {arrival.data.id}")
                    raise Exception(f"Badge not found in Grist for arrival {arrival.data.id}")

            # Prepare the arrival data for Grist
            fields = {}
            
            # Only include fields that were present in the original data
            if 'status' in present_fields:
                fields["status"] = arrival.data.status.value if arrival.data.status else None
            if 'arrival_date' in present_fields:
                fields["arrival_date"] = self._date_to_timestamp(arrival.data.arrival_date)
            if 'arrival_transport' in present_fields:
                fields["arrival_transport"] = arrival.data.arrival_transport.value if arrival.data.arrival_transport else None
            if 'departure_date' in present_fields:
                fields["departure_date"] = self._date_to_timestamp(arrival.data.departure_date)
            if 'departure_transport' in present_fields:
                fields["departure_transport"] = arrival.data.departure_transport.value if arrival.data.departure_transport else None
            if 'badge_id' in present_fields:
                fields["badge"] = corresponding_badge_id
            if 'deleted' in present_fields and arrival.data.deleted:
                fields["to_delete"] = self._date_to_timestamp(datetime.now())
                fields["delete_reason"] = f"FEEDER: deleted"
            elif 'deleted' in present_fields and arrival.data.deleted == False:
                fields["to_delete"] = None
                fields["delete_reason"] = None

            grist_data = {
                "records": [{
                    "fields": fields
                }]
            }
            print(arrival)
            print(grist_data)

            # Check if arrival exists in Grist
            uuid_no_dashes = str(arrival.data.id).replace('-', '')
            filter_obj = {"UUID": [uuid_no_dashes]}
            filter_param = urllib.parse.quote(json.dumps(filter_obj))
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Arrivals_2025/records?filter={filter_param}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching arrivals: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching arrivals: {resp.status} - {error_text}")
                    records = await resp.json()
                    existing_arrival = records.get('records', [None])[0] if records.get('records') else None
                if existing_arrival:
                    # Check if 'to_delete' is set in Grist
                    if existing_arrival["fields"].get("to_delete") is not None:
                        logger.info(f"Updating existing arrival with restored data from postgres")
                        from database.meta import async_session
                        from app.db.repos.arrival import ArrivalRepo
                        async with async_session() as db_session:
                            repo = ArrivalRepo(db_session)
                            db_arrival = await repo.retrieve(id=arrival.data.id, include_badge=True)
                            if db_arrival:
                                # Map all fields from db_arrival to fields for Grist
                                restored_fields = {
                                    "status": db_arrival.status.value if db_arrival.status else None,
                                    "arrival_date": self._date_to_timestamp(db_arrival.arrival_date) if db_arrival.arrival_date else None,
                                    "arrival_transport": db_arrival.arrival_transport.value if db_arrival.arrival_transport else None,
                                    "departure_date": self._date_to_timestamp(db_arrival.departure_date) if db_arrival.departure_date else None,
                                    "departure_transport": db_arrival.departure_transport.value if db_arrival.departure_transport else None,
                                    "badge": await self.find_badge_id_by_uuid(db_arrival.badge.id) if hasattr(db_arrival.badge, 'id') else None,
                                }
                                # Then, overlay with the fields from the original request
                                restored_fields.update(fields)

                                grist_data["records"][0]["fields"] = restored_fields
                                grist_data["records"][0]["id"] = existing_arrival["id"]
                                update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Arrivals_2025_copy/records"
                                async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                                    if resp.status != 200:
                                        error_text = await resp.text()
                                        logger.error(f"Error updating arrival: {resp.status} - {error_text}")
                                        raise Exception(f"Error updating arrival: {resp.status} - {error_text}")
                                logger.info(f"Successfully restored arrival {arrival.data.id} from DB to Grist")
                                return False
                    # Update existing arrival
                    grist_data["records"][0]["id"] = existing_arrival["id"]
                    logger.info(f"Updating existing arrival")
                    logger.info(grist_data)
                    update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Arrivals_2025/records"
                    async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error updating arrival: {resp.status} - {error_text}")
                            raise Exception(f"Error updating arrival: {resp.status} - {error_text}")
                else:
                    # Create new arrival
                    grist_data["records"][0]['fields']['UUID'] = uuid_no_dashes
                    logger.info(f"Creating new arrival")
                    async with session.post(url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error creating arrival: {resp.status} - {error_text}")
                            raise Exception(f"Error creating arrival: {resp.status} - {error_text}")

            logger.info(f"Successfully synced arrival {arrival.data.id} to Grist")
        except Exception as e:
            logger.error(f"Error syncing arrival to Grist: {e}")
            raise

async def grist_arrivals_writer(arrivals: List[Tuple[ArrivalWithMetadata, set]]):
    """Sync multiple arrivals to Grist"""
    logger.info(f"Working on {len(arrivals)} arrivals")
    try:
        writer = GristArrivalWriter()
        batch_size = 1
        for i in range(0, len(arrivals), batch_size):
        #for i in range(0, 10, batch_size):
            batch = arrivals[i:i+batch_size]
            tasks = [writer.update_arrival(arrival_tuple) for arrival_tuple in batch]
            await asyncio.gather(*tasks)
        logger.info("Finished syncing arrivals to Grist")
    except Exception as e:
        logger.critical(f"Error syncing arrivals to Grist: {e}")
        raise 