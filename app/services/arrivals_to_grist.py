import logging
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

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
        """Find badge ID in Grist by its UUID"""
        try:
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025/records"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching badges: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching badges: {resp.status} - {error_text}")
                    records = await resp.json()
                    badge_record = next((r for r in records.get('records', []) 
                                      if UUID(str(r['fields'].get('UUID'))) == badge_uuid), None)
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
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Arrivals_2025/records"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching arrivals: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching arrivals: {resp.status} - {error_text}")
                    records = await resp.json()
                    existing_arrival = next((r for r in records.get('records', []) 
                                        if UUID(str(r['fields'].get('UUID'))) == arrival.data.id), None)
                if existing_arrival:
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
                    grist_data["records"][0]['fields']['UUID'] = str(arrival.data.id)
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
    logger.info(f"Working on arrivals:{arrivals}")
    try:
        writer = GristArrivalWriter()
        for arrival_tuple in arrivals:
            await writer.update_arrival(arrival_tuple)
        logger.info("Finished syncing arrivals to Grist")
    except Exception as e:
        logger.critical(f"Error syncing arrivals to Grist: {e}")
        raise 