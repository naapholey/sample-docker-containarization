from flask import Flask, render_template_string, jsonify
from datetime import datetime
import socket
import os
import sys
import json
import redis
import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============ DATABASE CONFIGURATION ============
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'docker_class'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# ============ REDIS CACHE CONFIGURATION ============
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': 0,
    'decode_responses': True
}

# ============ HTML TEMPLATE ============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docker Class Demo - Multi-Container App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 50px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 800px;
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .docker-icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 20px;
            line-height: 1.3;
        }
        
        .welcome-text {
            color: #667eea;
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .message {
            color: #555;
            font-size: 1.3em;
            margin-bottom: 30px;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
            margin-bottom: 30px;
        }
        
        .service-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .service-card h3 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .service-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }
        
        .service-status {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
            border-radius: 8px;
        }
        
        .info-box h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: bold;
            color: #555;
        }
        
        .info-value {
            color: #667eea;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .status-ok {
            background: #10b981;
            color: white;
        }
        
        .status-error {
            background: #ef4444;
            color: white;
        }
        
        .status-warning {
            background: #f59e0b;
            color: white;
        }
        
        .footer {
            margin-top: 30px;
            color: #999;
            font-size: 0.9em;
            border-top: 1px solid #e0e0e0;
            padding-top: 20px;
        }
        
        .request-counter {
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .request-counter h3 {
            margin-bottom: 10px;
        }
        
        .counter-value {
            font-size: 2em;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="docker-icon">🐳</div>
        <h1>Docker Multi-Container Application</h1>
        <p class="welcome-text">Welcome to Docker Class with 10Alytics</p>
        <p class="message">Multi-container architecture demo</p>
        
        <!-- Services Grid -->
        <div class="services-grid">
            <div class="service-card">
                <div class="service-icon">🌐</div>
                <h3>Web Service</h3>
                <p class="service-status">Flask Application</p>
            </div>
            <div class="service-card">
                <div class="service-icon">🗄️</div>
                <h3>Database</h3>
                <p class="service-status">MySQL/MariaDB</p>
            </div>
            <div class="service-card">
                <div class="service-icon">⚡</div>
                <h3>Cache</h3>
                <p class="service-status">Redis</p>
            </div>
        </div>
        
        <!-- Container Information -->
        <div class="info-box">
            <h3>📊 Application Service Information</h3>
            <div class="info-item">
                <span class="info-label">Hostname (Container ID):</span>
                <span class="info-value">{{ hostname }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Container IP:</span>
                <span class="info-value">{{ container_ip }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Python Version:</span>
                <span class="info-value">{{ python_version }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Current Time:</span>
                <span class="info-value">{{ current_time }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Environment:</span>
                <span class="info-value">{{ environment }}</span>
            </div>
        </div>
        
        <!-- Database Connection Status -->
        <div class="info-box">
            <h3>🗄️ Database Service Status</h3>
            <div class="info-item">
                <span class="info-label">Database Host:</span>
                <span class="info-value">{{ db_host }} <span class="status-badge {{ db_status_class }}">{{ db_status }}</span></span>
            </div>
            <div class="info-item">
                <span class="info-label">Database Name:</span>
                <span class="info-value">{{ db_name }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Total Visits (from DB):</span>
                <span class="info-value">{{ total_visits }}</span>
            </div>
        </div>
        
        <!-- Redis Cache Status -->
        <div class="info-box">
            <h3>⚡ Cache Service Status</h3>
            <div class="info-item">
                <span class="info-label">Redis Host:</span>
                <span class="info-value">{{ redis_host }} <span class="status-badge {{ redis_status_class }}">{{ redis_status }}</span></span>
            </div>
            <div class="info-item">
                <span class="info-label">Cached Requests:</span>
                <span class="info-value">{{ cached_requests }}</span>
            </div>
        </div>
        
        <!-- Request Counter -->
        <div class="request-counter">
            <h3>📈 Page Views (from Cache)</h3>
            <div class="counter-value">{{ page_views }}</div>
        </div>
        
        <div class="footer">
            <p>This application is running in a 3-container Docker environment 🚀</p>
            <p><strong>Container ID:</strong> {{ container_id }} | <strong>Loaded at:</strong> {{ loaded_time }}</p>
        </div>
    </div>
</body>
</html>
"""

# ============ DATABASE FUNCTIONS ============

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables on startup"""
    for attempt in range(5):
        conn = get_db_connection()
        if not conn:
            logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
            import time
            time.sleep(5)
            continue
        
        cursor = conn.cursor()
        try:
            # Create visits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    container_id VARCHAR(255),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_agent VARCHAR(500),
                    ip_address VARCHAR(45)
                )
            ''')
            
            # Create visits_counter table for total count
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visits_counter (
                    id INT PRIMARY KEY DEFAULT 1,
                    total_count INT DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize counter if doesn't exist
            cursor.execute('SELECT COUNT(*) FROM visits_counter')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO visits_counter (id, total_count) VALUES (1, 0)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            return True
        except Error as e:
            logger.error(f"Database initialization error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    logger.error("Failed to initialize database after 5 attempts")
    return False

def record_visit(container_id, user_agent="", ip_address=""):
    """Record a visit in the database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Insert visit record
        query = '''
            INSERT INTO visits (container_id, user_agent, ip_address)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(query, (container_id, user_agent, ip_address))
        
        # Update counter
        cursor.execute('UPDATE visits_counter SET total_count = total_count + 1 WHERE id = 1')
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        logger.error(f"Error recording visit: {e}")
        return False

def get_total_visits():
    """Get total visits from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return 0
        
        cursor = conn.cursor()
        cursor.execute('SELECT total_count FROM visits_counter WHERE id = 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result[0] if result else 0
    except Error as e:
        logger.error(f"Error getting total visits: {e}")
        return 0

# ============ REDIS CACHE FUNCTIONS ============

def get_redis_connection():
    """Get Redis connection"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        return r
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        return None

def increment_page_views():
    """Increment page view counter in Redis"""
    try:
        r = get_redis_connection()
        if r:
            views = r.incr('page_views')
            return views
    except Exception as e:
        logger.error(f"Error incrementing page views: {e}")
    return 0

def get_page_views():
    """Get page view count from Redis"""
    try:
        r = get_redis_connection()
        if r:
            views = r.get('page_views')
            return int(views) if views else 0
    except Exception as e:
        logger.error(f"Error getting page views: {e}")
    return 0

def get_cached_requests_count():
    """Get number of cached requests"""
    try:
        r = get_redis_connection()
        if r:
            # Get all keys that start with 'request:'
            keys = r.keys('request:*')
            return len(keys)
    except Exception as e:
        logger.error(f"Error getting cached requests: {e}")
    return 0

# ============ ROUTES ============

@app.route('/')
def home():
    """
    Main route that displays welcome message with container and service information
    """
    # Container information
    hostname = socket.gethostname()
    try:
        container_ip = socket.gethostbyname(socket.gethostname())
    except:
        container_ip = "Unable to determine"
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    environment = os.getenv('APP_ENV', 'development')
    container_id = hostname[:12]
    loaded_time = datetime.now().strftime("%H:%M:%S")
    
    # Database status and info
    conn = get_db_connection()
    db_status = "Connected ✓" if conn else "Disconnected ✗"
    db_status_class = "status-ok" if conn else "status-error"
    if conn:
        conn.close()
    
    total_visits = get_total_visits()
    db_host = DB_CONFIG['host']
    db_name = DB_CONFIG['database']
    
    # Redis cache status
    redis_conn = get_redis_connection()
    redis_status = "Connected ✓" if redis_conn else "Disconnected ✗"
    redis_status_class = "status-ok" if redis_conn else "status-error"
    redis_host = REDIS_CONFIG['host']
    
    # Page views and cached requests
    page_views = increment_page_views()
    cached_requests = get_cached_requests_count()
    
    # Record this visit in database
    record_visit(container_id)
    
    return render_template_string(
        HTML_TEMPLATE,
        hostname=hostname,
        container_ip=container_ip,
        python_version=python_version,
        current_time=current_time,
        environment=environment,
        container_id=container_id,
        loaded_time=loaded_time,
        db_status=db_status,
        db_status_class=db_status_class,
        db_host=db_host,
        db_name=db_name,
        total_visits=total_visits,
        redis_status=redis_status,
        redis_status_class=redis_status_class,
        redis_host=redis_host,
        page_views=page_views,
        cached_requests=cached_requests
    )

@app.route('/health')
def health():
    """
    Health check endpoint for container monitoring
    Checks all three services
    """
    db_ok = get_db_connection() is not None
    redis_ok = get_redis_connection() is not None
    
    status = "healthy" if (db_ok and redis_ok) else "degraded"
    
    return jsonify({
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "service": "flask-docker-demo",
        "version": "2.0.0",
        "services": {
            "database": "ok" if db_ok else "failed",
            "redis": "ok" if redis_ok else "failed"
        }
    })

@app.route('/info')
def info():
    """
    Information endpoint that returns container and service details in JSON format
    """
    hostname = socket.gethostname()
    
    db_conn = get_db_connection()
    db_status = "connected" if db_conn else "disconnected"
    if db_conn:
        db_conn.close()
    
    redis_conn = get_redis_connection()
    redis_status = "connected" if redis_conn else "disconnected"
    
    return jsonify({
        "message": "Multi-container Docker application demo",
        "application": {
            "name": "Docker Class Demo",
            "version": "2.0.0",
            "environment": os.getenv('APP_ENV', 'development')
        },
        "container_info": {
            "hostname": hostname,
            "container_id": hostname[:12],
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "timestamp": datetime.now().isoformat()
        },
        "services": {
            "database": {
                "host": DB_CONFIG['host'],
                "name": DB_CONFIG['database'],
                "status": db_status,
                "total_visits": get_total_visits()
            },
            "cache": {
                "host": REDIS_CONFIG['host'],
                "port": REDIS_CONFIG['port'],
                "status": redis_status,
                "page_views": get_page_views()
            }
        }
    })

@app.route('/api/visits')
def get_visits():
    """Get visit statistics from database"""
    try:
        total = get_total_visits()
        page_views = get_page_views()
        
        return jsonify({
            "total_visits_in_db": total,
            "page_views_from_cache": page_views,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/redis-test')
def redis_test():
    """Test Redis connectivity and basic operations"""
    try:
        r = get_redis_connection()
        if not r:
            return jsonify({"status": "error", "message": "Redis connection failed"}), 500
        
        # Test set/get
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        
        return jsonify({
            "status": "ok",
            "message": "Redis is working",
            "test_key_value": value,
            "all_keys_count": len(r.keys('*'))
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/db-test')
def db_test():
    """Test database connectivity"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM visits')
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "ok",
            "message": "Database is working",
            "total_visits_recorded": count
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Get configuration
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
