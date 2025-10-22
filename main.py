import os
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Токен из переменной окружения
TOKEN=8329621184:AAE68wWxjTUsbLNorCPNZrtwDzWhAn3GbVg
ADMIN_IDS=495452574

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

tasks = {}  # {message_id: {"task": str, "user": str or None, "time": datetime}}

# Создание новой задачи
@dp.message_handler(commands=["task"])
async def create_task(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Только администраторы могут создавать задачи.")
        return

    text = message.text.replace("/task", "").strip()
    if not text:
        await message.reply("Напиши задачу после команды /task")
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="✅ Взять в работу", callback_data="take_task"))

    sent = await message.answer(
        f"📦 Новая задача:\n{text}\n\n🕒 Нужно взять в течение 15 минут!",
        reply_markup=kb
    )

    tasks[sent.message_id] = {"task": text, "user": None, "time": datetime.now()}

    # Проверка через 15 минут
    await asyncio.sleep(15 * 60)
    if tasks.get(sent.message_id) and tasks[sent.message_id]["user"] is None:
        await message.answer(f"⚠️ Задача не взята в работу:\n{text}")

# Взятие задачи в работу
@dp.callback_query_handler(lambda c: c.data == "take_task")
async def take_task(callback: types.CallbackQuery):
    msg = callback.message
    user = callback.from_user

    if msg.message_id not in tasks or tasks[msg.message_id]["user"]:
        await callback.answer("Эта задача уже взята!", show_alert=True)
        return

    tasks[msg.message_id]["user"] = user.username or user.first_name

    await msg.edit_text(
        f"✅ @{user.username or user.first_name} взял(а) задачу:\n{tasks[msg.message_id]['task']}\n\n🕐 Напоминание через 1 час"
    )

    await callback.answer("Ты взял задачу!")

    # Напоминание через 1 час
    await asyncio.sleep(60 * 60)
    if msg.message_id in tasks and tasks[msg.message_id]["user"] == (user.username or user.first_name):
        await msg.answer(f"⏰ @{user.username or user.first_name}, как прогресс по задаче:\n{tasks[msg.message_id]['task']}?")

# Просмотр всех задач
@dp.message_handler(commands=["tasks"])
async def show_tasks(message: types.Message):
    if not tasks:
        await message.reply("📭 Активных задач нет.")
        return

    text = "📋 Активные задачи:\n"
    for i, (mid, info) in enumerate(tasks.items(), start=1):
        user = info["user"] or "❌ не взята"
        text += f"{i}. {info['task']} — {user}\n"
    await message.reply(text)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp)

