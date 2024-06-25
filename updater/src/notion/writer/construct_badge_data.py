from typing import Dict


def construct_badge_data(
        title: str,
        services_and_locations_id: str,
        role_id: str,
        position: str,
        last_name: str,
        first_name: str,
        gender: str,
        is_child: bool,
        phone: str,
        dietary_restrictions: str,
        meal_type: str,
        photo_url: str,
        photo_name: str,
        party: str,
        color: str,
        comment: str
) -> Dict[str, Dict]:
    return {
        "Надпись": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        },
        "Службы и локации": {
            "relation": [
                {
                    "id": services_and_locations_id
                }
            ]
        },
        "Роль": {
            "relation": [
                {
                    "id": role_id
                }
            ]
        },
        "Должность": {
            "rich_text": [
                {
                    "text": {
                        "content": position
                    }
                }
            ]
        },
        "Фамилия": {
            "rich_text": [
                {
                    "text": {
                        "content": last_name
                    }
                }
            ]
        },
        "Имя": {
            "rich_text": [
                {
                    "text": {
                        "content": first_name
                    }
                }
            ]
        },
        "Пол": {
            "select": {
                "name": gender
            }
        },
        "Ребенок": {
            "checkbox": is_child
        },
        "Телефон": {
            "rich_text": [
                {
                    "text": {
                        "content": phone
                    }
                }
            ]
        },
        "Особенности питания": {
            "select": {
                "name": dietary_restrictions
            }
        },
        "Тип питания": {
            "select": {
                "name": meal_type
            }
        },
        "Фото": {
            "files": [
                {
                    "name": photo_name,
                    "file": {
                        "url": photo_url
                    }
                }
            ]
        },
        "Партия": {
            "select": {
                "name": party
            }
        },
        "Цвет": {
            "select": {
                "name": color
            }
        },
        "Комментарий": {
            "rich_text": [
                {
                    "text": {
                        "content": comment
                    }
                }
            ]
        }
    }


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
