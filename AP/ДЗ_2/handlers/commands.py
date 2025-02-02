from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
import aiohttp
import re
import logging 
from config_reader import config


router = Router()
users = {}

class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()

class FoodState(StatesGroup):
    grams = State()

@router.message(Command("help"))
async def cmd_start(message: Message):
    welcome_text = (
        "👋 Привет! Я ваш персональный помощник по здоровому образу жизни!\n\n"
        "📋 Вот что я умею:\n\n"
        "⚙️ Настройка профиля\n"
        "/set_profile - установить параметры (вес, рост, активность и др.)\n\n"
        "❓️ Информация о профиле\n"
        "/my_profile - вывод информации о профиле\n\n"
        "💧 Учёт воды\n"
        "/log_water <количество> - добавить выпитую воду (в мл)\n\n"
        "🍎 Учёт питания\n"
        "/log_food <продукт> - добавить потреблённые калории\n\n"
        "⚡ Тренировки\n"
        "/log_workout <тип> <минуты> - добавить тренировку\n\n"
        "📊 Отслеживание прогресса\n"
        "/check_progress - показать текущие показатели\n\n"
        "🌍 Для расчётов использую реальные данные о погоде и продуктах!\n"
        "Начните с настройки профиля командой /set_profile"
    )
    await message.answer(welcome_text)

# openweathermap API
async def get_temperature(city: str) -> float:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.OPENWEATHERMAP_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("Город не найден или введен некорректно")
            data = await response.json()
            return data["main"]["temp"]

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await message.answer("Введите ваш вес (в кг):")
    await state.set_state(ProfileStates.weight)

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await message.answer("Введите ваш рост (в см):")
        await state.set_state(ProfileStates.height)
    except ValueError:
        await message.answer("Пожалуйста, введите число.")

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        await state.update_data(height=height)
        await message.answer("Введите ваш возраст:")
        await state.set_state(ProfileStates.age)
    except ValueError:
        await message.answer("Пожалуйста, введите число.")

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer("Сколько минут активности в день?")
        await state.set_state(ProfileStates.activity)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    try:
        activity = int(message.text)
        await state.update_data(activity=activity)
        await message.answer("В каком городе вы находитесь?")
        await state.set_state(ProfileStates.city)
    except ValueError:
        await message.answer("Пожалуйста, введите текст")

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    
    if not re.match(r'^[a-zA-Z\s\'-]+$', city):
        await message.answer("❌ Пожалуйста, используйте английские буквы для названия города")
        return
        
    try:
        temperature = await get_temperature(city)
        data = await state.get_data()
        
        water_base = data["weight"] * 30
        water_activity = (data["activity"] // 30) * 500
        water_weather = 500 if temperature > 25 else 0
        water_goal = water_base + water_activity + water_weather
        
        calorie_base = 10*data["weight"] + 6.25*data["height"] - 5*data["age"] + 5
        calorie_activity = (data["activity"] // 30) * 300
        calorie_goal = calorie_base + calorie_activity
        
        users[message.from_user.id] = {
            **data,
            "city": city,
            "water_goal": water_goal,
            "calorie_goal": calorie_goal,
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0
        }
        await message.answer(f"✅ Профиль сохранен! Для просмотра профиля введите /my_profile")
        
    except ValueError as e:
        await message.answer(f"❌ {str(e)}. Проверьте правильность названия города")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при обработке запроса")
        logging.error(f"Weather API error: {str(e)}")
    
    await state.clear()

@router.message(Command("my_profile"))
async def cmd_my_profile(message: Message):
    user = users.get(message.from_user.id)
    if not user:
        await message.answer("❌ Ваш профиль не настроен. Введите /set_profile")
        return
    
    profile_info = (
        "📋 Ваш профиль:\n\n"
        f"⚖️ Вес: {user['weight']} кг\n"
        f"📏 Рост: {user['height']} см\n"
        f"🎂 Возраст: {user['age']} лет\n"
        f"🏃 Активность: {user['activity']} мин/день\n"
        f"🌍 Город: {user['city']}\n\n"
        f"💧 Дневная норма воды: {user['water_goal']} мл\n"
        f"🔥 Дневная норма калорий: {user['calorie_goal']} ккал"
    )
    
    await message.answer(profile_info)

@router.message(Command("log_water"))
async def cmd_log_water(message: Message):
    try:
        amount = float(message.text.split()[1])
        user = users.get(message.from_user.id)
        if user:
            user["logged_water"] += amount
            remaining = user["water_goal"] - user["logged_water"]
            await message.answer(f"💧 Записано: {amount} мл. Осталось: {max(remaining, 0)} мл")
        else:
            await message.answer("❌ Сначала настройте профиль")
    except (IndexError, ValueError):
        await message.answer("❌ Введите: /log_water <количество>")

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    try:
        product_name = message.text.split(maxsplit=1)[1].strip()
        if not product_name:
            await message.answer("❌ Пожалуйста, укажите название продукта")
            return
        
        url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await message.answer("❌ Ошибка при запросе к API. Попробуйте позже")
                    return
                
                data = await response.json()
                products = data.get("products", [])
                
                if not products:
                    await message.answer("❌ Продукт не найден. Попробуйте другое название")
                    return
                
                first_product = products[0]
                product_name = first_product.get("product_name", "Неизвестный продукт")
                kcal = first_product.get("nutriments", {}).get("energy-kcal_100g", 0)
                
                if not kcal:
                    await message.answer("❌ Не удалось получить информацию о калорийности продукта")
                    return
                
                await message.answer(f"🍎 {product_name} - {kcal} ккал/100г. Сколько грамм вы съели?")
                await state.update_data(kcal=kcal)
                await state.set_state(FoodState.grams)
                
    except IndexError:
        await message.answer("❌ Введите: /log_food <название продукта>")
    except Exception as e:
        await message.answer("❌ Произошла ошибка. Попробуйте позже")
        logging.error(f"Food API error: {str(e)}")

@router.message(FoodState.grams)
async def process_food_grams(message: Message, state: FSMContext):
    try:
        grams = float(message.text)
        data = await state.get_data()
        kcal = (grams / 100) * data["kcal"]
        user = users.get(message.from_user.id)
        if user:
            user["logged_calories"] += kcal
            await message.answer(f"✅ Записано: {round(kcal, 1)} ккал")
        else:
            await message.answer("❌ Сначала настройте профиль")
    except ValueError:
        await message.answer("❌ Введите число")
    await state.clear()

# Workout Logging
@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message):
    try:
        _, workout_type, duration = message.text.split()
        duration = int(duration)
        user = users.get(message.from_user.id)
        if user:
            burned = duration * 10
            water = (duration // 30) * 200
            
            user["burned_calories"] += burned
            user["water_goal"] += water
            
            await message.answer(
                f"⚡ {workout_type} {duration} мин\n"
                f"🔥 Сожжено: {burned} ккал\n"
                f"💧 Выпейте дополнительно: {water} мл"
            )
        else:
            await message.answer("❌ Сначала настройте профиль")
    except Exception:
        await message.answer("❌ Введите: /log_workout <тип> <минуты>")

@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    user = users.get(message.from_user.id)
    if user:
        water_remaining = user["water_goal"] - user["logged_water"]
        calories_remaining = user["calorie_goal"] - (user["logged_calories"] - user["burned_calories"])
        
        response = (
            "📊 Прогресс:\n\n"
            f"💧 Вода: {user['logged_water']}/{user['water_goal']} мл "
            f"(Осталось: {max(water_remaining, 0)} мл)\n\n"
            f"🔥 Калории:\n"
            f"• Потреблено: {user['logged_calories']} ккал\n"
            f"• Сожжено: {user['burned_calories']} ккал\n"
            f"• Баланс: {user['logged_calories'] - user['burned_calories']} ккал\n"
            f"• Цель: {user['calorie_goal']} ккал\n"
            f"• Осталось: {max(calories_remaining, 0)} ккал"
        )
        await message.answer(response)
    else:
        await message.answer("❌ Сначала настройте профиль")