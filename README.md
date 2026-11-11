# 🔐 Secure File Sharing API (Flask + JWT)

[![CI](https://github.com/Mudabbirarafat/secure-file-sharing/actions/workflows/ci.yml/badge.svg)](https://github.com/Mudabbirarafat/secure-file-sharing/actions/workflows/ci.yml)
[![XERJ Corpus Hub contributor](https://hub.xerj.org/contributors/Mudabbirarafat/badge.svg)](https://hub.xerj.org/contributors/Mudabbirarafat)

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
├── secure_file_sharing.postman_collection.json # Postman collection, in run order
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
Open Postman → Import → select the JSON file.

Set `baseUrl`, `opsEmail`, `opsPassword`, `clientEmail` and `clientPassword` in
the collection's variables. The values shipped with it are placeholders, not
credentials.

Then run the requests top to bottom. They are in that order for a reason:

- **Ops login** stores its token in `opsToken`, and **Ops upload** sends it as
  `Authorization: Bearer {{opsToken}}`. Upload answers 401 without it. The
  collection keeps a second, deliberately unauthenticated upload request so
  that rule is visible rather than assumed.
- **Client signup** lifts the token out of the `verify_link` it returns, so
  **Client verify email** needs nothing pasted in by hand.
- **Client request a download link** does the same with the signed URL, which
  is what **Client download** then uses.

#Author
Mudabbir Arafat
