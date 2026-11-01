# 🔐 Secure File Sharing API (Flask + JWT)

[![CI](https://github.com/Mudabbirarafat/secure-file-sharing/actions/workflows/ci.yml/badge.svg)](https://github.com/Mudabbirarafat/secure-file-sharing/actions/workflows/ci.yml)

This is a secure file sharing system built with Flask where:
- `Ops` users can upload `.docx`, `.pptx`, or `.xlsx` files.
- `Client` users can sign up, verify their email, log in, view available files, and download via a secure link.

---

## 📂 Folder Structure

secure-file-sharing/
├── app.py
├── client.py
├── ops.py
├── models.py
├── uploaded_files/ # Stores uploaded files
├── requirements.txt
├── secure_file_sharing.postman_collection.json # ✅ Postman dump
└── README.md

---

## ⚙️ Tech Stack

- Flask + Blueprints
- Flask SQLAlchemy
- JWT for authentication
- SQLite or any SQL DB
- Postman/Thunder Client for testing

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
python app.py
🔐 API Endpoints
➤ Ops APIs
Method	Route	Description
POST	/ops/login	Login as Ops user, returns a bearer token
POST	/ops/upload	Upload valid file (.docx/.pptx/.xlsx) - requires the token

### Ops authentication

`/ops/upload` requires a bearer token issued by `/ops/login`:

Step 1 — exchange credentials for a token:

```bash
curl -s -X POST localhost:5000/ops/login -H 'Content-Type: application/json' -d '{"email":"ops@example.com","password":"your-password"}'
```

```json
{ "message": "Ops login successful", "token": "eyJhbGciOiJIUzI1NiIs..." }
```

Step 2 — send the token with the upload:

```bash
curl -X POST localhost:5000/ops/upload -H "Authorization: Bearer <token>" -F file=@report.docx
```

Tokens last 60 minutes. The account's role is rechecked against the database on
every request, so a token stops working as soon as the account is removed or
is no longer an ops user.


➤ Client APIs
Method	Route	Description
POST	/client/signup	Client sign-up
GET	/client/verify/<token>	Email verification
POST	/client/login	Login as verified client
GET	/client/files?email=<email>	List all uploaded files
GET	/client/download-file/<filename>?email=<email>	Generate download link
GET	/client/download/<token>	Secure file download

---
## ⚙️ Tech Stack
- **Backend:** Flask (Blueprints)
- **Database:** SQLite (extensible to any SQL DB)
- **Authentication:** JWT
- **Testing Tools:** Postman / Thunder Client
- **Language:** Python

---
🔐 API Endpoints
Ops APIs
Method	Route	Description
POST	/ops/login	Login as Ops user, returns a bearer token
POST	/ops/upload	Upload valid file (.docx/.pptx/.xlsx) - requires the token

## 🚀 How to Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
The server will start at http://localhost:5000.

🧪 Postman Testing
This project includes a full Postman collection to test APIs.

✅ File:
secure_file_sharing.postman_collection.json

📥 How to use:
Open Postman → Import

Select the JSON file

All API routes will be pre-configured

Test login, upload, signup, file listing, secure download

#Author
Mudabbir Arafat
