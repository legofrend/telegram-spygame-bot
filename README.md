Telegram бот для игры Найди шпиона, MVP v2.0.1

# 0. ToDo:


# 1. Цель проекта

Цель проекта — сделать карточную игру "Находка для шпиона", в которую можно 
играть на телефоне через телеграм бота без физических карт. Бот должен отличать
ведущего игры и остальных участников, кто только получает карты. Бот также
ведет подсчет очков и выводит победителя. С ботом параллельно могут играть разные
группы людей. Игра доступна на разных языках (русский и английский).


# 2. Описание системы

Система состоит из следующих основных функциональных блоков:

1. Функционал для организатора
2. Функционал для игрока
3. Функционал механики игры
4. Функционал оплаты пожертвований


## 2.1. Типы пользователей

Система предусматривает два типа пользователей системы: организатор и игрок.
Организатор создаёт новую игру и приглашает в нее игроков. После сбора всех игроков
запускает новый раунд и указывает победителя по окончанию раунда. Игроки  
получают свою карту, список локаций, итоги раунда.


## 2.2. Регистрация

Отдельная регистрация не требуется, идентификация пользователя происходит по TelegramID
пользователя.


## 2.3. Аутентификация автора и подписчиков

Аутентификация организатора и остых игроков происходит также по TelegramId.


## 2.4. Функционал для организатора

Любой пользователь может стать организатором игры, нажав создать новую игру. Он
указывает название игры, которая является идентификатором игры для 
присоединения других игроков.
После создании игры организатор получает доступ к функционалу создателя.
Этот функционал состоит из следующих блоков:

1. **\game** - вывод свойств созданной им игры, включая список игроков, их очки, номер раунда
2. **\new** - старт нового раунда
3. [choice] - указание победителя раунда
4. **\end** - закончить игру 


### 2.4.1. Вывод свойств игры

По команде **\game** в Тг организатору приходит информация об игре:

* Название
* Номер раунда
* Сколько сейчас ироков
* Список игроков с их очками


### 2.4.2. Старт нового раунда

По команде **\new** или нажатию нативной кнопки стартует новый раунд. Всем участникам
раздаются карты, стартует таймер раунда. Выводится информация о времени старта 
и окончания раунда


### 2.4.3. По окончанию раунда выбор победителя

В любой момент раунда оргагизатору доступны кнопки с вариантамии, кто победил. По 
клику по кнопке раунд считется оконченным, очки игрокам начисляются согласно выбору:
* Выйграл шпион (2 очка)
* Выйграл шпион (4 очка)
* Выйграли не шпионы: кто именно указал на шпиона (2 очка, остальные 1 очко)

### 2.4.4. Закончить игру

Организтор не может параллельно создавать больше одной игры. Поэтому чтобы стартовать
новую, он должен закончить текущую. Кнопка или команда **\end** завершает игру для
всех игроков.



## 2.5. Функционал для игрока

Игроку достпны следующие команды и фунции:
* **\join [Name]** - присоединиться к существующей игре под названию игры Name
* **\quit** - покинуть игру
* **\loc** - вывести список локаций игры


## 2.6. Функционал механики игры

Новая игра: выбирается сет локаций, в MVP доступен один сет, который выбирается по 
умолчанию.

Новый раунд: 
1. случайным образом выбирается локация
2. один из игроков случайным образом выбирается шпионом
3. всем остальным игрокам случайно выбирается роль из локации
4. всем участникам рассылается соответствюущая информация: шпиону - что он шпион,
   остальным локация и их роль
5. Запускается старт таймера раунда, по умолчанию 7 минут


## 2.7. Функционал оплаты пожертвований

Пользователь может сделать пожертвование в пользу создателя любой суммы на его
выбор прямо в UI телеграма. В MVP версии вывод телефона создателя для СБП переводов.


# 3. Предлагаемый стек технологий

Для реализации системы предлагается следующий стек технологий:

* Бэкенд:
    - Язык Python
    - Aiogram для интеграции с Telegram
    - БД SQLLite
    - Docker для распределения нагрузки
* Фронтенд:
    - MidJourney или другие генеративные ИИ
    - UI/UX Telegram

Для интернет-эквайринга сделать отдельне исследование, чтобы можно было 
интегрировать оплату в телеграм. Для MVP версии пользователям доступен 
номер телефона создателя для СБП перевода.


# 4. Требования к дизайну

Минимализм, скорость, простота интерфейса, чтобы не отвлекать от основной игры.

Ссылки на авторов оригинальной игры.

