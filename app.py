from flask import Flask, render_template, request, session, redirect, url_for, flash
import database
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
# 設定 Secret Key 供 Session 與 Flash 訊息使用 (開發階段可寫死，上線建議使用環境變數)
app.secret_key = 'super_secret_campus_key'

# 初始化資料庫 (若 database.db 不存在則依據 schema.sql 建立)
database.init_db()

# 登入驗證裝飾器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入後再進行操作！', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('帳號與密碼欄位不能為空！', 'error')
            return redirect(url_for('register'))
            
        conn = database.get_db_connection()
        user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        
        if user:
            flash('此帳號已經被註冊了，請嘗試其他名稱！', 'error')
            conn.close()
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        
        flash('註冊成功！請登入您的帳號。', 'success')
        return redirect(url_for('login'))
        
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = database.get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('登入成功！歡迎回來，' + user['username'], 'success')
            return redirect(url_for('index'))
        else:
            flash('登入失敗，請檢查您的帳號或密碼。', 'error')
            
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出。', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
