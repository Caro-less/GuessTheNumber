import aiogram, asyncio
from aiogram import Dispatcher, Bot, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from random import randint
from config_reader import config


dp = Dispatcher()
bot = Bot(token=config.bot_token.get_secret_value())
min, max = 0, 100
curr_min, curr_max = 0, 100
curr_guess = -1
curr_num = -1
class Game(StatesGroup):
    before_game = State()
    in_game = State()
    after_game = State()



@dp.message(Command("start"))
async def greet(message: types.Message, state: FSMContext):
    await main_menu(message, message.from_user.full_name, state)

@dp.callback_query(F.data == "menu")
async def greet(query: types.CallbackQuery, state: FSMContext):
    await main_menu(query.message, query.from_user.full_name, state)

async def main_menu(message: types.Message, user_name: str, state: FSMContext):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Ты загадываешь!", callback_data="user_g"), types.InlineKeyboardButton(text = "Я загадываю!", callback_data="bot_g")]
    ])
    await message.answer(f"Привет, {user_name}! Поиграем?", reply_markup = kb)
    await state.set_state(Game.before_game)

@dp.callback_query(F.data == "user_g")
async def begin_game(query: types.CallbackQuery, state: FSMContext):
    global curr_num
    curr_num = randint(min, max)
    await state.update_data(mode="bot")
    await query.message.answer(f"Отлично, я загадал число от {min} до {max}! \nПиши свои догадки")
    await state.set_state(Game.in_game)

@dp.callback_query(F.data == "bot_g")
async def begin_game(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(mode="user")
    await query.message.answer(f"Хорошо, загадай число от от {min} до {max}, а я попытаюсь угадать. Готов?\n\nПиши 'больше', 'меньше' или 'угадал'")
    await state.set_state(Game.in_game)
    await asyncio.sleep(1)
    await guess_num(query.message)
    
async def guess_num(message: types.Message):
    global curr_guess
    curr_guess = randint(curr_min, curr_max)
    await message.answer(f"Мне кажется, это число {curr_guess}")
    

@dp.message(Game.in_game)    
async def start(message: types.Message, state: FSMContext):
    msg = message.text
    data = await state.get_data()
    mode = data["mode"]
    global curr_min
    global curr_max
    global curr_guess
    if mode == "bot":
        if not msg.isdigit():
            await message.answer("Пожалуйста, введи число 🙂")
            return    
        if int(msg)>curr_num:
            await message.answer("Меньше!")
        elif int(msg)<curr_num:
            await message.answer("Больше")
        else:
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Еще раз!", callback_data="menu")]
        ])
            await message.answer("Угадал! Сыграем еще?", reply_markup=kb)
            await set_default_values()
            await state.set_state(Game.after_game)
        
    if mode == "user":
        if msg=="больше":
            curr_min = curr_guess+1
            await guess_num(message)
        elif msg=="меньше":
            curr_max = curr_guess-1
            await guess_num(message)
        elif msg=="угадал":
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Еще раз!", callback_data="menu")]
        ])
            await message.answer("Ура! Сыграем еще раз?", reply_markup=kb)
            await set_default_values()
            await state.set_state(Game.after_game)
        else:
            message.answer("Извини, я тебя не понимаю. Пожалуйста, повтори")

async def set_default_values():
    global curr_guess
    global curr_min
    global curr_max
    curr_min, curr_max, curr_guess = 0, 100, -1
    

async def main():
    # Старт поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
