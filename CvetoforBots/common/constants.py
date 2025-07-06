from collections import namedtuple


BOT_CHOICES = [
    ('ulanudebot', 'Улан-Удэ Бот'),
    ('angarskbot', 'Ангарск Бот'),
]

START_TEXT = (
    "Для продолжения работы в <b>{title}</b> Вам необходимо ознакомиться со следующими документами:"
)

WELCOME_TEXT = (
    "<b>Привет и добро пожаловать!</b>\n\n"
    "Этот бот создан для <i>любителей цветов</i> и <u>красивой жизни</u> 🌸💐"
)

AGREEMENT_TEXT = (
    "Нажимая кнопку «Согласен(-на)», вы подтверждаете, что ознакомились с присланными выше документами, а также:\n"
    "• Даёте согласие с условиями публичной оферты\n"
    "• Даёте согласие на обработку персональных данных\n"
    "• Политикой обработки персональных данных\n"
    "• Даёте согласие на получение информационных и рекламных рассылок"
)

CATEGORIES_CHOICE_TEXT = "Какой способ подобрать букет выбираете?"

CHOOSE_CATEGORIES = "Выберите одну категорию для продолжения"

SELECTED_FILTERS_TEMPLATE = "\n\nВы выбрали:\n{filters}"

nav_tuple = namedtuple("NavButton", ["text", "callback"])


class NavButtons:
    BACK = nav_tuple("◀️ Назад", "back")
    NEXT = nav_tuple("Далее ➡️", "next")


documents_tuple = namedtuple('DocumentButton', ['text', 'slug'])


class DocumentButtons:
    OFFER = documents_tuple("Оферта", "offer")
    POLICY = documents_tuple("Политика обработки персональных данных", "policy")
    PERSONAL_DATA = documents_tuple("Согласие на обработку персональных данных", "personal_data")
    NOTIFICATION = documents_tuple("Согласие на получение рассылки", "notification")
    USER_AGREE = documents_tuple("Согласен(-на)", "user_agreed")


categories_tuple = namedtuple('CategoryButtons', ['text', 'callback'])


class CategoryButtons:
    BUDGET_BOUQUET = categories_tuple("Выбрать букет по бюджету", "budget-bouqet")
    BY_FLOWER_BOUQUET = categories_tuple("Выбрать букет по цветку", "by-flower-bouqet")


budgets_tuple = namedtuple('BudgetButtons', ['text', 'callback'])


class BudgetButtons:
    UP_TO_3K = budgets_tuple("до 3000 руб.", "up-to-3k")
    FROM_3K_6K = budgets_tuple("от 3000 руб. до 6000 руб.", "from-3k-6k")
    FROM_6K = budgets_tuple("от 6000 руб. и более", "from-6k")


post_card_tuple = namedtuple("PostCardButtons", ['text', 'callback'])


class PostCardButtons:
    YES = post_card_tuple("Да", "post-card-yes")
    NO = post_card_tuple("Нет", "post-card-no")


flowers_tuple = namedtuple('FlowerButtons', ['text', 'callback'])


class FlowerBouquetButtons:
    ROSE_KENIA = flowers_tuple("Розы Кения", "rose-kenia")  # rose-bouquet
    ROSE_ECUADOR = flowers_tuple("Розы Эквадор", "rose-ecuador")
    BASKET = flowers_tuple("Корзина с цветами", "flower-basket")
    CHRYSANTHEMUM = flowers_tuple("Хризантема", "chrysanthemum-bouquet")
    MIXED = flowers_tuple("Сборный букет", "mixed-bouquet")


class FlowerButtons:
    ROSE_KENIA = "Розы Кения"
    ROSE_ECUADOR = "Розы Эквадор"
    BASKET = "Корзина с цветами"
    CHRYSANTHEMUM = "Хризантема"
    MIXED = "Сборный букет"

    @classmethod
    def all(cls):
        return [
            cls.ROSE_KENIA,
            cls.ROSE_ECUADOR,
            cls.BASKET,
            cls.CHRYSANTHEMUM,
            cls.MIXED,
        ]


class PriceButtons:
    UP_TO_3K = "до 3000 руб."
    FROM_3K_6K = "от 3000 руб. до 6000 руб."
    FROM_6K = "от 6000 руб. и более"

    @classmethod
    def all(cls):
        return [
            cls.UP_TO_3K,
            cls.FROM_3K_6K,
            cls.FROM_6K,
        ]


actions_tuple = namedtuple('ActionButton', ['text', 'callback'])


class ActionButtons:
    CHOOSE = actions_tuple("✅ Оформить заказ", "order")
    NEW_FILTER = actions_tuple("🔄 Новый поиск", "new_filter")
    CATALOG_PREV = actions_tuple("◀️", "catalog_prev")
    CATALOG_NEXT = actions_tuple("▶️", "catalog_next")
    CART = actions_tuple("🛒", "basket")
    ADD_TO_CART = actions_tuple("⤵️ Добавить в корзину", "add_to_cart")
    REMOVE_FROM_CART = actions_tuple("❌ Удалить из корзины", "remove_from_cart")
