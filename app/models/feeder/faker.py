from faker import Faker

from app.models.feeder import Direction
from app.models.feeder.arrival import Arrival
from app.models.feeder.badge import Badge
from uuid import uuid4
import random

from app.models.feeder.engagement import Engagement
from app.models.feeder.person import Person
from app.models.feeder.response import ResponseModelGET

fake = Faker()


def generate_random_badge() -> Badge:
    return Badge(
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
        notion_id=str(uuid4())
    )


def generate_random_arrival() -> Arrival:
    return Arrival(
        id=str(uuid4()),
        deleted=False,
        badge=str(uuid4()),
        status=random.choice(["PLANNED", "COMPLETED"]),
        arrival_date=str(fake.date_this_year()),
        arrival_transport=random.choice(["CAR", "PLANE", "TRAIN", "UNDEFINED"]),
        departure_date=str(fake.date_this_year()),
        departure_transport=random.choice(["CAR", "PLANE", "TRAIN", "UNDEFINED"])
    )


def generate_random_engagement() -> Engagement:
    return Engagement(
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


def generate_random_person() -> Person:
    return Person(
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


def generate_random_direction() -> Direction:
    return Direction(
        id=str(uuid4()),
        deleted=False,
        name=fake.word(),
        first_year=fake.year(),
        last_year=fake.year(),
        type=fake.word(),
        notion_id=str(uuid4())
    )


def generate_random_response_model_get() -> ResponseModelGET:
    return ResponseModelGET(
        badges=[generate_random_badge() for _ in range(5)],
        arrivals=[generate_random_arrival() for _ in range(5)],
        engagements=[generate_random_engagement() for _ in range(5)],
        persons=[generate_random_person() for _ in range(5)],
        directions=[generate_random_direction() for _ in range(5)]
    )
