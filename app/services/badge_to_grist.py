import logging
from typing import List
from uuid import UUID

import aiohttp
from app.config import config
from app.models.badge import Badge

logger = logging.getLogger(__name__)

class GristBadgeWriter:
    def __init__(self):
        self.server = config.grist.server
        self.doc_id = config.grist.doc_id
        self.api_key = config.grist.api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def update_badge(self, badge: Badge):
        """Update or create a badge in Grist"""
        logger.info(f"Working on badge:{badge}")
        try:
            # Prepare the badge data for Grist
            grist_data = {
                "records": [{
                    #"id": badge.nocode_int_id,
                    "fields": {
                        "name": badge.name,
                        #"last_name": badge.last_name or "",
                        #"first_name": badge.first_name or "",
                        "gender": "Ж" if badge.gender == 'FEMALE' else "M" if badge.gender == 'MALE' else "др." if badge.gender == 'OTHER' else None,
                        "phone": badge.phone or "",
                        "diet": "Без особенностей" if badge.diet == 'STANDARD' else "Веган" if badge.diet == 'VEGAN' else "Unknown",
                        "feed_type": "Бесплатно" if badge.feed == 'FREE' else "Платно" if badge.feed == 'PAID' else "Без питания",
                        "batch": str(badge.batch) if badge.batch else "",
                        "role": badge.role.name,
                        "comment": badge.comment or "",
                        "position": badge.occupation,
                        "person": str(badge.person.id) if badge.person else "",
                        "parent": str(badge.parent.id) if badge.parent else "",
                        "updated_at": badge.last_updated.isoformat() if badge.last_updated else "",
                        #"uuid": str(badge.id),
                        #"directions": [str(d.id) for d in badge.directions] if badge.directions else []
                    }
                }]
            }

            # Check if badge exists in Grist
            url = f"{self.server}/api/docs/{self.doc_id}/tables/Copy_of_Badges_2025/records"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Error fetching badges: {resp.status} - {error_text}")
                        raise Exception(f"Error fetching badges: {resp.status} - {error_text}")
                    records = await resp.json()
                    existing_badge = next((r for r in records.get('records', []) 
                                        if r['fields'].get('UUID') == badge.id), None)
                logger.info(f"BADGE EXIST??? {existing_badge}")
                if existing_badge:
                    # Update existing badge
                    grist_data["records"][0]["id"] = existing_badge.id
                    logger.info(grist_data)
                    update_url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2025/records"
                    async with session.patch(update_url, headers=self.headers, json=grist_data) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error(f"Error updating badge: {resp.status} - {error_text}")
                            raise Exception(f"Error updating badge: {resp.status} - {error_text}")
                else:
                    # Create new badge
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

async def grist_writer_v2(badges: List[Badge]):
    """Sync multiple badges to Grist"""
    logger.info(f"Working on badge:{badges}")
    try:
        writer = GristBadgeWriter()
        for badge in badges:
            await writer.update_badge(badge)
        logger.info("Finished syncing badges to Grist")
    except Exception as e:
        logger.critical(f"Error syncing badges to Grist: {e}")
        raise 