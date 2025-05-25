import logging
from typing import List, Optional
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
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025_copy2/records"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching badges: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching badges: {resp.status} - {error_text}")
                    records = await resp.json()
                    badge_record = next((r for r in records.get('records', []) 
                                      if UUID(r['fields'].get('UUID')) == badge_uuid), None)
                    if badge_record:
                        return badge_record['id']
                    return None
        except Exception as e:
            logger.error(f"Error finding badge in Grist: {e}")
            raise

    async def update_arrival(self, arrival: ArrivalWithMetadata):
        """Update or create a arrival in Grist"""
        logger.info(f"Working on arrival:{arrival}")
        try:
            # Find corresponding badge ID in Grist
            corresponding_badge_id = await self.find_badge_id_by_uuid(arrival.data.badge_id) if arrival.data.badge_id else None
            if not corresponding_badge_id:
                logger.error(f"Could not find corresponding badge in Grist for arrival {arrival.data.id}")
                raise Exception(f"Badge not found in Grist for arrival {arrival.data.id}")

            # Prepare the arrival data for Grist
            grist_data = {
                "records": [{
                    #"id": arrival.nocode_int_id,
                    "fields": {
                        "status": arrival.data.status.value if arrival.data.status else None,
                        'arrival_date': self._date_to_timestamp(arrival.data.arrival_date),
                        'arrival_transport': arrival.data.arrival_transport.value if arrival.data.arrival_transport else None,
                        'departure_date': self._date_to_timestamp(arrival.data.departure_date),
                        'departure_transport': arrival.data.departure_transport.value if arrival.data.departure_transport else None,
                        'badge': corresponding_badge_id
                    }
                }]
            }
            print(arrival)
            print(grist_data)

            # Check if arrival exists in Grist
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Arivals_2025_copy2/records"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching arrivals: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching arrivals: {resp.status} - {error_text}")
                    records = await resp.json()
                    existing_arrival = next((r for r in records.get('records', []) 
                                        if UUID(r['fields'].get('UUID')) == arrival.data.id), None)
                if existing_arrival:
                    # Update existing arrival
                    grist_data["records"][0]["id"] = existing_arrival["id"]
                    logger.info(grist_data)
                    update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Arivals_2025_copy2/records"
                    async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error updating arrival: {resp.status} - {error_text}")
                            raise Exception(f"Error updating arrival: {resp.status} - {error_text}")
                else:
                    # Create new arrival
                    grist_data["records"][0]['fields']['UUID'] = str(arrival.data.id)
                    async with session.post(url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error creating arrival: {resp.status} - {error_text}")
                            raise Exception(f"Error creating arrival: {resp.status} - {error_text}")

            logger.info(f"Successfully synced arrival {arrival.data.id} to Grist")
        except Exception as e:
            logger.error(f"Error syncing arrival to Grist: {e}")
            raise

async def grist_arrivals_writer(arrivals: List[ArrivalWithMetadata]):
    """Sync multiple arrivals to Grist"""
    logger.info(f"Working on arrival:{arrivals}")
    try:
        writer = GristArrivalWriter()
        for arrival in arrivals:
            await writer.update_arrival(arrival)
        logger.info("Finished syncing arrivals to Grist")
    except Exception as e:
        logger.critical(f"Error syncing arrivals to Grist: {e}")
        raise 