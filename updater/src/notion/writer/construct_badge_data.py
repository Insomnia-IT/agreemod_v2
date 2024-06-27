"""
Эти функции нужны для восстановления данных в Notion в автоматическом режиме из дампа
"""

from typing import Dict, Optional

# from dictionaries.dictionaries import ParticipationRole

badge_data = {  # TODO: читать это из базы?! Или из ParticipationRole?
    "Волонтёр": "0459773f-44c7-48ca-b93a-3e34d6734af5",
    "Аниматор": "057f0f30-0918-445b-aa16-0f1c1c54e216",
    "Медик": "35d3f838-3b6d-47aa-8fe8-9f42c7e5cf5d",
    "Пресса": "45dd1e26-1b0e-45df-b451-472a240a2bb0",
    "Лектор": "48d62cd1-097a-4770-b36f-e6d77165675b",
    "Свои (плюсодины)": "5899450b-338d-4f6a-a1f9-1fa9fa7fc151",
    "VIP": "7f6da8d7-9b21-4e5d-ac0a-d545fff1a195",
    "Артист": "949fb54d-e39b-40e4-a452-2b5bb8874989",
    "Подрядчик": "98d86463-eb8e-4a64-8662-f609f69878be",
    "Мастер": "a381b28f-ad2a-4656-b434-4ad1bf9f6229",
    "Лидер нефедеральной локации": "aed0b237-0f3d-4974-9c73-e7d6a95a47dd",
    "Волонтёр нефедеральной локации": "ee79040c-8080-47e0-8f5a-1e4c423994a5",
    "Сопровождающие (участников)": "ffbe65c1-03f6-40b4-878b-c706fbb3aabf",
    "Бригадир": "9f8714fa-106d-4c67-84c7-5ea22b0b60b7",
    "Организатор": "31361def-f99f-4189-a347-86ecb75476f9",
    "Зам. руководителя": "48414ef4-776b-44ea-af5e-ad19c4fd1e42"
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
            "relation": [{"id": i} for i in services_and_locations_id.split(",")]
        }

    if role_id:
        role_name = badge_data.get(role_id)
        if role_name:
            data["Роль"] = {
                "relation": [
                    {
                        # "id": ParticipationRole[role_id].value
                        "id": role_name  # TODO: читать из enum
                    }
                ]
            }

    if position and str(position) != 'nan':
        data["Должность"] = {
            "rich_text": [
                {
                    "text": {
                        "content": position
                    }
                }
            ]
        }

    if last_name and str(last_name) != 'nan':
        data["Фамилия"] = {
            "rich_text": [
                {
                    "text": {
                        "content": last_name
                    }
                }
            ]
        }

    if first_name and str(first_name) != 'nan':
        data["Имя"] = {
            "rich_text": [
                {
                    "text": {
                        "content": first_name
                    }
                }
            ]
        }

    if gender and str(gender) != 'nan':
        data["Пол"] = {
            "select": {
                "name": gender
            }
        }

    if bool(is_child):
        data["Ребенок"] = {
            "checkbox": bool(is_child)
        }

    if phone and str(phone) != 'nan':
        data["Телефон"] = {
            "rich_text": [
                {
                    "text": {
                        "content": phone
                    }
                }
            ]
        }

    if dietary_restrictions and str(dietary_restrictions) != 'nan':
        data["Особенности питания"] = {
            "select": {
                "name": dietary_restrictions
            }
        }

    if meal_type and str(meal_type) != 'nan':
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

    if party and str(party) != 'nan':
        data["Партия"] = {
            "select": {
                "name": str(int(float(party)))
            }
        }

    if color and str(color) != 'nan':
        data["Цвет"] = {
            "select": {
                "name": color
            }
        }

    if comment and str(comment) != 'nan':
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


def extract_and_construct_badge_data_from_notion(data):
    title = data.get('Надпись', {}).get('title', [{}])[0].get('plain_text')
    services_and_locations_id = data.get('Службы и локации', {}).get('relation', [{}])[0].get('id')
    role_id = data.get('Роль', {}).get('relation', [{}])[0].get('id')
    position = data.get('Должность', {}).get('rich_text', [{}])[0].get('plain_text')
    last_name = data.get('Фамилия', {}).get('rich_text', [{}])[0].get('plain_text')
    first_name = data.get('Имя', {}).get('rich_text', [{}])[0].get('plain_text')
    gender = data.get('Пол', {}).get('select', {}).get('name')
    is_child = data.get('Ребенок', {}).get('checkbox')

    phone_info = data.get('Телефон', {}).get('rich_text', [])
    if phone_info and isinstance(phone_info, list) and len(phone_info) > 0:
        phone = phone_info[0].get('plain_text')
    else:
        phone = None

    dietary_restrictions = data.get('Особенности питания', {}).get('select', {}).get('name')
    meal_type = data.get('Тип питания', {}).get('select', {}).get('name')
    photo_url = data.get('Фото', {}).get('files', [{}])[0].get('file', {}).get('url')
    photo_name = data.get('Фото', {}).get('files', [{}])[0].get('name')
    party = data.get('Партия', {}).get('select', {}).get('name')
    color = data.get('color', {}).get('formula', {}).get('string')

    comment = data.get('Комментарий', {}).get('rich_text', [])
    if comment:
        comment = comment[0].get('plain_text')
    else:
        comment = None

    return construct_badge_data(
        title=title,
        services_and_locations_id=services_and_locations_id,
        role_id=role_id,
        position=position,
        last_name=last_name,
        first_name=first_name,
        gender=gender,
        is_child=is_child,
        phone=phone,
        dietary_restrictions=dietary_restrictions,
        meal_type=meal_type,
        photo_url=photo_url,
        photo_name=photo_name,
        party=party,
        color=color,
        comment=comment
    )


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
