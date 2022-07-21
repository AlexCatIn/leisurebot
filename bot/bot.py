import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import schedule


from crawler.moviedb import Movie, Cinema, Book
from crawler.htmlparser import get_cinema, get_book, get_movie
from .config import TOKEN


available_city_names = ["Ростов-на-Дону", "Москва", "Санкт-Петербург", "Сочи"]
available_interests = ["Кино дома", "Книги", "Фильмы в кинотеатре"]

class ChoosingActivity(StatesGroup):
    waiting_for_city_name = State()
    waiting_for_intrests = State()

async def activity_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_city_names:
        keyboard.add(name)
    await message.answer("Выберите город:", reply_markup=keyboard)
    await ChoosingActivity.waiting_for_city_name.set()

async def city_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_city_names:
        await message.answer("Пожалуйста, выберите город, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_city=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for interests in available_interests:
        keyboard.add(interests)
    await ChoosingActivity.next()
    await message.answer("Теперь выберите Ваши интересы:", reply_markup=keyboard)

async def interest_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_interests:
        await message.answer("Пожалуйста, выберите интерес, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_interest=message.text)
    user_data = await state.get_data()
    if message.text == "Кино дома":
        movie_answer = " "
        for movie in Movie.select().limit(10).order_by(Movie.movie_id.desc()):
            movie_answer += f' * {movie.name_russian} | {movie.movie_url} \n'
        await message.answer(movie_answer, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    elif message.text == "Книги":
        book_answer = " "
        for book in Book.select().limit(20).order_by(Book.book_id.desc()):
            book_answer += f' * {book.name_russian} | {book.author} | {book.rate} | {book.book_url} \n'
        await message.answer(book_answer, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    elif message.text == "Фильмы в кинотеатре":
        cinema_answer = " "
        for cinema in Cinema.select().limit(8).order_by(Cinema.cinema_id.desc()):
            cinema_answer += f' * {cinema.name_russian} | {cinema.cinema_genre} | {cinema.cinema_url} \n'
        await message.answer(cinema_answer, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()    
    else:    
        await message.answer(f"Вы выбрали {message.text} в городе {user_data['chosen_city']}.\n" , reply_markup=types.ReplyKeyboardRemove())
        await state.finish()

def register_handlers_activity(dp: Dispatcher):
    dp.register_message_handler(activity_start, commands="activity", state="*")
    dp.register_message_handler(city_chosen, state=ChoosingActivity.waiting_for_city_name)
    dp.register_message_handler(interest_chosen, state=ChoosingActivity.waiting_for_intrests)


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Выберите, чем хотите заниматься: активности (/activity).",
        reply_markup=types.ReplyKeyboardRemove()
    )

async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())

def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/activity", description="Выбрать интересы"),
        BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    logging.basicConfig(level=logging.INFO)

    register_handlers_common(dp)
    register_handlers_activity(dp)

    await set_commands(bot)

    await dp.start_polling()


def job():
    get_movie()
    get_book()
    get_cinema()
    
schedule.every().thursday.do(job)


def run_bot():
    asyncio.run(main())
    while True:
        schedule.run_pending()
