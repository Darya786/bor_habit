import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database import init_db, get_habits, add_habit, delete_habit

from config import TOKEN 

bot = Bot(token=TOKEN)
dp = Dispatcher()

class HabitForm(StatesGroup):
    waiting_for_habit_name = State()

def get_main_menu():
    button1 = InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_habit")
    button2 = InlineKeyboardButton(text="📊 Мои привычки", callback_data="show_habits")
    return InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]])

def get_cancel_menu():
    button = InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет! Я твой умный трекер привычек! 🚀\nВыберите действие:",
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "cancel_action")
async def process_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Действие отменено")
    await callback.message.answer("Главное меню:", reply_markup=get_main_menu())

@dp.callback_query(F.data == "show_habits")
async def process_show_habits(callback: types.CallbackQuery):
    user_habits = await get_habits(callback.from_user.id)
    await callback.answer()
    
    if not user_habits:
        await callback.message.answer("У вас пока нет сохраненных привычек! 😔", reply_markup=get_main_menu())
    else:
        await callback.message.answer("📋 Ваши привычки:\n(Нажмите 🗑️ рядом с привычкой, чтобы удалить её)")
        
        for habit_id, habit_name in user_habits:
            delete_btn = InlineKeyboardButton(text=f"🗑️ Удалить «{habit_name}»", callback_data=f"delete_{habit_id}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[delete_btn]])
            await callback.message.answer(f"🔹 {habit_name}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("delete_"))
async def process_delete_habit(callback: types.CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    
    await delete_habit(habit_id, callback.from_user.id)
    await callback.answer("Привычка удалена!")
    
    await callback.message.edit_text("❌ *Привычка была удалена*", parse_mode="Markdown")

@dp.callback_query(F.data == "add_habit")
async def process_add_habit(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Напишите название привычки (например: 'Учить Python 30 минут'):",
        reply_markup=get_cancel_menu()
    )
    await state.set_state(HabitForm.waiting_for_habit_name)

@dp.message(HabitForm.waiting_for_habit_name)
async def process_habit_name(message: types.Message, state: FSMContext):
    habit_name = message.text
    await add_habit(message.from_user.id, habit_name)
    await state.clear()
    
    await message.answer(
        f"✅ Привычка «{habit_name}» успешно сохранена!",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def main():
    await init_db()
    print("База данных подключена! Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())