import asyncio

from aiogram import types

from data.config import ADMINS
from loader import dp, db, bot
from aiogram.dispatcher import FSMContext


@dp.message_handler(text="/reklama", user_id=ADMINS)
async def send_ad_to_all(message: types.Message, state: FSMContext):
    await message.answer("Xabaringizni yuboring")
    await state.set_state("xabar")


@dp.message_handler(state="xabar")
async def add_product_1(message: types.Message, state: FSMContext):
    users = await db.select_all_users()
    x = message.text
    for user in users:
        # print(user[3])
        user_id = users[3]
        await bot.send_message(
            chat_id=user_id, text=x
        )

        await asyncio.sleep(0.05)
    await state.finish()
    
@dp.message_handler(text="/tovar",user_id=ADMINS)
async def add_product(message: types.Message,state: FSMContext):
    await message.answer("Ma'lumotni bering")
    await state.set_state('tovar_nomi')

@dp.message_handler(state="tovar_nomi")
async def add_product_1(message: types.Message, state: FSMContext):
    await message.answer("Qabul qilindi")
    l = message.text
    print(l)
    l = list(l.split("|"))
    print(0, l[0])
    print(1,l[1])
    print(2,l[2])
    print(3, l[3])
    print(4, l[4])
    print(5, l[5])
    print(6, l[6])
    print(7, l[7])
    print("-------")
    l[0] = l[0].replace(" ","")
    l[1] = l[1].replace(" ","")
    l[2] = l[2].replace(" ","")
    l[3] = l[3].replace(" ","")
    l[4] = l[4].replace(" ","")
    l[5] = l[5].replace(" ","")
    l[6] = l[6].replace(" ","")
    print(0, l[0])
    print(1,l[1])
    print(2,l[2])
    print(3, l[3])
    print(4, l[4])
    print(5, l[5])
    print(6, l[6])
    print(7, l[7])
    await db.add_product(category_code=l[0],category_name=l[1],subcategory_code=l[2],subcategory_name=l[3],productname=l[4],photo=l[5],price=int(l[6]),description=l[7])
    await message.answer("Qabul qilindi")
    await state.finish()