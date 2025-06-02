from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime, timezone
from functools import wraps
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_user_titles_and_badges(cursor, username):
    titles = []
    badges = []

    cursor.execute("""
        SELECT 
            CASE WHEN title_volunteer THEN '志愿者' END as t1,
            CASE WHEN title_senior_volunteer THEN '高级志愿者' END as t2,
            CASE WHEN title_support_staff THEN '志愿管理人员' END as t3,
            CASE WHEN title_tech_advisor THEN '技术顾问' END as t4,
            CASE WHEN title_admin THEN '管理人员' END as t5,
            CASE WHEN title_site_owner THEN '网站负责人' END as t6
        FROM users WHERE username = %s
    """, (username,))
    result = cursor.fetchone()
    titles = [t for t in result.values() if t]

    cursor.execute("""
        SELECT 
            CASE WHEN badge_answer_expert THEN '回答小能手' END as b1,
            CASE WHEN badge_site_engineer THEN '网站工程师' END as b2,
            CASE WHEN badge_log_analyst THEN '日志分析师' END as b3
        FROM users WHERE username = %s
    """, (username,))
    result = cursor.fetchone()
    badges = [b for b in result.values() if b]
    
    return titles, badges
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'wanghong_community1',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def get_db():
    return pymysql.connect(**db_config)

@app.route('/')
def index():
    username = session.get('username', None)
    return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='请填写用户名和密码')
        
        conn = get_db()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
                
            if user:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='用户名或密码错误')
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('register.html', error='用户名和密码不能为空')
        
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return render_template('register.html', error='用户名已存在')

            sql = "INSERT INTO users (username, password, created_at) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password, datetime.now()))
            conn.commit()
            
            session['username'] = username
            return redirect(url_for('index'))
        conn.close()
    
    return render_template('register.html')

@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()
            user_id = user['id']

            sql = "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (title, content, user_id))
            conn.commit()
        conn.close()
        return redirect(url_for('forum'))
        
    return render_template('post.html')

@app.route('/forum')
def forum():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    current_page = request.args.get('page', 1, type=int)
    posts_per_page = 5
    
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM posts")
        total_posts = cursor.fetchone()['total']
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

        offset = (current_page - 1) * posts_per_page
        sql = """
            SELECT 
                p.*,
                u.username,
                COUNT(r.id) as reply_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN replies r ON p.id = r.post_id
            GROUP BY p.id, u.username
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (posts_per_page, offset))
        posts = cursor.fetchall()
    conn.close()
    
    return render_template('forum.html', 
                         username=username, 
                         current_page=current_page, 
                         total_pages=total_pages,
                         posts=posts)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/thread/<int:post_id>/reply', methods=['POST'])
def reply_post(post_id):
    if 'username' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    data = request.get_json()
    content = data.get('content')
    reply_to = data.get('reply_to')
    
    if not content:
        return jsonify({'error': '回复内容不能为空'}), 400
    
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE username = %s', (session['username'],))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': '用户不存在'}), 404

            cursor.execute('SELECT id FROM posts WHERE id = %s', (post_id,))
            if not cursor.fetchone():
                return jsonify({'error': '帖子不存在'}), 404

            cursor.execute(
                'INSERT INTO replies (content, user_id, post_id, reply_to, created_at) VALUES (%s, %s, %s, %s, NOW())',
                (content, user['id'], post_id, reply_to)
            )
            conn.commit()

            reply_id = cursor.lastrowid
            cursor.execute("""
                SELECT r.*, u.username 
                FROM replies r 
                JOIN users u ON r.user_id = u.id 
                WHERE r.id = %s
            """, (reply_id,))
            reply = cursor.fetchone()

            titles, badges = get_user_titles_and_badges(cursor, session['username'])

        return jsonify({
            'id': reply['id'],
            'username': reply['username'],
            'content': reply['content'],
            'created_at': reply['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'titles': ','.join(titles) if titles else '',
            'badges': ','.join(badges) if badges else ''
        })
    finally:
        conn.close()

def is_post_author(cursor, username, post_id):
    cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
    post = cursor.fetchone()
    if not post:
        return False
        
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    return user and user['id'] == post['user_id']

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()

        if not is_post_author(cursor, session['username'], post_id):
            titles, _ = get_user_titles_and_badges(cursor, session['username'])
            if not any(title in ['志愿管理人员', '技术顾问', '管理人员', '网站负责人'] for title in titles):
                return "没有权限编辑此帖子", 403

        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            if not title or not content:
                return render_template('edit_post.html', post=post, error='标题和内容不能为空')
            
            cursor.execute(
                "UPDATE posts SET title = %s, content = %s WHERE id = %s",
                (title, content, post_id)
            )
            conn.commit()
            return redirect(url_for('thread', thread_id=post_id))
    
    return render_template('edit_post.html', post=post, username=session.get('username'))

@app.route('/thread/<thread_id>')
def thread(thread_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = %s", [thread_id])
    post = cur.fetchone()

    if post is None:
        cur.close()
        conn.close()
        return "Post not found", 404

    cur.execute("""
        SELECT r.*, u.username
        FROM replies r
        JOIN users u ON r.user_id = u.id
        WHERE r.post_id = %s
        ORDER BY r.created_at DESC
    """, [thread_id])
    replies = cur.fetchall()

    is_author = False
    has_edit_permission = False
    if 'username' in session:
        is_author = is_post_author(cur, session['username'], thread_id)
        titles, _ = get_user_titles_and_badges(cur, session['username'])
        has_edit_permission = any(title in ['志愿管理人员', '技术顾问', '管理人员', '网站负责人'] for title in titles)
    
    cur.close()
    conn.close()

    return render_template('thread.html', 
                         post=post, 
                         replies=replies, 
                         username=session.get('username'),
                         is_post_author=is_author,
                         has_edit_permission=has_edit_permission)

@app.route('/profile/<username>')
def profile(username):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT username, created_at FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        titles, badges = get_user_titles_and_badges(cursor, username)
        
        sql = """
            SELECT p.*, COUNT(r.id) as reply_count 
            FROM posts p 
            LEFT JOIN replies r ON p.id = r.post_id 
            JOIN users u ON p.user_id = u.id 
            WHERE u.username = %s 
            GROUP BY p.id 
            ORDER BY p.created_at DESC
        """
        cursor.execute(sql, (username,))
        posts = cursor.fetchall()

        sql = """
            SELECT r.*, p.title as post_title, p.id as post_id
            FROM replies r
            JOIN posts p ON r.post_id = p.id
            JOIN users u ON r.user_id = u.id
            WHERE u.username = %s
            ORDER BY r.created_at DESC
        """
        cursor.execute(sql, (username,))
        replies = cursor.fetchall()

        for post in posts:
            post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
        for reply in replies:
            reply['created_at'] = reply['created_at'].strftime('%Y-%m-%d %H:%M')
        
        conn.close()
        return render_template('profile.html',
                           profile_user=username,
                           join_date=user['created_at'].strftime('%Y-%m-%d'),
                           titles=titles,
                           badges=badges,
                           posts=posts,
                           replies=replies,
                           username=session.get('username'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)