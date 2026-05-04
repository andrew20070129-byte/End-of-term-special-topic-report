from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
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

@app.route('/facilities')
def facility_list():
    conn = database.get_db_connection()
    facilities = conn.execute('SELECT * FROM facilities').fetchall()
    conn.close()
    return render_template('facilities/facility_list.html', facilities=facilities)

@app.route('/facility/<int:id>')
def facility_detail(id):
    conn = database.get_db_connection()
    facility = conn.execute('SELECT * FROM facilities WHERE id = ?', (id,)).fetchone()
    
    if not facility:
        flash('找不到該設施', 'error')
        conn.close()
        return redirect(url_for('facility_list'))
        
    reviews = conn.execute('''
        SELECT r.*, u.username 
        FROM facility_reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.facility_id = ?
        ORDER BY r.created_at DESC
    ''', (id,)).fetchall()
    
    conn.close()
    return render_template('facilities/facility_detail.html', facility=facility, reviews=reviews)

@app.route('/facility/<int:id>/review', methods=['POST'])
@login_required
def add_facility_review(id):
    rating = request.form.get('rating', type=int)
    content = request.form.get('content')
    
    if not rating or rating < 1 or rating > 5:
        flash('請給予有效的星等評分 (1-5)', 'error')
        return redirect(url_for('facility_detail', id=id))
        
    conn = database.get_db_connection()
    conn.execute('INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)',
                 (id, session['user_id'], rating, content))
    conn.commit()
    conn.close()
    
    flash('評價發布成功！', 'success')
    return redirect(url_for('facility_detail', id=id))

@app.route('/review/<int:id>/delete', methods=['POST'])
@login_required
def delete_review(id):
    conn = database.get_db_connection()
    review = conn.execute('SELECT * FROM facility_reviews WHERE id = ?', (id,)).fetchone()
    
    if not review:
        flash('評價不存在', 'error')
        conn.close()
        return redirect(url_for('facility_list'))
        
    if review['user_id'] != session['user_id']:
        flash('您無權刪除他人的評價', 'error')
        conn.close()
        return redirect(url_for('facility_detail', id=review['facility_id']))
        
    conn.execute('DELETE FROM facility_reviews WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('評價已成功刪除', 'success')
    return redirect(url_for('facility_detail', id=review['facility_id']))

@app.route('/review/<int:id>/vote', methods=['POST'])
@login_required
def vote_review(id):
    data = request.get_json()
    vote_type = data.get('vote_type')
    if vote_type not in ['like', 'dislike']:
        return jsonify({'status': 'error', 'message': '無效的投票類型'}), 400
        
    conn = database.get_db_connection()
    review = conn.execute('SELECT facility_id, likes, dislikes FROM facility_reviews WHERE id = ?', (id,)).fetchone()
    
    if not review:
        conn.close()
        return jsonify({'status': 'error', 'message': '評價不存在'}), 404
        
    user_id = session['user_id']
    existing_vote = conn.execute('SELECT vote_type FROM review_votes WHERE review_id = ? AND user_id = ?', (id, user_id)).fetchone()
    
    if existing_vote:
        conn.close()
        return jsonify({'status': 'error', 'message': '您已經對這則評價投過票了！'}), 400
        
    # Record the vote
    conn.execute('INSERT INTO review_votes (review_id, user_id, vote_type) VALUES (?, ?, ?)', (id, user_id, vote_type))
    
    # Update count
    if vote_type == 'like':
        new_likes = review['likes'] + 1
        conn.execute('UPDATE facility_reviews SET likes = ? WHERE id = ?', (new_likes, id))
        result = {'status': 'success', 'likes': new_likes, 'dislikes': review['dislikes']}
    else:
        new_dislikes = review['dislikes'] + 1
        conn.execute('UPDATE facility_reviews SET dislikes = ? WHERE id = ?', (new_dislikes, id))
        result = {'status': 'success', 'likes': review['likes'], 'dislikes': new_dislikes}
        
    conn.commit()
    conn.close()
    
    return jsonify(result)

@app.route('/forum')
def forum():
    conn = database.get_db_connection()
    boards = conn.execute('SELECT * FROM boards').fetchall()
    
    # 抓取最新 5 篇文章
    recent_posts = conn.execute('''
        SELECT p.*, b.name as board_name, u.username
        FROM posts p
        JOIN boards b ON p.board_id = b.id
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 5
    ''').fetchall()
    conn.close()
    
    return render_template('forum/forum.html', boards=boards, recent_posts=recent_posts)

@app.route('/board/<int:id>')
def board_detail(id):
    conn = database.get_db_connection()
    board = conn.execute('SELECT * FROM boards WHERE id = ?', (id,)).fetchone()
    if not board:
        flash('找不到該看板', 'error')
        conn.close()
        return redirect(url_for('forum'))
        
    posts = conn.execute('''
        SELECT p.*, u.username, 
               (SELECT COUNT(*) FROM post_comments WHERE post_id = p.id) as comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.board_id = ?
        ORDER BY p.created_at DESC
    ''', (id,)).fetchall()
    
    conn.close()
    return render_template('forum/board.html', board=board, posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    conn = database.get_db_connection()
    if request.method == 'POST':
        board_id = request.form.get('board_id', type=int)
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags')
        
        if not board_id or not title or not content:
            flash('請填寫完整文章資訊', 'error')
            boards = conn.execute('SELECT * FROM boards').fetchall()
            conn.close()
            return render_template('forum/new_post.html', boards=boards)
            
        cursor = conn.execute('INSERT INTO posts (board_id, user_id, title, content, tags) VALUES (?, ?, ?, ?, ?)',
                              (board_id, session['user_id'], title, content, tags))
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('文章發布成功！', 'success')
        return redirect(url_for('post_detail', id=post_id))
        
    boards = conn.execute('SELECT * FROM boards').fetchall()
    conn.close()
    return render_template('forum/new_post.html', boards=boards)

@app.route('/post/<int:id>')
def post_detail(id):
    conn = database.get_db_connection()
    post = conn.execute('''
        SELECT p.*, b.name as board_name, u.username
        FROM posts p
        JOIN boards b ON p.board_id = b.id
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    ''', (id,)).fetchone()
    
    if not post:
        flash('找不到該文章', 'error')
        conn.close()
        return redirect(url_for('forum'))
        
    comments = conn.execute('''
        SELECT c.*, u.username 
        FROM post_comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
    ''', (id,)).fetchall()
    
    conn.close()
    return render_template('forum/post.html', post=post, comments=comments)

@app.route('/post/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    content = request.form.get('content')
    if not content:
        flash('留言內容不可為空', 'error')
        return redirect(url_for('post_detail', id=id))
        
    conn = database.get_db_connection()
    conn.execute('INSERT INTO post_comments (post_id, user_id, content) VALUES (?, ?, ?)',
                 (id, session['user_id'], content))
    conn.commit()
    conn.close()
    
    flash('留言發布成功', 'success')
    return redirect(url_for('post_detail', id=id))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('forum'))
        
    search_term = f'%{query}%'
    conn = database.get_db_connection()
    posts = conn.execute('''
        SELECT p.*, b.name as board_name, u.username
        FROM posts p
        JOIN boards b ON p.board_id = b.id
        JOIN users u ON p.user_id = u.id
        WHERE p.title LIKE ? OR p.content LIKE ?
        ORDER BY p.created_at DESC
    ''', (search_term, search_term)).fetchall()
    conn.close()
    
    return render_template('forum/search_results.html', query=query, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
