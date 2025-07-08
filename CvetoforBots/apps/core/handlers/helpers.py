import datetime
import re
import json

from django.db.models import Q

from CvetoforBots.apps.flowers.models import Color, Product


def make_bouquet_query(price_filter: str) -> Q:
    match price_filter:
        case "от 3000 руб. до 6000 руб.":
            query = Q(prices__price__gte=3000, prices__price__lte=6000)
        case "до 3000 руб.":
            query = Q(prices__price__lte=3000)
        case "от 6000 руб. и более":
            query = Q(prices__price__gte=6000)
        case "Розы Кения":
            query = Q(category__title__icontains='кения')
        case "Розы Эквадор":
            query = Q(category__title__icontains='эквадор')
        case "Корзина с цветами":
            query = Q(category__id=3) & ~Q(category__title__icontains="фрукт") & ~Q(
                category__title__icontains="подар")
        case "Хризантема":
            query = Q(category__title__icontains='хризантем')
        case "Сборный букет":
            query = Q(category__title__icontains='сборн')
    return query


def to_markdown(html_text: str) -> str:
    html_text = (html_text
                 .replace("<p>", "")
                 .replace("</p>", "")
                 .replace("<ul>", "")
                 .replace("</ul>", "")
                 .replace("<li>", "- ")
                 .replace("</li>", "")
                 .replace("<h1>", "* ")
                 .replace("</h1>", " *")
                 .replace("<h2>", "* ")
                 .replace("</h2>", " *")
                 .replace("<h3>", "* ")
                 .replace("</h3>", " *")
                 .replace("&ndash;", "—")
                 .replace("<strong>", "")
                 .replace("</strong>", "")
                 .replace("<i>", "")
                 .replace("</i>", "")
                 )
    return html_text


def _parse_bouquet_component(data: dict) -> dict | None:
    """
    Парсит JSON-строку, представляющую компонент букета, и возвращает словарь с данными.
    (Эта функция взята из предыдущего ответа)
    """
    try:
        # Извлекаем обязательные данные
        quantity = int(data.get('count', 0))
        name = data.get('__title')

        browsers = data.get('browsers', {})
        product_id = browsers.get('products', [None])[0]

        # Если чего-то важного нет, считаем данные некорректными
        if not name or product_id is None:
            if browsers:  # Под отличающийся формат в БД
                try:
                    result = {
                        "name": Product.objects.filter(id=browsers.get('products')[0]).first().title,
                        'quantity': data.get("count"),
                        "color_name": Color.objects.filter(id=browsers.get("color")[0]).first().title,
                    }
                except Exception:
                    return None
            else:
                return None
        else:
            # Собираем результат, если данные стандартные
            result = {
                'name': name,
                'quantity': quantity,
                'product_id': product_id,
                'color_name': None,
                'color_id': None
            }

        # Добавляем цвет, если он есть
        if 'color' in browsers and 'color[__title]' in data:
            result['color_name'] = data.get('color[__title]')
            result['color_id'] = browsers.get('color', [None])[0]

        return result

    except (json.JSONDecodeError, ValueError, TypeError, IndexError):
        # В случае любой ошибки парсинга возвращаем None
        return None


def get_formatted_component_string(data: dict) -> str | None:
    """
    Принимает JSON-строку, парсит её и возвращает
    отформатированную строку вида "*товар* *сколько* шт.".
    """
    component_data = _parse_bouquet_component(data)

    if not component_data:
        return None

    name = component_data['name']
    quantity = component_data['quantity']

    return f"{name} {quantity} шт."


def combine_duplicate_items(text_input: str) -> str:
    """
    Объединяет одинаковые позиции, сохраняя начальный перенос строки, если он был.
    """
    starts_with_newline = text_input.startswith('\n')

    item_totals = {}

    lines = text_input.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.rsplit(' ', 2)
            item_name = parts[0]
            quantity = int(parts[1])
            item_totals[item_name] = item_totals.get(item_name, 0) + quantity
        except (IndexError, ValueError):
            continue

    output_lines = [f"{name} {total_quantity} шт." for name, total_quantity in item_totals.items()]
    final_string = "\n".join(output_lines)

    if starts_with_newline:
        return "\n" + final_string
    else:
        return final_string


def is_valid_russian_phone(phone_number: str) -> bool:
    """
    Проверяет российский номер телефона в разных форматах
    приводя его к стандартному виду 7XXXXXXXXXX.

    :param phone_number: Строка для проверки.
    :return: True, если номер валидный, иначе False.
    """
    if not isinstance(phone_number, str):
        return False

    cleaned_number = re.sub(r'\D', '', phone_number)

    if len(cleaned_number) == 11 and cleaned_number.startswith('8'):
        cleaned_number = '7' + cleaned_number[1:]

    return len(cleaned_number) == 11 and cleaned_number.startswith('7')


def get_next_four_days_formatted():
    """
    Возвращает список из 4-х дат в виде строк формата 'dd.mm.YYYY'.
    """
    today = datetime.date.today()
    formatted_dates = []
    for i in range(0, 4):
        day_offset = datetime.timedelta(days=i)
        future_date = today + day_offset
        formatted_dates.append(future_date.strftime('%d.%m.%Y'))
    return formatted_dates
