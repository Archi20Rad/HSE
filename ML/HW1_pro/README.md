# AI_HW1_Regression_with_inference_pro

## Что было сделано
1. Проведены эксперименты в Jupyter Notebook:
   - Базовое исследование данных. Обработка дубликатов, пропущенных значений. Статистический анализ датасета, анализ распределений признаков. 
   - Исправление некорректной типизации данных. Выделение новых признаков.
   - Визуализация, анализ корреляции данных. Выявление иных зависимостей.
   - Обучение моделей с использованием линейной регрессии, Ridge, Lasso, ElasticNet. Регуляризация. Кросс-валидация, подбор гиперпараметров.
   - Оценка метрик качества и оценка моделей по R², MSE и бизнес метрикам.
2. Разработан REST API с использованием FastAPI:
   - Эндпоинты для предсказания стоимости одной машины и загрузки файла с данными для массового предсказания.
3. Подготовлен `pickle` файл с моделью и коэффициентами для предобработки.

## Результаты
- Модель обучена с использованием Ridge регрессии.
- Лучшие метрики:
  - R² на тестовой выборке: **0.89**
  - Средняя квадратическая ошибка (MSE): **60977850270.61**
- Наибольший буст качества дали:
  - Добавление в модель категориальных признаков и их дальнейшее кодирование с помощью OneHotEncoder.


## Демонстрация работы
### 1. Запуск сервера
Запуск сервера локально через run.py
![run.py](https://github.com/Archi20Rad/HSE/blob/main/ML/HW1_pro/screenshot_1.png)

### 2. Swagger UI
Сервис предоставляет документацию для API, доступную по адресу:
[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

![Swagger UI](https://github.com/Archi20Rad/HSE/blob/main/ML/HW1_pro/screenshot_2.png)

---

### 3. Пример запроса `/predict_item`
Пример запроса для предсказания стоимости одного автомобиля:

![Predict Item](https://github.com/Archi20Rad/HSE/blob/main/ML/HW1_pro/screenshot_3.png)

---

### 4. Пример запроса `/predict_items`
Пример загрузки CSV-файла и получения предсказаний:

![Predict Items](https://github.com/Archi20Rad/HSE/blob/main/ML/HW1_pro/screenshot_4.png)

Скачанный файл содержит следующий результат:

![predictions.csv](https://github.com/Archi20Rad/HSE/blob/main/ML/HW1_pro/predictions.csv)

---

## Что сделать не вышло
1. Не удалось сделать Feature Engineering, просто времени не хватило. 