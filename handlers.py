from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import FSInputFile
from config import ADMIN_IDS, OPEN_CHANNEL, CLOSED_GROUP_ID
from db import is_admin, get_test_by_code, save_test, save_result, get_user_tests, get_test_results, get_excel_data, get_user_results, delete_test
from utils import generate_test_code, results_to_excel, format_datetime
import os

router = Router()

# --- FSM holatlari ---
class AdminStates(StatesGroup):
    waiting_test_name = State()
    waiting_question_count = State()
    waiting_answers = State()

class UserStates(StatesGroup):
    waiting_test_code = State()
    waiting_full_name = State()
    waiting_user_answers = State()

# Majburiy obuna tekshiruvi
async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(OPEN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- START HANDLER ---
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not await check_subscription(user_id, message.bot):
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Tekshirish")]], resize_keyboard=True)
        await message.answer(
            f"🛑 Botdan foydalanishdan oldin quyidagi kanalga obuna bo‘ling:\n\n📢 {OPEN_CHANNEL}\n\n✅ Obuna bo‘lgach, “Tekshirish” tugmasini bosing.",
            reply_markup=kb
        )
        return
    # Obuna bo'lganlar uchun asosiy menyu
    if is_admin(user_id) or user_id in ADMIN_IDS:
        await show_admin_menu(message)
    else:
        await show_user_menu(message)

# --- TEKSHIRISH TUGMASI HANDLERI ---
@router.message(F.text == "Tekshirish")
async def tekshirish_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if await check_subscription(user_id, message.bot):
        # Obuna bo'lganlar uchun asosiy menyu
        if is_admin(user_id) or user_id in ADMIN_IDS:
            await message.answer("🎉 Obuna tasdiqlandi!", reply_markup=ReplyKeyboardRemove())
            await show_admin_menu(message)
        else:
            await message.answer("🎉 Obuna tasdiqlandi!", reply_markup=ReplyKeyboardRemove())
            await show_user_menu(message)
    else:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Tekshirish")]], resize_keyboard=True)
        await message.answer(
            f"❗ Obuna bo‘lmagansiz. Iltimos, avval kanalga a'zo bo‘ling!\n\n📢 {OPEN_CHANNEL}",
            reply_markup=kb
        )

# --- ADMIN PANEL ---
async def show_admin_menu(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Test yaratish")],
            [KeyboardButton(text="📋 Mening testlarim"), KeyboardButton(text="🧾 Test natijalari")],
            [KeyboardButton(text="🗑 Testni o‘chirish"), KeyboardButton(text="📤 Excel yuklash")],
            [KeyboardButton(text="🔙 Bosh menyu")],
        ], resize_keyboard=True
    )
    await message.answer("🔐 Admin panelga xush kelibsiz!", reply_markup=kb)

# --- USER MENU ---
async def show_user_menu(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧪 Test ishlash")],
            [KeyboardButton(text="📊 Mening natijalarim")],
            [KeyboardButton(text="📌 Yordam")],
            [KeyboardButton(text="©️Bot haqida")],
        ], resize_keyboard=True
    )
    await message.answer("🎉 Xush kelibsiz! Siz endi test ishlashingiz mumkin.", reply_markup=kb)

@router.message(F.text == "©️Bot haqida")
async def bot_haqida_handler(message: Message):
    await message.answer(
        "Ushbu bot @Tolov_admini_btu tomonidan yaratildi, sizga ham turli telegram botlar va saytlar kerak bo‘lsa murojaat qiling!"
    )

@router.message(F.text == "📌 Yordam")
async def yordam_handler(message: Message):
    await message.answer(
        "Test ishlashda qandaydir muammolar bo'lsa savol va tajlif uchun murojjat qiling!\n 👉 @NChBadmin0309"
    )

# --- ADMIN: TEST YARATISH JARAYONI ---
@router.message(F.text == "➕ Test yaratish")
async def admin_create_test(message: Message, state: FSMContext):
    await message.answer("📝 Test nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminStates.waiting_test_name)

@router.message(AdminStates.waiting_test_name)
async def admin_test_name(message: Message, state: FSMContext):
    await state.update_data(test_name=message.text)
    await message.answer("🔢 Savollar sonini kiriting:")
    await state.set_state(AdminStates.waiting_question_count)

@router.message(AdminStates.waiting_question_count)
async def admin_question_count(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, raqam kiriting!")
        return
    await state.update_data(question_count=int(message.text))
    await message.answer("✅ To‘g‘ri javoblarni kiriting (masalan: A B B B, abbbab, ABABABA):")
    await state.set_state(AdminStates.waiting_answers)

@router.message(AdminStates.waiting_answers)
async def admin_answers(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        # Harflarni qabul qilish: A B B B, abbbab, ABABABA barchasi uchun
        javob_text = message.text.strip().replace(' ', '').upper()
        answers = list(javob_text)
        if len(answers) != data['question_count']:
            await message.answer(f"Javoblar soni {data['question_count']} ta bo'lishi kerak!")
            return
        # Test kodini generatsiya qilamiz
        code = generate_test_code()
        # Testni bazaga yozish
        save_test(code, data['test_name'], data['question_count'], ' '.join(answers), message.from_user.id)
        # To'liq xabar chiqarish
        await message.answer(
            f"✅️Test ishlanishga tayyor\n"
            f"🗒Test nomi: {data['test_name']}\n"
            f"🔢Testlar soni: {data['question_count']} ta\n"
            f"‼️Test kodi: {code}\n\n"
            f"Test javoblaringizni quyidagi botga jo'nating:\n"
            f"👉 @test_tekshiruvchinewbot\n\n"
            f"Testda qatnashuvchilar quyidagicha javob yuborishlari mumkin:\n\n"
            f"🧪 Test ishlash tugmasini bosing va yuqoridagi kodni kiriting hamda javoblarni yuboring!\n\n"
            f"Namuna javob yuborish :\n"
            f"ACBD...\n"
            f"yoki\n"
            f"abcd...\n\n"
            f"✅ Test ishlanishga tayyor!!!"
        )
        await show_admin_menu(message)
        await state.clear()
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")
        await show_admin_menu(message)
        await state.clear()

# --- USER: TEST ISHLASH JARAYONI ---
@router.message(F.text == "🧪 Test ishlash")
async def user_start_test(message: Message, state: FSMContext):
    await message.answer("🔢 Test kodini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.waiting_test_code)

@router.message(UserStates.waiting_test_code)
async def user_enter_test_code(message: Message, state: FSMContext):
    try:
        code = message.text.strip().upper()
        test = get_test_by_code(code)
        if not test:
            await message.answer("❗ Test kodi noto'g'ri. Qayta urinib ko'ring.")
            return
        await state.update_data(test_code=code, test_name=test[0], question_count=test[1])
        await message.answer("Ism va familiyangizni kiriting:")
        await state.set_state(UserStates.waiting_full_name)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")
        await show_user_menu(message)
        await state.clear()

@router.message(UserStates.waiting_full_name)
async def user_enter_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    data = await state.get_data()
    await message.answer(f"✍️ Javoblaringizni quyidagi formatda yuboring:\nabcd yoki ABCD(jami {data['question_count']} ta harf)")
    await state.set_state(UserStates.waiting_user_answers)

@router.message(UserStates.waiting_user_answers)
async def user_send_answers(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        # Harflarni qabul qilish: A B C D, abcd, ABCD, abca, ABABC barchasi uchun
        user_text = message.text.strip().replace(' ', '').upper()
        user_answers = list(user_text)
        if len(user_answers) != data['question_count']:
            await message.answer(f"Javoblar soni {data['question_count']} ta bo'lishi kerak!")
            return
        
        # To'g'ri javoblarni bazadan olamiz
        test_data = get_test_by_code(data['test_code'])
        if not test_data:
            await message.answer("Test topilmadi. Qayta urinib ko'ring.")
            return
            
        correct_answers = [a.upper() for a in test_data[2].split()]
        natija_lines = []
        correct_count = 0
        for i, (user, correct) in enumerate(zip(user_answers, correct_answers), 1):
            if user == correct:
                natija_lines.append(f"{i}. {user} ✅        1 ball")
                correct_count += 1
            else:
                natija_lines.append(f"{i}. {user} ❌({correct})   0 ball")
        total = data['question_count']
        
        # Natijani bazaga yozamiz
        save_result(
            message.from_user.id, 
            data['full_name'], 
            data['test_code'], 
            ' '.join(user_answers), 
            correct_count, 
            total, 
            int(correct_count*100/total), 
            format_datetime()
        )
        
        # Foydalanuvchiga natijani ko'rsatamiz
        natija_text = (
            f"{data['full_name']} ning natijasi\n\n"
            f"📌Test kodi: {data['test_code']}\n"
            f"Test nomi: {data['test_name']}\n"
            f"📋Savollar soni: {total} ta\n\n"
            f"Natijalari:\n"
            + '\n'.join(natija_lines) +
            f"\n\n📊Jami: {correct_count} ball"
        )
        await message.answer(natija_text)
        
        # Yopiq guruhga natijani yuborish
        try:
            await message.bot.send_message(CLOSED_GROUP_ID, natija_text)
        except Exception as e:
            pass  # Guruhga yuborishda xatolik bo'lsa jim turadi
            
        await show_user_menu(message)
        await state.clear()
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")
        await show_user_menu(message)
        await state.clear()

# --- ADMIN: MENING TESTLARIM ---
@router.message(F.text == "📋 Mening testlarim")
async def admin_my_tests(message: Message):
    try:
        tests = get_user_tests(message.from_user.id)
        if not tests:
            await message.answer("Sizda hali testlar yo'q.")
            return
        text = "Siz yaratgan testlar:\n\n"
        for code, name, count in tests:
            text += f"📝 {name}\n🔢 Savollar: {count}\n‼️ Kod: {code}\n\n"
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

# --- ADMIN: TEST NATIJALARI ---
@router.message(F.text == "🧾 Test natijalari")
async def admin_test_results(message: Message):
    try:
        results = get_test_results(message.from_user.id)
        if not results:
            await message.answer("Sizda hali testlar yo'q.")
            return
        text = "Test natijalari:\n\n"
        for code, name, count, avg_percent in results:
            text += f"📝 {name}\n‼️ Kod: {code}\n👥 Ishlaganlar: {count} ta\n🎯 O'rtacha foiz: {avg_percent}%\n\n"
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

# --- ADMIN: TESTNI O'CHIRISH ---
@router.message(F.text == "🗑 Testni o'chirish")
async def admin_delete_test(message: Message, state: FSMContext):
    try:
        tests = get_user_tests(message.from_user.id)
        if not tests:
            await message.answer("Sizda o'chirish uchun test yo'q.")
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{name} ({code})", callback_data=f"deltest_{code}")]
            for code, name, _ in tests
        ])
        await message.answer("O'chirish uchun testni tanlang:", reply_markup=kb)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

@router.callback_query(F.data.startswith("deltest_"))
async def delete_test_callback(call: CallbackQuery):
    try:
        code = call.data.replace("deltest_", "")
        delete_test(code)
        await call.message.edit_text(f"Test va natijalari o'chirildi! Kod: {code}")
    except Exception as e:
        await call.message.edit_text(f"Xatolik yuz berdi: {str(e)}")

# --- ADMIN: EXCEL YUKLASH ---
@router.message(F.text == "📤 Excel yuklash")
async def admin_excel_download(message: Message):
    try:
        rows = get_excel_data(message.from_user.id)
        if not rows:
            await message.answer("Natijalar yo'q.")
            return
        results = []
        for row in rows:
            results.append({
                'Foydalanuvchi': row[0],
                'Test kodi': row[1],
                'Test nomi': row[2],
                'Javoblar': row[3],
                'To'g'ri': row[4],
                'Jami': row[5],
                'Foiz': row[6],
                'Vaqt': row[7],
            })
        filename = f"test_natijalar_{message.from_user.id}.xlsx"
        results_to_excel(results, filename)
        await message.answer_document(FSInputFile(filename))
        os.remove(filename)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}") 

@router.message(F.text == "📊 Mening natijalarim")
async def user_my_results(message: Message):
    try:
        rows = get_user_results(message.from_user.id)
        if not rows:
            await message.answer("Siz hali birorta test ishlamagansiz.")
            return
        text = "Sizning natijalaringiz:\n\n"
        for code, name, correct, total, percent, date in rows:
            text += (f"📌Test kodi: {code}\n"
                     f"Test nomi: {name}\n"
                     f"✅ Ball: {correct}/{total}\n"
                     f"🎯 Foiz: {percent}%\n"
                     f"🕒 Sana: {date}\n\n")
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}") 