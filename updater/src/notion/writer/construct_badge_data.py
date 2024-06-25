from typing import Dict, Optional

# from dictionaries.dictionaries import ParticipationRole

badge_data = {  # TODO: читать это из базы?! Или из ParticipationRole?
    "VOLUNTEER": "0459773f44c748cab93a3e34d6734af5",
    "ANIMATOR": "057f0f300918445baa160f1c1c54e216",
    "MEDIC": "35d3f8383b6d47aa8fe89f42c7e5cf5d",
    "PRESS": "45dd1e261b0e45dfb451472a240a2bb0",
    "LECTOR": "48d62cd1097a4770b36fe6d77165675b",
    "FELLOW": "5899450b338d4f6aa1f91fa9fa7fc151",
    "VIP": "7f6da8d79b214e5dac0ad545fff1a195",
    "ARTIST": "949fb54de39b40e4a4522b5bb8874989",
    "CONTRACTOR": "98d86463eb8e4a648662f609f69878be",
    "MASTER": "a381b28fad2a4656b4344ad1bf9f6229",
    "CAMP_LEAD": "aed0b2370f3d49749c73e7d6a95a47dd",
    "CAMP_GUY": "ee79040c808047e08f5a1e4c423994a5",
    "ART_FELLOW": "ffbe65c103f640b4878bc706fbb3aabf",
    "TEAM_LEAD": "9f8714fa106d4c6784c75ea22b0b60b7",
    "ORGANIZER": "31361deff99f4189a34786ecb75476f9",
    "VICE": "48414ef4776b44eaaf5ead19c4fd1e42"
}


def construct_badge_data(
        title: Optional[str] = None,
        services_and_locations_id: Optional[str] = None,
        role_id: Optional[str] = None,
        position: Optional[str] = None,
        last_name: Optional[str] = None,
        first_name: Optional[str] = None,
        gender: Optional[str] = None,
        is_child: Optional[bool] = None,
        phone: Optional[str] = None,
        dietary_restrictions: Optional[str] = None,
        meal_type: Optional[str] = None,
        photo_url: Optional[str] = None,
        photo_name: Optional[str] = None,
        party: Optional[str] = None,
        color: Optional[str] = None,
        comment: Optional[str] = None
) -> Dict[str, Dict]:
    data = {}

    if title:
        data["Надпись"] = {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        }

    if services_and_locations_id:
        data["Службы и локации"] = {
            "relation": [
                {
                    "id": services_and_locations_id
                }
            ]
        }

    if role_id:
        data["Роль"] = {
            "relation": [
                {
                    # "id": ParticipationRole[role_id].value
                    "id": badge_data[role_id]
                }
            ]
        }

    if position:
        data["Должность"] = {
            "rich_text": [
                {
                    "text": {
                        "content": position
                    }
                }
            ]
        }

    if last_name:
        data["Фамилия"] = {
            "rich_text": [
                {
                    "text": {
                        "content": last_name
                    }
                }
            ]
        }

    if first_name:
        data["Имя"] = {
            "rich_text": [
                {
                    "text": {
                        "content": first_name
                    }
                }
            ]
        }

    if gender:
        data["Пол"] = {
            "select": {
                "name": gender
            }
        }

    if is_child is not None:
        data["Ребенок"] = {
            "checkbox": is_child
        }

    if phone:
        data["Телефон"] = {
            "rich_text": [
                {
                    "text": {
                        "content": phone
                    }
                }
            ]
        }

    if dietary_restrictions:
        data["Особенности питания"] = {
            "select": {
                "name": dietary_restrictions
            }
        }

    if meal_type:
        data["Тип питания"] = {
            "select": {
                "name": meal_type
            }
        }

    if photo_url and photo_name:
        data["Фото"] = {
            "files": [
                {
                    "name": photo_name,
                    "file": {
                        "url": photo_url
                    }
                }
            ]
        }

    if party:
        data["Партия"] = {
            "select": {
                "name": party
            }
        }

    if color:
        data["Цвет"] = {
            "select": {
                "name": color
            }
        }

    if comment:
        data["Комментарий"] = {
            "rich_text": [
                {
                    "text": {
                        "content": comment
                    }
                }
            ]
        }

    return data


if __name__ == '__main__':
    # Пример использования функции-конструктора
    page_data = construct_badge_data(
        title="Рюкзак",
        services_and_locations_id="08fe99b5-c934-4932-a6c0-5a685d35c1c1",  # Заменить на актуальный
        role_id="9f8714fa-106d-4c67-84c7-5ea22b0b60b7",  # Заменить на актуальный ID
        position="Артист Карнавала",
        last_name="ТЕСТ",
        first_name="ТЕСТ",
        gender="М",
        is_child=False,
        phone="+79999999999",
        dietary_restrictions="Без особенностей",
        meal_type="Бесплатно",
        photo_url="https://prod-files-secure.s3.us-west-2.amazonaws.com/f8e39894-4d91-4bbc-a2f0-2997b3523b3d/bd22e81c-99b9-44f6-b476-4d21d916b66c/11zon_cropped_%284%29.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240619T150004Z&X-Amz-Expires=3600&X-Amz-Signature=18002bd50abf49e32bc8bba23ef7db4959de7250a10dadfaf557d1eaead36d8d&X-Amz-SignedHeaders=host&x-id=GetObject",
        photo_name="avatar.jpg",
        party="4",
        color="Оранжевый",
        comment=""
    )

    print(page_data)
