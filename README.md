# 🔐 Secure File Sharing API (Flask + JWT)

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

yaml
Copy
Edit

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
POST	/ops/login	Login as Ops user
POST	/ops/upload	Upload valid file (.docx/.pptx/.xlsx)

➤ Client APIs
Method	Route	Description
POST	/client/signup	Client sign-up
GET	/client/verify/<token>	Email verification
POST	/client/login	Login as verified client
GET	/client/files?email=<email>	List all uploaded files
GET	/client/download-file/<filename>?email=<email>	Generate download link
GET	/client/download/<token>	Secure file download

🧪 Postman Testing
This project includes a full Postman collection to test APIs.

✅ File:
secure_file_sharing.postman_collection.json

📥 How to use:
Open Postman → Import

Select the JSON file

All API routes will be pre-configured

Test login, upload, signup, file listing, secure download