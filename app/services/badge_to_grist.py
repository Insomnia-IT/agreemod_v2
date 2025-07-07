import logging
import asyncio
from typing import List, Tuple
from uuid import UUID
import json
import urllib.parse

import aiohttp
from app.config import config
#from app.models.badge import Badge
from app.schemas.feeder.badge import Badge
from datetime import datetime
from database.meta import async_session
from app.db.repos.badge import BadgeRepo

logger = logging.getLogger(__name__)

class GristBadgeWriter:
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

    async def update_badge(self, badge_tuple: Tuple[Badge, set]) -> bool:
        """Update or create a badge in Grist. Return True if created, False if updated."""
        badge, present_fields = badge_tuple
        if badge.id is None:
            return False
        logger.info(f"Working on badge:{badge}")
        try:
            # Prepare the badge data for Grist
            fields = {}
            
            # Only include fields that were present in the original data
            if 'name' in present_fields:
                fields["name"] = badge.name
            if 'last_name' in present_fields:
                fields["last_name"] = badge.last_name
            if 'first_name' in present_fields:
                fields["first_name"] = badge.first_name
            if 'gender' in present_fields:
                fields["gender"] = badge.gender if badge.gender else None
            if 'phone' in present_fields:
                fields["phone"] = badge.phone
            if 'diet' in present_fields:
                fields["diet"] = badge.diet.value if badge.diet else None
            if 'feed' in present_fields:
                fields["feed_type"] = badge.feed
            if 'child' in present_fields:
                fields["infant"] = badge.child
            if 'role' in present_fields:
                fields["role"] = badge.role
            if 'comment' in present_fields:
                fields["comment"] = badge.comment
            if 'occupation' in present_fields:
                fields["position"] = badge.occupation
            if 'person' in present_fields:
                fields["person"] = badge.person.nocode_int_id if badge.person else ""
            if 'parent' in present_fields:
                fields["parent"] = str(badge.parent.nocode_int_id) if badge.parent else ""
            if 'directions' in present_fields:
                fields["directions_ref"] = ["L"] + [d.nocode_int_id for d in badge.directions] if badge.directions else None
            if 'deleted' in present_fields and badge.deleted:
                fields["to_delete"] = self._date_to_timestamp(datetime.now())
                fields["delete_reason"] = f"FEEDER: deleted"
            elif 'deleted' in present_fields and badge.deleted == False:
                fields["to_delete"] = None
                fields["delete_reason"] = None
            fields["status"] = "Из Кормителя"

            grist_data = {
                "records": [{
                    "fields": fields
                }]
            }

            # Check if badge exists in Grist
            uuid_no_dashes = str(badge.id).replace('-', '')
            filter_obj = {"UUID": [uuid_no_dashes]}
            filter_param = urllib.parse.quote(json.dumps(filter_obj))
            url = (
                f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025/records"
                f"?filter={filter_param}"
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching badges: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching badges: {resp.status} - {error_text}")
                    records = await resp.json()
                    existing_badge = records.get('records', [None])[0] if records.get('records') else None
                if existing_badge:
                    # Check if 'to_delete' is set in Grist
                    if existing_badge["fields"].get("to_delete") is not None and badge.deleted != True:
                        logger.info(f"Updating existing badge with restored data from postgres")
                        async with async_session() as db_session:
                            repo = BadgeRepo(db_session)
                            # badge.id is UUID, ensure it's the right type
                            db_badge = await repo.retrieve(id=badge.id)
                            if db_badge:
                                # Map all fields from db_badge to fields for Grist
                                restored_fields = {
                                    "name": db_badge.name,
                                    "last_name": db_badge.last_name,
                                    "first_name": db_badge.first_name,
                                    "gender": db_badge.gender.value if db_badge.gender else None,
                                    "phone": db_badge.phone,
                                    "diet": db_badge.diet.value if db_badge.diet else None,
                                    "feed_type": db_badge.feed,
                                    "infant": db_badge.child,
                                    "role": db_badge.role.value if db_badge.role else None,
                                    "comment": db_badge.comment,
                                    "position": db_badge.occupation,
                                    "person": db_badge.person.nocode_int_id if db_badge.person else "",
                                    "parent": str(db_badge.parent.nocode_int_id) if db_badge.parent else "",
                                    "directions_ref": ["L"] + [d.nocode_int_id for d in db_badge.directions] if db_badge.directions else None,
                                    "status": "Из Кормителя",
                                }
                                # Then, overlay with the fields from the original request
                                restored_fields.update(fields)

                                grist_data["records"][0]["fields"] = restored_fields
                                grist_data["records"][0]["id"] = existing_badge["id"]
                                update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025/records"
                                async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                                    if resp.status != 200:
                                        error_text = await resp.text()
                                        logger.error(f"Error updating badge: {resp.status} - {error_text}")
                                        raise Exception(f"Error updating badge: {resp.status} - {error_text}")
                                logger.info(f"Successfully restored badge {badge.name} from DB to Grist")
                                return False
                    # Update existing badge
                    logger.info(f"Updating existing badge with data from Feeder")
                    grist_data["records"][0]["id"] = existing_badge["id"]
                    logger.info(grist_data)
                    update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025/records"
                    async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error updating badge: {resp.status} - {error_text}")
                            raise Exception(f"Error updating badge: {resp.status} - {error_text}")
                    logger.info(f"Successfully synced badge {badge.name} to Grist")
                    return False
                else:
                    # Create new badge
                    logger.info(f"Creating new badge")
                    grist_data["records"][0]['fields']['UUID'] = uuid_no_dashes #str(badge.id)
                    async with session.post(url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error creating badge: {resp.status} - {error_text}")
                            raise Exception(f"Error creating badge: {resp.status} - {error_text}")
                    logger.info(f"Successfully synced badge {badge.name} to Grist")
                    return True

        except Exception as e:
            logger.error(f"Error syncing badge to Grist: {e}")
            raise

async def update_badge_with_retry(writer: "GristBadgeWriter", badge_tuple: Tuple[Badge, set]):
    """Helper to call update_badge and retry if it's a new badge."""
    was_created = await writer.update_badge(badge_tuple)
    if was_created:
        # TODO: Somehow Grist doesn't allow me to make first entry correct, so we have to do it twice
        await writer.update_badge(badge_tuple)

async def grist_badges_writer(badges: List[Tuple[Badge, set]]):
    """Sync multiple badges to Grist"""
    logger.info(f"Working on {len(badges)} badges")
    try:
        writer = GristBadgeWriter()
        batch_size = 1
        for i in range(0, len(badges), batch_size):
        #for i in range(0, 10, batch_size):
            batch = badges[i : i + batch_size]
            tasks = [update_badge_with_retry(writer, badge_tuple) for badge_tuple in batch]
            await asyncio.gather(*tasks)
        logger.info("Finished syncing badges to Grist")
    except Exception as e:
        logger.critical(f"Error syncing badges to Grist: {e}")
        raise 