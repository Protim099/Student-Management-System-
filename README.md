# 🎓 Student Management System

একটি সম্পূর্ণ Full-Stack Student Management System — Flask REST API ব্যাকএন্ড + JWT Auth + Vanilla JS/Tailwind CSS ফ্রন্টএন্ড।

## টেক স্ট্যাক

| অংশ | টেকনোলজি |
|---|---|
| Frontend | HTML5, Tailwind CSS (CDN), Vanilla JavaScript |
| Backend | Python + Flask (REST API) |
| Database | SQLite (ডিফল্ট, ডেভ) / PostgreSQL / MySQL |
| Auth | JWT (Flask-JWT-Extended) |

## Folder Structure

```
student-management-system/
├── backend/
│   ├── app.py              # মূল Flask app + সব API রুট
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html          # লগইন পেজ
│   ├── register.html       # রেজিস্ট্রেশন পেজ
│   ├── dashboard.html      # স্টুডেন্ট ম্যানেজমেন্ট ড্যাশবোর্ড
│   └── js/
│       ├── api.js          # backend এর সাথে fetch কল
│       └── dashboard.js    # dashboard এর সব লজিক (CRUD, search, pagination)
└── README.md
```

## 🚀 চালানোর নিয়ম

### ১. Backend সেটআপ

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows এ: venv\Scripts\activate

pip install -r requirements.txt

# (ঐচ্ছিক) .env ফাইল বানান
cp .env.example .env

python app.py
```

Backend চলবে: **http://localhost:5000**

প্রথমবার রান করলে স্বয়ংক্রিয়ভাবে একটা ডিফল্ট admin একাউন্ট তৈরি হবে:
- **username:** `admin`
- **password:** `admin123`

### ২. Database পরিবর্তন (PostgreSQL / MySQL)

ডিফল্টভাবে SQLite ব্যবহার হয় (কোনো সেটআপ লাগে না)। প্রোডাকশনে PostgreSQL বা MySQL ব্যবহার করতে চাইলে:

**PostgreSQL:**
```bash
pip install psycopg2-binary
# .env এ:
DATABASE_URL=postgresql://username:password@localhost:5432/student_db
```

**MySQL:**
```bash
pip install PyMySQL
# .env এ:
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/student_db
```

### ৩. Frontend চালানো

`frontend/` ফোল্ডারের `index.html` ফাইলটা সরাসরি ব্রাউজারে ওপেন করলেই হবে। অথবা লাইভ সার্ভার ব্যবহার করতে পারেন:

```bash
cd frontend
python -m http.server 5500
```

তারপর ব্রাউজারে যান: **http://localhost:5500**

> ⚠️ `js/api.js` ফাইলে `API_BASE_URL` ভ্যারিয়েবলটা আপনার backend URL এর সাথে ম্যাচ করে কিনা চেক করে নিন।

## 🔑 API Endpoints সামারি

| Method | Endpoint | কাজ | Auth লাগবে? |
|---|---|---|---|
| POST | `/api/register` | নতুন ইউজার রেজিস্ট্রেশন | না |
| POST | `/api/login` | লগইন, JWT টোকেন রিটার্ন করে | না |
| GET | `/api/me` | বর্তমান লগইন করা ইউজারের তথ্য | হ্যাঁ |
| GET | `/api/students` | সব স্টুডেন্ট লিস্ট (search, pagination সহ) | হ্যাঁ |
| GET | `/api/students/<id>` | একজন স্টুডেন্টের তথ্য | হ্যাঁ |
| POST | `/api/students` | নতুন স্টুডেন্ট যোগ করা | হ্যাঁ |
| PUT | `/api/students/<id>` | স্টুডেন্ট তথ্য এডিট করা | হ্যাঁ |
| DELETE | `/api/students/<id>` | স্টুডেন্ট ডিলিট করা | হ্যাঁ |
| GET | `/api/stats` | ড্যাশবোর্ড স্ট্যাটিস্টিক্স | হ্যাঁ |

প্রোটেক্টেড রুটে হেডারে টোকেন পাঠাতে হবে:
```
Authorization: Bearer <your_jwt_token>
```

## ✨ ফিচার

- JWT ভিত্তিক Authentication (Login/Register)
- Student CRUD (Create, Read, Update, Delete)
- নাম/রোল/ডিপার্টমেন্ট দিয়ে লাইভ সার্চ
- Pagination
- ডিপার্টমেন্ট অনুযায়ী স্ট্যাটিস্টিক্স
- Responsive UI (Tailwind CSS)

## 🔧 ভবিষ্যতে যোগ করা যেতে পারে

- Role-based access (Admin vs Teacher পার্মিশন আলাদা করা)
- Student profile picture আপলোড
- Attendance ও Grade মডিউল
- CSV/Excel এ Export করার ফিচার
- Refresh Token ও Password Reset ফ্লো
