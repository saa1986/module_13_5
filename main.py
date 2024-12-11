"""Необходимо дополнить код предыдущей задачи, чтобы вопросы о параметрах тела для расчёта калорий выдавались по нажатию кнопки.
Измените massage_handler для функции set_age. Теперь этот хэндлер будет реагировать на текст 'Рассчитать', а не на 'Calories'.
Создайте клавиатуру ReplyKeyboardMarkup и 2 кнопки KeyboardButton на ней со следующим текстом: 'Рассчитать' и
'Информация'. Сделайте так, чтобы клавиатура подстраивалась под размеры интерфейса устройства при помощи параметра resize_keyboard.
Используйте ранее созданную клавиатуру в ответе функции start, используя параметр reply_markup.
В итоге при команде /start у вас должна присылаться клавиатура с двумя кнопками. При нажатии на кнопку с надписью
'Рассчитать' срабатывает функция set_age с которой начинается работа машины состояний для age, growth"""

from aiogram import Bot, Dispatcher, types  # Импортируем необходимые классы из aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Импортируем хранилище для состояний в памяти
from aiogram.dispatcher import FSMContext  # Импортируем контекст состояния
from aiogram.dispatcher.filters.state import State, StatesGroup  # Импортируем классы для работы с состояниями
from aiogram.utils import executor  # Импортируем вспомогательные функции для запуска бота
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # Импортируем классы для создания клавиатуры
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)

button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')

kb.add(button, button2) # Добавляем кнопку 'Рассчитать' в клавиатуру


class UserState(StatesGroup):  # Создаем класс состояний для пользователя
    age = State()  # Определяем состояние для возраста
    growth = State()  # Определяем состояние для роста
    weight = State()  # Определяем состояние для веса


@dp.message_handler(commands=['start'])  # Обработчик на команду /start
async def start(message: types.Message):  # Асинхронная функция для обработки команды
    await message.answer('Привет, я бот помогающий твоему здоровью', reply_markup=kb)  # Ответ пользователю с клавиатурой


# Функция для установки возраста
@dp.message_handler(text='Рассчитать')  # Обработчик на команду /start
async def start(message: types.Message):  # Асинхронная функция для обработки команды
    await message.answer("Введите свой возраст:")  # Ответ пользователю с инструкцией
    await UserState.age.set()  # Переходим к состоянию age


# Функция для установки возраста
@dp.message_handler(text='Информация')  # Обработчик на команду /start
async def info(message: types.Message):  # Асинхронная функция для обработки команды
    await message.answer("о информации:", reply_markup=kb)  # Ответ пользователю с инструкцией


# Функция для установки роста
@dp.message_handler(state=UserState.age)  # Обработчик на состояние UserState.age
async def set_growth(message: types.Message, state: FSMContext):  # Асинхронная функция для установки роста
    await state.update_data(age=message.text)  # Сохраняем введенный возраст в состоянии
    await message.answer('Введите свой рост:')  # Запрашиваем у пользователя рост
    await UserState.growth.set()  # Переходим к состоянию growth


# Функция для установки веса
@dp.message_handler(state=UserState.growth)  # Обработчик на состояние UserState.growth
async def set_weight(message: types.Message, state: FSMContext):  # Асинхронная функция для установки веса
    await state.update_data(growth=message.text)  # Сохраняем введенный рост в состоянии
    await message.answer('Введите свой вес:')  # Запрашиваем у пользователя вес
    await UserState.weight.set()  # Переходим к состоянию weight


# Функция для отправки нормы калорий
@dp.message_handler(state=UserState.weight)  # Обработчик на состояние UserState.weight
async def send_calories(message: types.Message, state: FSMContext):  # Асинхронная функция для вычисления калорий
    await state.update_data(weight=message.text)  # Сохраняем введенный вес в состоянии

    data = await state.get_data()  # Получаем все данные из состояния
    age = int(data['age'])  # Извлекаем возраст и преобразуем в целое число
    growth = int(data['growth'])  # Извлекаем рост и преобразуем в целое число
    weight = int(data['weight'])  # Извлекаем вес и преобразуем в целое число

    # Формула Миффлина - Сан Жеора для женщин (можно изменить для мужчин)
    calories = 655 + (9.6 * weight) + (1.8 * growth) - (4.7 * age)  # Вычисляем норму калорий

    await message.answer(f'Ваша норма калорий: {calories:.2f} ккал.')  # Отправляем результат пользователю
    await state.finish()  # Завершаем машину состояний


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == '__main__':  # Проверяем, что этот файл запускается как основной
    executor.start_polling(dp, skip_updates=True)  # Запускаем бота, пропуская обновления

