import logging
from typing import List, Tuple
from uuid import UUID

import aiohttp
from app.config import config
#from app.models.badge import Badge
from app.schemas.feeder.badge import Badge

logger = logging.getLogger(__name__)

class GristBadgeWriter:
    def __init__(self):
        self.server = config.grist.server
        self.doc_id = config.grist.doc_id
        self.api_key = config.grist.api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def update_badge(self, badge_tuple: Tuple[Badge, set]):
        """Update or create a badge in Grist"""
        badge, present_fields = badge_tuple
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
                fields["gender"] = badge.gender.value if badge.gender else None
            if 'phone' in present_fields:
                fields["phone"] = badge.phone
            if 'diet' in present_fields:
                fields["diet"] = badge.diet.value if badge.diet else None
            if 'feed' in present_fields:
                fields["feed_type"] = badge.feed
            if 'child' in present_fields:
                fields["infant"] = badge.child
            if 'role' in present_fields:
                fields["role"] = badge.role.value
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

            grist_data = {
                "records": [{
                    "fields": fields
                }]
            }

            # Check if badge exists in Grist
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025_copy2/records"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching badges: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching badges: {resp.status} - {error_text}")
                    records = await resp.json()
                    existing_badge = next((r for r in records.get('records', []) 
                                        if UUID(r['fields'].get('UUID')) == UUID(badge.id)), None)
                if existing_badge:
                    # Update existing badge
                    logger.info(f"Updating existing badge")
                    grist_data["records"][0]["id"] = existing_badge["id"]
                    logger.info(grist_data)
                    update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025_copy2/records"
                    async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error updating badge: {resp.status} - {error_text}")
                            raise Exception(f"Error updating badge: {resp.status} - {error_text}")
                else:
                    # Create new badge
                    logger.info(f"Creating new badge")
                    grist_data["records"][0]['fields']['UUID'] = str(badge.id)
                    async with session.post(url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error creating badge: {resp.status} - {error_text}")
                            raise Exception(f"Error creating badge: {resp.status} - {error_text}")

            logger.info(f"Successfully synced badge {badge.name} to Grist")
        except Exception as e:
            logger.error(f"Error syncing badge to Grist: {e}")
            raise

async def grist_badges_writer(badges: List[Tuple[Badge, set]]):
    """Sync multiple badges to Grist"""
    logger.info(f"Working on badges:{badges}")
    try:
        writer = GristBadgeWriter()
        for badge_tuple in badges:
            await writer.update_badge(badge_tuple)
            # TODO: Somehow Grist doesn't allow me to make first entry correct, so we have to do it twice
            await writer.update_badge(badge_tuple)
        logger.info("Finished syncing badges to Grist")
    except Exception as e:
        logger.critical(f"Error syncing badges to Grist: {e}")
        raise 