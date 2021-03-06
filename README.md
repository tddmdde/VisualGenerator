Данный модуль используется для автоматизации создания вижуалов SMM специалистами без привлечения дизайнеров.

Дизайнеры создали шаблоны для регулярных товарных вижуалов в виде Excel таблиц.
В таблицах указаны координаты элементов, их группы, идентификаторы и другие необходимые параметры.
Таблицы можно найти в resources/visuals/templates


**Со стороны пользователя:**

1. Пользователь выбирает необходимый шаблон из имеющихся.

![Alt text](example_pics/ui_1_choose_template.png?raw=true)

2. При выборе шаблона отрисовывается необходимая форма, начинающаяся с инструкции:

![Alt text](example_pics/ui_2_instruction.png?raw=true)

3. Пользователь выбирает нужный формат и регион, вносит SKU (артикул) товара и нажимает на "Получить данные"

![Alt text](example_pics/ui_3_get_data.png?raw=true)

4. Сервис возвращает наименование товара и текущие цены. Пользователю необходимо отформатировать название по эстетическим соображениям, разбив его на части.

![Alt text](example_pics/ui_4_refactor_title.png?raw=true)

5. Пользователь отформатировал название, ввёл данные о событии (Рассрочка 12%) и нажал на Сгенерировать.

![Alt text](example_pics/ui_5_entered_data.png?raw=true)

6. Через 5-7 секунд ему возвращается сгенерированная картинка.

![Alt text](example_pics/ui_6_generated_image.png?raw=true)

7. В продовой версии есть возможность запостить в Telegram по нажатию кнопки в WebUI.

![Alt text](example_pics/example_tg_post.png?raw=true)
