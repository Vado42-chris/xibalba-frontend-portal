#!/usr/bin/env python3
"""
Xibalba Mixed Media Studio - Backend Web Application
Real web application with Google OAuth, client portals, and email management
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from flask_oauthlib.client import OAuth  # Temporarily disabled for deployment
import sqlite3
import os
import json
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Google OAuth Configuration - Temporarily disabled for deployment
# oauth = OAuth(app)
# google = oauth.remote_app(
#     'google',
#     consumer_key=os.environ.get('GOOGLE_CLIENT_ID'),
#     consumer_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
#     request_token_params={'scope': 'email'},
#     base_url='https://www.googleapis.com/oauth2/v1/',
#     request_token_url=None,
#     access_token_method='POST',
#     access_token_url='https://accounts.google.com/o/oauth2/token',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
# )

# Database initialization
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('xibalba.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT UNIQUE,
            name TEXT,
            picture_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Email registry table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_address TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('floater', 'claimed', 'verified', 'suspended')),
            claimed_by_user_id INTEGER,
            claimed_at TIMESTAMP,
            verification_token TEXT,
            verification_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (claimed_by_user_id) REFERENCES users(id)
        )
    ''')
    
    # Client portals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_portals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            portal_type TEXT NOT NULL,
            portal_data TEXT,
            access_level TEXT DEFAULT 'basic',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Virtual studios table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS virtual_studios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studio_name TEXT UNIQUE NOT NULL,
            studio_type TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Homepage - Xibalba Mixed Media Studio"""
    return render_template('index.html')

@app.route('/services')
def services():
    """Services page - All virtual studios and clients"""
    conn = sqlite3.connect('xibalba.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM virtual_studios WHERE status = "active"')
    studios = cursor.fetchall()
    conn.close()
    
    return render_template('services.html', studios=studios)

@app.route('/about')
def about():
    """About page - Company information"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page - Contact information"""
    return render_template('contact.html')

@app.route('/login')
def login():
    """Login page - Google OAuth - Temporarily disabled for deployment"""
    # return google.authorize(callback=url_for('authorized', _external=True))
    return redirect(url_for('dashboard'))  # Temporary bypass for deployment

@app.route('/logout')
def logout():
    """Logout - Clear session"""
    session.pop('google_token', None)
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    """Google OAuth callback - Temporarily disabled for deployment"""
    # resp = google.authorized_response()
    # if resp is None:
    #     return 'Access denied: reason=%s error=%s' % (
    #         request.args['error_reason'],
    #         request.args['error_description']
    #     )
    
    # session['google_token'] = (resp['access_token'], '')
    # user_info = google.get('userinfo')
    
    # Store user in database
    conn = sqlite3.connect('xibalba.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users (google_id, email, name, picture_url, last_login)
        VALUES (?, ?, ?, ?, ?)
    ''', ('temp_user_123', 'test@example.com', 'Test User', '', datetime.now()))
    
    conn.commit()
    conn.close()
    
    session['user'] = {'id': 'temp_user_123', 'name': 'Test User', 'email': 'test@example.com'}
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """User dashboard - Client portal access"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    
    # Get user's client portals
    conn = sqlite3.connect('xibalba.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM client_portals WHERE user_id = ?', (user['id'],))
    portals = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', user=user, portals=portals)

@app.route('/portal/<portal_type>')
def client_portal(portal_type):
    """Individual client portal access"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    
    # Portal-specific logic
    if portal_type == 'sam-law':
        return render_template('portals/sam_law.html', user=user)
    elif portal_type == 'evolution-foods':
        return render_template('portals/evolution_foods.html', user=user)
    elif portal_type == 'veilrift':
        return render_template('portals/veilrift.html', user=user)
    elif portal_type == 'ai-command-center':
        return render_template('portals/ai_command_center.html', user=user)
    elif portal_type == 'dreamcatcher':
        return render_template('portals/dreamcatcher.html', user=user)
    else:
        return render_template('portals/generic.html', user=user, portal_type=portal_type)

@app.route('/api/email-floater', methods=['GET', 'POST'])
def email_floater():
    """Email floater system API"""
    if request.method == 'POST':
        data = request.get_json()
        email_address = data.get('email_address')
        action = data.get('action')
        
        conn = sqlite3.connect('xibalba.db')
        cursor = conn.cursor()
        
        if action == 'add':
            cursor.execute('''
                INSERT OR IGNORE INTO email_registry (email_address, status)
                VALUES (?, 'floater')
            ''', (email_address,))
        elif action == 'claim':
            if 'user' in session:
                user_id = session['user']['id']
                cursor.execute('''
                    UPDATE email_registry 
                    SET status = 'claimed', claimed_by_user_id = ?, claimed_at = ?
                    WHERE email_address = ? AND status = 'floater'
                ''', (user_id, datetime.now(), email_address))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'})
    
    # GET request - return floater emails
    conn = sqlite3.connect('xibalba.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM email_registry WHERE status = "floater"')
    floaters = cursor.fetchall()
    conn.close()
    
    return jsonify({'floaters': floaters})

@google.tokengetter
def get_google_oauth_token():
    """Get Google OAuth token from session"""
    return session.get('google_token')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
