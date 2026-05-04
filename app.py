from flask import Flask, render_template, request, session, redirect, url_for, flash
import database
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# 設定 Secret Key 供 Session 與 Flash 訊息使用 (開發階段可寫死，上線建議使用環境變數)
app.secret_key = 'super_secret_campus_key'

# 初始化資料庫 (若 database.db 不存在則依據 schema.sql 建立)
database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
