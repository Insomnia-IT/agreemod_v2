from enum import StrEnum
import logging

import psycopg2

from database.config import config

logger = logging.getLogger(__name__)

conn = psycopg2.connect(
    database="agreemod",
    user=config.postgres.user,
    password=config.postgres.password,
    host=config.postgres.host,
    port=config.postgres.port,
)
try:
    cur = conn.cursor()
    cur.execute(f"SELECT code, color FROM public.badge_color")
    badge_colors = cur.fetchall()
    # cur.execute(f"SELECT code, diet FROM public.diet_type")
    # diet_types = cur.fetchall()
    cur.execute(f"SELECT name, code FROM public.direction_type")
    direction_types = cur.fetchall()
    # cur.execute(f"SELECT code, feed FROM public.feed_type")
    # feed_types = cur.fetchall()
    # cur.execute(f"SELECT code, gender FROM public.gender")
    # genders = cur.fetchall()
    cur.execute(f"SELECT code, name FROM public.participation_role")
    participation_roles = cur.fetchall()
    cur.execute(f"SELECT code, name FROM public.participation_status")
    participation_statuses = cur.fetchall()
    # cur.execute(f"SELECT code, transport FROM public.transport_type")
    # transport_types = cur.fetchall()

    BadgeColor = StrEnum('BadgeColor', badge_colors)
    DirectionType = StrEnum('DirectionType', direction_types)
    ParticipationRole = StrEnum('ParticipationRole', participation_roles)
    ParticipationStatus = StrEnum('ParticipationStatus', participation_statuses)
finally:
    conn.close()