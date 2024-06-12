import random

from uuid import uuid4

from faker import Faker

from app.schemas.feeder.arrival import ArrivalResponse
from app.schemas.feeder.badge import BadgeResponse
from app.schemas.feeder.directions import DirectionResponse
from app.schemas.feeder.engagement import EngagementResponse
from app.schemas.feeder.person import PersonResponse
from app.schemas.feeder.requests import SyncResponseSchema


fake = Faker()


def generate_random_badge() -> BadgeResponse:
    return BadgeResponse(
        id=str(uuid4()),  # uuid4()
        deleted=False,
        name=fake.name(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        gender=random.choice(["MALE", "FEMALE"]),
        phone=fake.phone_number(),
        infant=random.choice([True, False]),
        vegan=random.choice([True, False]),
        feed=random.choice(["FREE", "PAID"]),
        number=str(fake.random_int(min=1, max=100)),
        batch=fake.word(),
        role=random.choice(["ORGANIZER", "PARTICIPANT"]),
        position=fake.job(),
        photo=fake.image_url(),
        person=str(uuid4()),
        comment=fake.sentence(),
        notion_id=str(uuid4()),
    )


def generate_random_arrival() -> ArrivalResponse:
    return ArrivalResponse(
        id=str(uuid4()),
        deleted=False,
        badge=str(uuid4()),
        status=random.choice(["PLANNED", "COMPLETED"]),
        arrival_date=str(fake.date_this_year()),
        arrival_transport=random.choice(["CAR", "PLANE", "TRAIN", "UNDEFINED"]),
        departure_date=str(fake.date_this_year()),
        departure_transport=random.choice(["CAR", "PLANE", "TRAIN", "UNDEFINED"]),
    )


def generate_random_engagement() -> EngagementResponse:
    return EngagementResponse(
        id=str(uuid4()),
        deleted=False,
        year=fake.year(),
        person=str(uuid4()),
        role=random.choice(["ORGANIZER", "PARTICIPANT"]),
        position=fake.job(),
        status=random.choice(["PLANNED", "COMPLETED"]),
        direction=str(uuid4()),
        notion_id=str(uuid4()),
    )


def generate_random_person() -> PersonResponse:
    return PersonResponse(
        id=str(uuid4()),
        deleted=False,
        name=fake.name(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        nickname=fake.user_name(),
        other_names=", ".join(fake.words(nb=3)),
        gender=random.choice(["MALE", "FEMALE"]),
        birth_date=str(fake.date_of_birth(minimum_age=18, maximum_age=90)),
        phone=fake.phone_number(),
        telegram=fake.user_name(),
        email=fake.email(),
        city=fake.city(),
        vegan=random.choice([True, False]),
        notion_id=str(uuid4()),
    )


def generate_random_direction() -> DirectionResponse:
    return DirectionResponse(
        id=str(uuid4()),
        deleted=False,
        name=fake.word(),
        first_year=fake.year(),
        last_year=fake.year(),
        type=fake.word(),
        notion_id=str(uuid4()),
    )


def generate_random_response_model_get() -> SyncResponseSchema:
    return SyncResponseSchema(
        badges=[generate_random_badge() for _ in range(5)],
        arrivals=[generate_random_arrival() for _ in range(5)],
        engagements=[generate_random_engagement() for _ in range(5)],
        persons=[generate_random_person() for _ in range(5)],
        directions=[generate_random_direction() for _ in range(5)],
    )
