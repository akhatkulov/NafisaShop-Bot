from typing import Union

from aiogram import types
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup,KeyboardButton
from aiogram.dispatcher import FSMContext
from data.config import ADMINS
from states import *
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.inline.menu_keyboards import (
    menu_cd,
    buy_item,
    categories_keyboard,
    subcategories_keyboard,
    items_keyboard,
    item_keyboard,
)
from loader import dp, db

# Bosh menyu matni uchun handler
@dp.message_handler(text="Bosh menyu")
async def show_menu(message: types.Message):
    # Foydalanuvchilarga barcha kategoriyalarni qaytaramiz
    await list_categories(message)


# Kategoriyalarni qaytaruvchi funksiya. Callback query yoki Message qabul qilishi ham mumkin.
# **kwargs yordamida esa boshqa parametrlarni ham qabul qiladi: (category, subcategory, item_id)
async def list_categories(message: Union[CallbackQuery, Message], **kwargs):
    # Keyboardni chaqiramiz
    markup = await categories_keyboard()

    # Agar foydalanuvchidan Message kelsa Keyboardni yuboramiz
    if isinstance(message, Message):
        await message.answer("Bo'lim tanlang", reply_markup=markup)

    # Agar foydalanuvchidan Callback kelsa Callback natbibi o'zgartiramiz
    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)


# Ost-kategoriyalarni qaytaruvchi funksiya
async def list_subcategories(callback: CallbackQuery, category, **kwargs):
    markup = await subcategories_keyboard(category)

    # Xabar matnini o'zgartiramiz va keyboardni yuboramiz
    await callback.message.edit_reply_markup(markup)


# Ost-kategoriyaga tegishli mahsulotlar ro'yxatini yuboruvchi funksiya
async def list_items(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory)

    await callback.message.edit_text(text="Mahsulot tanlang", reply_markup=markup)


# Biror mahsulot uchun Xarid qilish tugmasini yuboruvchi funksiya
async def show_item(callback: CallbackQuery, category, subcategory, item_id):
    markup = item_keyboard(category, subcategory, item_id)

    # Mahsulot haqida ma'lumotni bazadan olamiz
    item = await db.get_product(item_id)

    if item["photo"]:
        text = f"<a href=\"{item['photo']}\">{item['productname']}</a>\n\n"
    else:
        text = f"{item['productname']}\n\n"
    text += f"Narxi: {item['price']}So'm\n{item['description']}"

    await callback.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(buy_item.filter(),state=None)
async def buy(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    data = callback_data['item_id']
    await state.update_data(
        {"item_id": data}
    )
    try:
        fullname_msg = await call.message.answer(f"👤Ism Familiyangiz yuboring!")
        await PersonalData.fullName.set()
    except:
        await state.finish()
    
#
# Foydanuvchini Ism va Familiyasi olamiz
@dp.message_handler(state=PersonalData.fullName)
async def answer_fullname(message: types.Message, state: FSMContext):
    try:
        fullname = message.text
        await state.update_data(
            {"name": fullname}
        )
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        phone_button = KeyboardButton(text="☎️ Yuborish", request_contact=True)
        keyboard.add(phone_button)

        await message.answer("📞Telefon raqamingizni yuboring.",reply_markup=keyboard)

        await PersonalData.phoneNum.set()
    except:
        await state.finish()
async def show_item1(item_id):

    item = await db.get_product(item_id)

    if item["photo"]:

        text = f"<a href=\"{item['photo']}\"> 🚘Tovar Nomi: {item['productname']} </a>\n"
    else:
        text = f"{item['productname']}\n\n"
    text += f"💸Narxi: {item['price']}$\n\n<b>Tovar Haqida👇</b>\n<i>    {item['description']}</i>\n"

    return text

@dp.message_handler(content_types=types.ContentType.CONTACT,state=PersonalData.phoneNum)
async def answer_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    user_id = message.from_user.id
    username = message.from_user.username
    await state.update_data(
        {"phone": phone,
         'username': username,
         'user_id': user_id}
    )
    data = await state.get_data()
    name = data.get("name")
    phone = data.get("phone")
    item_id = data.get('item_id')
    ariza = "<b>📩Foydalanuvchidan Kelgan Ariza Mavjud!</b>\n\n"
    ariza += f"👤Ism Familiya: {name}\n"
    ariza += f"📞Telefon raqam: {phone}\n"
    ariza += f"✅Username: @{username}\n"
    ariza += f"🆔Telegram_id:{user_id}\n\n"
    ariza += f"<b>🔰Tovar haqida Malumot.</b>\n\n"
    ariza += await show_item1(item_id)

    await dp.bot.send_message(ADMINS[0],ariza)
    msg = "✅Malumotlaringiz Qabul Qilindi Adminlarimiz tez orada siz bilan bo'g'lanishadi."

    await message.answer(msg)
    await state.finish()


# Yuqoridagi barcha funksiyalar uchun yagona handler
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict):
    """
    :param call: Handlerga kelgan Callback query
    :param callback_data: Tugma bosilganda kelgan ma'lumotlar
    """

    # Foydalanuvchi so'ragan Level (qavat)
    current_level = callback_data.get("level")

    # Foydalanuvchi so'ragan Kategoriya
    category = callback_data.get("category")

    # Ost-kategoriya (har doim ham bo'lavermaydi)
    subcategory = callback_data.get("subcategory")

    # Mahsulot ID raqami (har doim ham bo'lavermaydi)
    item_id = int(callback_data.get("item_id"))

    # Har bir Level (qavatga) mos funksiyalarni yozib chiqamiz
    levels = {
        "0": list_categories,  # Kategoriyalarni qaytaramiz
        "1": list_subcategories,  # Ost-kategoriyalarni qaytaramiz
        "2": list_items,  # Mahsulotlarni qaytaramiz
        "3": show_item,  # Mahsulotni ko'rsatamiz
    }

    # Foydalanuvchidan kelgan Level qiymatiga mos funksiyani chaqiramiz
    current_level_function = levels[current_level]

    # Tanlangan funksiyani chaqiramiz va kerakli parametrlarni uzatamiz
    await current_level_function(
        call, category=category, subcategory=subcategory, item_id=item_id
    )
