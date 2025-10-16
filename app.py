from flask import Flask, request, jsonify, send_from_directory, Response, make_response
from flask_cors import CORS
import os
import json
import shutil
from database import db_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
COVER_FOLDER = "images"
BOOKS_FILE = "books.json"
LOGIN_FILE = "login.json"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)
db_session = Session()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COVER_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["COVER_FOLDER"] = COVER_FOLDER

ADMIN_USERNAME = "adminstrator"
ADMIN_PASSWORD = "qwertyuiopasdfghjklzxcvbnm"

#audio yuklash

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"message": "Audio fayl yuklanmadi!"}), 400

    file = request.files['audio']
    book_title = request.form.get("title")
    audio_name = request.form.get("audio_name")  # Foydalanuvchi kiritgan nom

    if not book_title:
        return jsonify({"message": "Kitob nomi kerak!"}), 400

    if not audio_name:
        return jsonify({"message": "Audio nomi kiritilishi shart!"}), 400

    if file and allowed_file(file.filename):
        # Foydalanuvchi kiritgan nomni fayl kengaytmasi bilan birga yaratamiz
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        new_filename = secure_filename(audio_name) + "." + file_extension

        # Kitobga mos `audios/` papkasini yaratamiz
        book_folder = os.path.join(app.config['UPLOAD_FOLDER'], book_title, 'audios')
        os.makedirs(book_folder, exist_ok=True)

        # Yangi nom bilan faylni saqlaymiz
        file_path = os.path.join(book_folder, new_filename)
        file.save(file_path)

        return jsonify({"message": "Audio fayl muvaffaqiyatli yuklandi!", "file_path": file_path}), 200
    else:
        return jsonify({"message": "Noto‘g‘ri fayl formati! Faqat MP3 formatlar ruxsat etiladi."}), 400

@app.route("/users/block/<username>", methods=["PUT"])
def toggle_block_user(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            user["isBlocked"] = not user.get("isBlocked", False)  # Block yoki unblock qilish
            save_users(users)
            status = "Bloklandi" if user["isBlocked"] else "Blokdan chiqarildi"
            return jsonify({"message": f"✅ {username} {status}!"}), 200
    return jsonify({"error": "❌ Foydalanuvchi topilmadi!"}), 404


@app.route("/uploads/audios/<path:filename>")
def serve_audio(filename):
    if filename.lower().endswith(".mp3"):
        audio_path = os.path.join("uploads/audios", filename)

        if not os.path.exists(audio_path):
            return jsonify({"error": "❌ Audio fayl topilmadi!"}), 404

        def generate():
            with open(audio_path, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk

        response = Response(generate(), mimetype="audio/mpeg")
        response.headers["Content-Disposition"] = "inline"  # Yuklab olishni bloklaydi
        return response

    return jsonify({"error": "❌ Faqat audio fayllar qo‘llaniladi!"}), 403


@app.route("/search", methods=["GET"])
def search_books():
    query = request.args.get("query", "").lower()
    if not query:
        return jsonify([])  # Agar bo‘sh bo‘lsa, bo‘sh ro‘yxat qaytaramiz

    books = load_books()
    results = [book for book in books if query in book["title"].lower()]
    
    return jsonify(results)  # Natijalarni JSON formatida qaytarish






def save_users(users):
    with open(LOGIN_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)







# 📥 **Kitob yuklash (bloklangan foydalanuvchi yuklay olmaydi)**
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Fayl topilmadi!"}), 400

    file = request.files["file"]
    cover = request.files.get("cover")
    title = request.form.get("title", "Noma'lum Kitob").strip()
    username = request.form.get("username")

    if not username:
        return jsonify({"error": "Foydalanuvchi nomi talab qilinadi!"}), 400

    # 🚨 **Foydalanuvchi bloklanganligini tekshirish**
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)

    if not user:
        return jsonify({"error": "Foydalanuvchi topilmadi!"}), 404
    if user.get("isBlocked", False):  # `isBlocked` True bo'lsa, yuklash taqiqlanadi
        return jsonify({"error": "Siz bloklangansiz, kitob yuklay olmaysiz! agar kitob yuklashingiz zarur bo'lsa profil sahifasining pastki qismida admin bilan bog'lanish uchun havola mavjud"}), 403

    # 📚 **Kitob nomi bo‘yicha takrorlanish oldini olish**
    books = load_books()
    for book in books:
        if book["title"].lower() == title.lower():
            return jsonify({"message": "Bunday nomdagi kitob allaqachon mavjud!"}), 400

    # 📂 **Yangi papka yaratish (kitob nomiga mos)**
    book_folder = os.path.join(app.config["UPLOAD_FOLDER"], title)
    os.makedirs(book_folder, exist_ok=True)

    # 📥 **Faylni saqlash**
    file_path = os.path.join(book_folder, "kitob.pdf")
    file.save(file_path)

    # 📸 **Muqovani saqlash**
    cover_path = os.path.join(app.config["COVER_FOLDER"], cover.filename) if cover and cover.filename else "images/default-book.jpg"
    if cover:
        cover.save(cover_path)

    new_book = {
        "title": title,
        "filename": file_path.replace("\\", "/"),  # Windows uchun `\` emas `/` qo‘llaniladi
        "cover": os.path.join(app.config["COVER_FOLDER"], os.path.basename(cover_path)),
        "username": username
    }

    # Kitobni ro'yxatga qo'shamiz
    books.append(new_book)

    # Yangi ro'yxatni JSON faylga saqlaymiz
    save_books(books)

    return jsonify({"message": "✅ Fayl muvaffaqiyatli yuklandi!", "filename": file_path, "cover": cover_path}), 200



def save_books(books):
    with open(BOOKS_FILE, "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)

# 📂 JSON fayllarni yuklash va saqlash funksiyalari
def load_books():
    with open(BOOKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)



# 📜 **Barcha kitoblarni olish**
@app.route("/books", methods=["GET"])
def get_books():
    books = load_books()
    return jsonify(books)

@app.route("/book")
def get_book():
    title = request.args.get("title")
    books = load_books()

    for book in books:
        if book["title"] == title:
            if "cover" not in book or not book["cover"].strip():
                book["cover"] = "images/default-book.jpg"  # ⚠ Default rasm
            return jsonify(book)

    return jsonify({"error": "Kitob topilmadi"}), 404

#kitobning audiosini topish
@app.route("/book_audio/<book_title>", methods=["GET"])
def get_book_audio(book_title):
    """Kitob papkasidagi mavjud audio fayllarni qaytaradi"""
    audio_folder = os.path.join(app.config["UPLOAD_FOLDER"], book_title, "audios")

    if not os.path.exists(audio_folder):
        return jsonify({"audio": []})  # Agar audio yo‘q bo‘lsa, bo‘sh ro‘yxat qaytariladi

    audio_files = [f"http://127.0.0.1:5000/uploads/{book_title}/audios/{file}" for file in os.listdir(audio_folder) if file.endswith(".mp3")]

    return jsonify({"audio": audio_files})



# 📌 **Foydalanuvchining shaxsiy kitoblarini olish**
@app.route("/user_books/<username>", methods=["GET"])
def get_user_books(username):
    books = load_books()
    user_books = [book for book in books if book["username"] == username]
    return jsonify(user_books)


# 🗑 **Kitobni o‘chirish**
@app.route("/books/<title>", methods=["DELETE"])
def delete_book_admin(title):
    books = load_books()
    new_books = [book for book in books if book["title"].lower() != title.lower()]
    
    # Kitob papkasining to‘liq yo‘lini aniqlash
    book_folder = os.path.join(UPLOAD_FOLDER, title)
    
    if os.path.exists(book_folder):
        try:
            shutil.rmtree(book_folder)  # Papkani to‘liq o‘chirish
            folder_deleted = True
        except Exception as e:
            folder_deleted = False
            print(f"❌ Papkani o‘chirishda xatolik: {e}")
    else:
        folder_deleted = None  # Papka mavjud emas edi
    
    save_books(new_books)

    # Javob shakllantirish
    if len(books) > len(new_books):
        return jsonify({
            "message": "✅ Kitob o‘chirildi!",
            "folder_deleted": folder_deleted
        })
    else:
        return jsonify({
            "message": "❌ Kitob topilmadi!",
            "folder_deleted": folder_deleted
        })


# 📂 **Yuklangan fayllarni qaytarish**
@app.route("/uploads/<path:filename>")
def download_file(filename):
    # Agar fayl MP3 bo‘lsa, faqat saytda eshitish uchun xizmat qilamiz
    if filename.lower().endswith(".mp3"):
        audio_path = os.path.join("uploads", filename)

        if not os.path.exists(audio_path):
            return jsonify({"error": "❌ Audio fayl topilmadi!"}), 404

        def generate():
            with open(audio_path, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk

        return Response(generate(), mimetype="audio/mpeg")

    # Boshqa fayllarni yuklab olishga ruxsat beramiz
    return send_from_directory("uploads", filename)


#  **Foydalanuvchi ro‘yxatdan o‘tishi**
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return jsonify({"message": "❌ Login va parol talab qilinadi!"}), 400

    users = load_users()
    if any(user["username"] == username for user in users):
        return jsonify({"message": "❌ Bu login allaqachon mavjud!"}), 400

    users.append({
        "username": username,
        "password": password,
        "isBlocked": True
    })
    save_users(users)
    return jsonify({"message": "✅ Ro‘yxatdan muvaffaqiyatli o‘tdingiz!"}), 201

def load_users():
    if not os.path.exists(LOGIN_FILE):
        return []
    with open(LOGIN_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

#  **Foydalanuvchi tizimga kirishi**
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")

    #  **Admin tekshirish**
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        resp = make_response(jsonify({"message": "✅ Admin panelga xush kelibsiz!", "username": username, "admin": True}))
        resp.set_cookie("user_id", "admin", max_age=60*60*24*30, httponly=True)  # 30 kun saqlanadi
        return resp

    # 📂 **Foydalanuvchilar ro‘yxatini yuklash**
    users = load_users()

    # 🔎 **Foydalanuvchini qidirish va tekshirish**
    for user in users:
        if user["username"] == username:
            if user["password"] != password:
                return jsonify({"message": "❌ Login yoki parol noto‘g‘ri!"}), 401
            

            # ✅ **Muvaffaqiyatli login - Cookie saqlash**
            resp = make_response(jsonify({"message": "✅ Kirish muvaffaqiyatli!", "username": username}))
            resp.set_cookie("user_id", str(user["username"]), max_age=60*60*24*30, httponly=True)  # 30 kun cookie
            return resp

    return jsonify({"message": "❌ Foydalanuvchi topilmadi!"}), 404

# 👥 **Barcha foydalanuvchilar ro‘yxatini olish**
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(load_users())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
