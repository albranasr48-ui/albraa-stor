from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymysql
import os

app = Flask(__name__)

# إعدادات اتصال قاعدة بيانات MySQL (قم بتعديل البيانات حسب خادمك أو بيئة الاستضافة)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'store_db')

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM settings WHERE id = 1")
        settings = cursor.fetchone()
        
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
    conn.close()
    return render_template('index.html', settings=settings, categories=categories, products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_settings':
            name = request.form.get('store_name')
            phone = request.form.get('store_phone')
            logo = request.form.get('store_logo')
            with conn.cursor() as cursor:
                cursor.execute("UPDATE settings SET store_name=%s, store_phone=%s, store_logo=%s WHERE id=1", (name, phone, logo))
                conn.commit()
                
        elif action == 'add_product':
            name = request.form.get('name')
            category_id = request.form.get('category_id')
            price = request.form.get('price')
            discount = request.form.get('discount', 0)
            image = request.form.get('image', '')
            description = request.form.get('description', '')
            colors = request.form.get('colors', '')
            sizes = request.form.get('sizes', '')
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO products (name, category_id, price, discount, image, description, colors, sizes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, category_id, price, discount, image, description, colors, sizes))
                conn.commit()
                
        elif action == 'delete_product':
            prod_id = request.form.get('product_id')
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE id = %s", (prod_id,))
                conn.commit()
                
        elif action == 'add_category':
            cat_name = request.form.get('category_name')
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO categories (name) VALUES (%s)", (cat_name,))
                conn.commit()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM settings WHERE id = 1")
        settings = cursor.fetchone()
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        cursor.execute("SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id")
        products = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', settings=settings, categories=categories, products=products)

if __name__ == '__main__':
    app.run(debug=True)