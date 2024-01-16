# banned-links-checker
Скрипт является консольной программой для автоматизации поиска запрещенных ссылок в статьях на известном интернет ресурсе.

## Использование
У скрипта есть 2 варианта использования:
1. Проверка нескольких статей, которые берутся из RSS ленты.
2. Проверка одной отдельной статьи.

### 1. Проверка нескольких статей
Скрипт берет статьи из RSS ленты https://habr.com/ru/rss/articles/?fl=ru (последние 40 статей на сайте), просматривает их на предмет запрещенных ссылок и выводит подозрительные ссылки в окно терминала. Подозрительными считаются ссылки доменные имена в которых не входят в список разрешенных. Списки разрешенных доменов находятся в текстовых файлах в каталоге `allowed_domains`. Список доменов периодически пополняется.

Просмотренные статьи записываются в файл `article_links.txt` (если файла нет в текущем каталоге он создается при запуске). Данный файл нужен для того чтобы повторно не проверять статьи, которые уже были проверены, текущие статьи из RSS ленты сравниваются со статьями из файла `article_links.txt`.

Ссылки, в которых есть параметры запроса, для большей наглядности помечаются символом `▶`, чтобы выделять реферальные/партнерские/маркетинговые ссылки.

Найденные ссылки выводятся в формате `текст ссылки -> url ссылки`.

Пример запуска:

```
$ python async_links_checker.py
----------------------------------------
Link: https://habr.com/ru/articles/784996/
Title: А закрыл ли я замок двери? Home assistant + Aqara и немного витухи

▶ Датчик акара 900 р. → https://aliexpress.ru/item/32991903307.html?sku_id=12000036195547989
Магнит 100 р. → https://leroymerlin.ru/product/magnit-15-mm-s-otverstiem-81969375/
Дверь → https://torex.ru/configurator/2730946/
Наличники → https://leroymerlin.ru/product/nalichnik-teleskopicheskiy-artens-flay-una-2150x70x8-mm-hardfleh-laminaciya-cvet-belyy-komplekt-5-sht-83859814/
----------------------------------------
Link: https://habr.com/ru/articles/785056/
Title: Шкала масштабов вселенной (русский язык)

шкале масштабов вселенной → https://universe.pavelfrolov.com/
шкала → https://htwins.net/scale2/index.html
flash приложение → https://elementy.ru/catalog/1054/Shkala_masshtabov_Vselennoy_SWF_s02_yapfiles_ru_files_531066_SHkala_masshtabov_Vselennoy_v_2_swf
выгрузил → https://universe.pavelfrolov.com/
...
```
**Примечание:** ссылки проверяются только в UGC статьях, статьи в корпоративных блогах игнорируются.
### 2. Проверка одной статьи
Для проверки одной отдельной статьи при запуске нужно указать её URL - `$ python async_links_checker.py <url>`.

Пример запуска:
```bash
$ python async_link_checker.py https://habr.com/ru/articles/785402/
----------------------------------------
Link: https://habr.com/ru/articles/785402/
Title: Введение в поддержку JavaScript в MySQL

GraalVM → https://www.graalvm.org/
ECMAScript 2021 → https://tc39.es/ecma262/2021/
GraalVM → https://www.graalvm.org/
конкурентоспособна с точки зрения производительности → https://www.graalvm.org/javascript/

```

## Зависимости

В скрипте используются библиотека `asyncio` и языковые конструкции `async/await` поэтому версия Python должна быть не ниже 3.5.

Рекомендуется устанавливать зависимости в виртуальном окружении, используя [venv](https://docs.python.org/3/library/venv.html) или любую другую реализацию, например, [virtualenv](https://github.com/pypa/virtualenv).

В примере используется модуль `venv` который появился в стандартной библиотеке python версии 3.3.

1. Скопируйте репозиторий в текущий каталог. Воспользуйтесь командой:
```bash
$ git clone https://github.com/igorzakhar/banned-links-checker.git
```

После этого программа будет скопирована в каталог `banned-links-checker`.

2. Создайте и активируйте виртуальное окружение:
```bash
$ cd banned-links-checker # Переходим в каталог с программой
$ python3 -m venv my_virtual_environment # Создаем виртуальное окружение
$ source my_virtual_environment/bin/activate # Активируем виртуальное окружение
```

3. Установите сторонние библиотеки  из файла зависимостей:
```bash
$ pip install -r requirements.txt # В качестве альтернативы используйте pip3
```



