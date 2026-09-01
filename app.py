import os, sqlite3, smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')
DB='medisaarthi.db'
UPLOAD_DIR='uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)
DELIVERY_CHARGE=30
CONTACT='7859090242'
STATUSES=['Order Placed','Prescription Verified','Packed','Out for Delivery','Delivered']

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    c=db()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL,
      email TEXT, address TEXT NOT NULL, items TEXT NOT NULL, subtotal REAL NOT NULL,
      delivery REAL NOT NULL, total REAL NOT NULL, prescription TEXT, status TEXT NOT NULL,
      created_at TEXT NOT NULL)''')
    c.commit(); c.close()

def send_email(to_email, subject, body):
    host=os.environ.get('SMTP_HOST'); port=os.environ.get('SMTP_PORT','587')
    user=os.environ.get('SMTP_USER'); password=os.environ.get('SMTP_PASSWORD'); sender=os.environ.get('SMTP_FROM',user)
    if not (host and user and password and to_email): return False
    try:
        msg=EmailMessage(); msg['Subject']=subject; msg['From']=sender; msg['To']=to_email; msg.set_content(body)
        with smtplib.SMTP(host,int(port)) as s:
            s.starttls(); s.login(user,password); s.send_message(msg)
        return True
    except Exception as e:
        print('Email error:',e); return False

@app.context_processor
def inject(): return {'delivery_charge':DELIVERY_CHARGE,'contact':CONTACT}

@app.route('/')
def home(): return render_template('index.html')

@app.post('/api/order')
def create_order():
    data=request.form
    name=data.get('name','').strip(); phone=data.get('phone','').strip(); email=data.get('email','').strip(); address=data.get('address','').strip(); items=data.get('items','').strip()
    try: subtotal=float(data.get('subtotal','0'))
    except: subtotal=0
    if not name or not phone or not address or not items or subtotal<=0: return jsonify({'ok':False,'error':'Please fill all required order details.'}),400
    prescription=None
    f=request.files.get('prescription')
    if f and f.filename:
        fn=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(f.filename)}"; f.save(os.path.join(UPLOAD_DIR,fn)); prescription=fn
    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c=db(); cur=c.execute('INSERT INTO orders(name,phone,email,address,items,subtotal,delivery,total,prescription,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(name,phone,email,address,items,subtotal,DELIVERY_CHARGE,subtotal+DELIVERY_CHARGE,prescription,STATUSES[0],now)); oid=cur.lastrowid; c.commit(); c.close()
    if email:
        send_email(email, f'MediSaarthi Order #{oid} received', f'Hello {name},\n\nYour MediSaarthi order #{oid} has been placed.\nTotal: ₹{subtotal+DELIVERY_CHARGE:.2f}\nDelivery charge: ₹{DELIVERY_CHARGE}\nStatus: {STATUSES[0]}\n\nTrack: {request.host_url}track/{oid}\n\nMediSaarthi\nContact: {CONTACT}')
    return jsonify({'ok':True,'order_id':oid,'tracking_url':url_for('track',order_id=oid)})

@app.route('/track/<int:order_id>')
def track(order_id):
    c=db(); order=c.execute('SELECT * FROM orders WHERE id=?',(order_id,)).fetchone(); c.close()
    if not order: return render_template('notfound.html'),404
    return render_template('track.html',order=order,statuses=STATUSES)

@app.get('/api/track/<int:order_id>')
def track_api(order_id):
    c=db(); o=c.execute('SELECT id,name,total,status,created_at FROM orders WHERE id=?',(order_id,)).fetchone(); c.close()
    return jsonify(dict(o) if o else {'error':'Order not found'}), (200 if o else 404)

@app.post('/api/admin/status/<int:order_id>')
def update_status(order_id):
    # Protect this endpoint in production with real admin authentication.
    status=request.form.get('status')
    if status not in STATUSES: return jsonify({'ok':False,'error':'Invalid status'}),400
    c=db(); o=c.execute('SELECT * FROM orders WHERE id=?',(order_id,)).fetchone();
    if not o: c.close(); return jsonify({'ok':False,'error':'Order not found'}),404
    c.execute('UPDATE orders SET status=? WHERE id=?',(status,order_id)); c.commit(); c.close()
    if o['email']:
        send_email(o['email'],f'MediSaarthi Order #{order_id} update',f'Your order #{order_id} status is now: {status}.\nTrack: {request.host_url}track/{order_id}')
    return jsonify({'ok':True})

@app.route('/admin')
def admin():
    c=db(); orders=c.execute('SELECT * FROM orders ORDER BY id DESC LIMIT 100').fetchall(); c.close(); return render_template('admin.html',orders=orders,statuses=STATUSES)

if __name__=='__main__':
    init_db(); app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=True)
