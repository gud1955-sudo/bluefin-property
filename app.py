import os, math, re, threading
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='프로젝트폴더/templates')
CORS(app)

# ── DB 설정 ──
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///property.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ══════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════

class SaleProperty(db.Model):
    __tablename__ = 'sale_properties'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    address     = db.Column(db.String(300))        # 지번 주소
    district    = db.Column(db.String(50))
    area        = db.Column(db.Float)              # 전용면적 ㎡
    floors      = db.Column(db.String(100))        # 예: 지하3/지상15층
    year        = db.Column(db.Integer)
    price       = db.Column(db.BigInteger)         # 만원 단위
    roi         = db.Column(db.Float)
    status      = db.Column(db.String(20), default='활성')
    agent       = db.Column(db.String(100))
    memo        = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'address': self.address,
            'district': self.district, 'area': self.area, 'floors': self.floors,
            'year': self.year, 'price': self.price, 'roi': self.roi,
            'status': self.status, 'agent': self.agent, 'memo': self.memo,
            'date': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }


class Building(db.Model):
    __tablename__ = 'buildings'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(200), nullable=False)
    address       = db.Column(db.String(300))      # 지번 주소
    district      = db.Column(db.String(50))
    total_area    = db.Column(db.Float)
    underground   = db.Column(db.String(50))
    aboveground   = db.Column(db.String(50))
    year          = db.Column(db.Integer)
    elevator      = db.Column(db.String(100))
    parking       = db.Column(db.String(100))
    hvac          = db.Column(db.String(100))
    grade         = db.Column(db.String(20))
    subway        = db.Column(db.String(200))
    features      = db.Column(db.Text)
    memo          = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    floors    = db.relationship('Floor',   backref='building', cascade='all, delete-orphan', lazy=True)
    memos     = db.relationship('Memo',    backref='building', cascade='all, delete-orphan', lazy=True)
    contacts  = db.relationship('Contact', backref='building', cascade='all, delete-orphan', lazy=True)

    def to_list_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'address': self.address or '', 'district': self.district or ''
        }

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'address': self.address,
            'district': self.district, 'totalArea': self.total_area,
            'underground': self.underground, 'aboveground': self.aboveground,
            'year': self.year, 'elevator': self.elevator, 'parking': self.parking,
            'hvac': self.hvac, 'grade': self.grade, 'subway': self.subway,
            'features': self.features, 'memo': self.memo,
            'floors':   [f.to_dict() for f in self.floors],
            'memos':    [m.to_dict() for m in sorted(self.memos,   key=lambda x: x.created_at, reverse=True)],
            'contacts': [c.to_dict() for c in self.contacts],
        }


class Floor(db.Model):
    __tablename__ = 'floors'
    id            = db.Column(db.Integer, primary_key=True)
    building_id   = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    floor         = db.Column(db.String(50))
    rent_area_py  = db.Column(db.Float)
    rent_area_sqm = db.Column(db.Float)
    own_area_py   = db.Column(db.Float)
    own_area_sqm  = db.Column(db.Float)
    deposit       = db.Column(db.BigInteger)       # 만원
    rent          = db.Column(db.BigInteger)       # 만원/월
    mgmt          = db.Column(db.BigInteger)       # 만원/월
    noc           = db.Column(db.Float)
    vacancy       = db.Column(db.String(20), default='공실아님')
    interior      = db.Column(db.String(5), default='무')
    parking       = db.Column(db.Integer, default=0)
    agent         = db.Column(db.String(100))
    lease_end     = db.Column(db.String(20))

    def to_dict(self):
        return {
            'id': self.id, 'floor': self.floor,
            'rentAreaPY': self.rent_area_py, 'rentAreaSQM': self.rent_area_sqm,
            'ownAreaPY':  self.own_area_py,  'ownAreaSQM':  self.own_area_sqm,
            'deposit': self.deposit, 'rent': self.rent, 'mgmt': self.mgmt,
            'noc': self.noc, 'vacancy': self.vacancy,
            'interior': self.interior, 'parking': self.parking, 'agent': self.agent,
            'leaseEnd': self.lease_end,
        }


class Memo(db.Model):
    __tablename__ = 'memos'
    id          = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    author      = db.Column(db.String(100))
    content     = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'author': self.author, 'content': self.content,
            'date': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Contact(db.Model):
    __tablename__ = 'contacts'
    id          = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    name        = db.Column(db.String(100))
    phone       = db.Column(db.String(100))
    title       = db.Column(db.String(100))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'phone': self.phone, 'title': self.title}


# ══════════════════════════════════════════
# ROUTES — 페이지
# ══════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    try:
        bld_cnt = Building.query.count()
        floor_cnt = Floor.query.count()
        contact_cnt = Contact.query.count()
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        db_type = 'PostgreSQL' if 'postgresql' in db_url else 'SQLite'
        return jsonify({'db': db_type, 'buildings': bld_cnt, 'floors': floor_cnt, 'contacts': contact_cnt})
    except Exception as e:
        return jsonify({'error': str(e)})


# ══════════════════════════════════════════
# API — 매매 매물
# ══════════════════════════════════════════

@app.route('/api/sales', methods=['GET'])
def get_sales():
    sales = SaleProperty.query.order_by(SaleProperty.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sales])

@app.route('/api/sales', methods=['POST'])
def create_sale():
    d = request.json
    s = SaleProperty(
        name=d.get('name'), address=d.get('address'), district=d.get('district'),
        area=d.get('area'), floors=d.get('floors'), year=d.get('year'),
        price=d.get('price'), roi=d.get('roi'), status=d.get('status','활성'),
        agent=d.get('agent'), memo=d.get('memo')
    )
    db.session.add(s); db.session.commit()
    return jsonify(s.to_dict()), 201

@app.route('/api/sales/<int:sid>', methods=['PUT'])
def update_sale(sid):
    s = SaleProperty.query.get_or_404(sid)
    d = request.json
    for field in ['name','address','district','area','floors','year','price','roi','status','agent','memo']:
        if field in d:
            setattr(s, field, d[field])
    db.session.commit()
    return jsonify(s.to_dict())

@app.route('/api/sales/<int:sid>', methods=['DELETE'])
def delete_sale(sid):
    s = SaleProperty.query.get_or_404(sid)
    db.session.delete(s); db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════
# API — 건물
# ══════════════════════════════════════════

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    q        = request.args.get('q', '').strip()
    district = request.args.get('district', '').strip()
    page     = max(1, int(request.args.get('page', 1)))
    per_page = max(1, min(100, int(request.args.get('per_page', 15))))

    query = Building.query
    if q:
        query = query.filter(db.or_(
            Building.name.ilike(f'%{q}%'),
            Building.address.ilike(f'%{q}%')
        ))
    if district:
        query = query.filter(Building.district == district)

    total = query.count()
    items = query.order_by(Building.created_at.desc()) \
                 .offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'items': [b.to_list_dict() for b in items],
        'total': total,
        'page':  page,
        'pages': math.ceil(total / per_page) if total else 1
    })

@app.route('/api/buildings/<int:bid>', methods=['GET'])
def get_building(bid):
    b = Building.query.get_or_404(bid)
    return jsonify(b.to_dict())

@app.route('/api/buildings', methods=['POST'])
def create_building():
    d = request.json
    b = Building(
        name=d.get('name'), address=d.get('address'), district=d.get('district'),
        total_area=d.get('totalArea'), underground=d.get('underground'),
        aboveground=d.get('aboveground'), year=d.get('year'),
        elevator=d.get('elevator'), parking=d.get('parking'), hvac=d.get('hvac'),
        grade=d.get('grade'), subway=d.get('subway'),
        features=d.get('features'), memo=d.get('memo')
    )
    db.session.add(b); db.session.commit()
    return jsonify(b.to_dict()), 201

@app.route('/api/buildings/<int:bid>', methods=['PUT'])
def update_building(bid):
    b = Building.query.get_or_404(bid)
    d = request.json
    field_map = {
        'name':'name','address':'address','district':'district',
        'totalArea':'total_area','underground':'underground','aboveground':'aboveground',
        'year':'year','elevator':'elevator','parking':'parking','hvac':'hvac',
        'grade':'grade','subway':'subway','features':'features','memo':'memo'
    }
    for k, attr in field_map.items():
        if k in d: setattr(b, attr, d[k])
    db.session.commit()
    return jsonify(b.to_dict())

@app.route('/api/buildings/<int:bid>', methods=['DELETE'])
def delete_building(bid):
    b = Building.query.get_or_404(bid)
    db.session.delete(b); db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════
# API — 층
# ══════════════════════════════════════════

@app.route('/api/buildings/<int:bid>/floors', methods=['POST'])
def create_floor(bid):
    Building.query.get_or_404(bid)
    d = request.json
    py   = d.get('ownAreaPY') or 0      # 전용면적 (평) ← 기준
    rent = d.get('rent') or 0
    mgmt = d.get('mgmt') or 0
    # NOC = (임대료 + 관리비) ÷ 전용면적(평)  단위: 만원/평
    noc = round((rent + mgmt) / py, 2) if py else d.get('noc') or 0
    f = Floor(
        building_id=bid, floor=d.get('floor'),
        rent_area_py=d.get('rentAreaPY'), rent_area_sqm=d.get('rentAreaSQM'),
        own_area_py=d.get('ownAreaPY'),   own_area_sqm=d.get('ownAreaSQM'),
        deposit=d.get('deposit'), rent=rent, mgmt=mgmt, noc=noc,
        vacancy=d.get('vacancy','공실아님'), interior=d.get('interior','무'),
        parking=d.get('parking',0), agent=d.get('agent'), lease_end=d.get('leaseEnd')
    )
    db.session.add(f); db.session.commit()
    return jsonify(f.to_dict()), 201

@app.route('/api/floors/<int:fid>', methods=['PUT'])
def update_floor(fid):
    f = Floor.query.get_or_404(fid)
    d = request.json
    field_map = {
        'floor':'floor', 'rentAreaPY':'rent_area_py', 'rentAreaSQM':'rent_area_sqm',
        'ownAreaPY':'own_area_py', 'ownAreaSQM':'own_area_sqm',
        'deposit':'deposit', 'rent':'rent', 'mgmt':'mgmt',
        'vacancy':'vacancy', 'interior':'interior', 'parking':'parking', 'agent':'agent',
        'leaseEnd':'lease_end'
    }
    for k, attr in field_map.items():
        if k in d: setattr(f, attr, d[k])
    # NOC = (임대료 + 관리비) ÷ 전용면적(평)
    py = f.own_area_py or 0
    if py and (f.rent or f.mgmt):
        f.noc = round(((f.rent or 0) + (f.mgmt or 0)) / py, 2)
    db.session.commit()
    return jsonify(f.to_dict())

@app.route('/api/floors/<int:fid>', methods=['DELETE'])
def delete_floor(fid):
    f = Floor.query.get_or_404(fid)
    db.session.delete(f); db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════
# API — 메모
# ══════════════════════════════════════════

@app.route('/api/buildings/<int:bid>/memos', methods=['POST'])
def create_memo(bid):
    Building.query.get_or_404(bid)
    d = request.json
    m = Memo(building_id=bid, author=d.get('author'), content=d.get('content'))
    db.session.add(m); db.session.commit()
    return jsonify(m.to_dict()), 201

@app.route('/api/memos/<int:mid>', methods=['DELETE'])
def delete_memo(mid):
    m = Memo.query.get_or_404(mid)
    db.session.delete(m); db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════
# API — 연락처
# ══════════════════════════════════════════

@app.route('/api/buildings/<int:bid>/contacts', methods=['POST'])
def create_contact(bid):
    Building.query.get_or_404(bid)
    d = request.json
    c = Contact(building_id=bid, name=d.get('name'), phone=d.get('phone'), title=d.get('title'))
    db.session.add(c); db.session.commit()
    return jsonify(c.to_dict()), 201

@app.route('/api/contacts/<int:cid>', methods=['DELETE'])
def delete_contact(cid):
    c = Contact.query.get_or_404(cid)
    db.session.delete(c); db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════
# INIT
# ══════════════════════════════════════════

def seed_from_sqlite():
    import sqlite3
    sqlite_path = os.path.join(os.path.dirname(__file__), 'instance', 'property.db')
    if not os.path.exists(sqlite_path):
        print('[seed] SQLite 파일 없음')
        return

    src = sqlite3.connect(sqlite_path)
    src.row_factory = sqlite3.Row
    cur = src.cursor()

    # 건물 복사 (id 매핑 유지)
    cur.execute('SELECT * FROM buildings')
    buildings = cur.fetchall()
    id_map = {}
    for row in buildings:
        b = Building(
            name=row['name'], address=row['address'], district=row['district'],
            total_area=row['total_area'], underground=row['underground'],
            aboveground=row['aboveground'], year=row['year'],
            elevator=row['elevator'], parking=row['parking'], hvac=row['hvac'],
            grade=row['grade'], subway=row['subway'],
            features=row['features'], memo=row['memo']
        )
        db.session.add(b)
        db.session.flush()
        id_map[row['id']] = b.id

    # 연락처 복사
    cur.execute('SELECT * FROM contacts')
    for row in cur.fetchall():
        if row['building_id'] in id_map:
            db.session.add(Contact(
                building_id=id_map[row['building_id']],
                name=row['name'], phone=row['phone'], title=row['title']
            ))

    # 층별 임대 정보 복사
    cur.execute('SELECT * FROM floors')
    for row in cur.fetchall():
        if row['building_id'] in id_map:
            db.session.add(Floor(
                building_id=id_map[row['building_id']],
                floor=row['floor'],
                rent_area_py=row['rent_area_py'], rent_area_sqm=row['rent_area_sqm'],
                own_area_py=row['own_area_py'],   own_area_sqm=row['own_area_sqm'],
                deposit=row['deposit'], rent=row['rent'], mgmt=row['mgmt'], noc=row['noc'],
                vacancy=row['vacancy'], interior=row['interior'],
                parking=row['parking'], agent=row['agent']
            ))

    # 매매 매물 복사
    cur.execute('SELECT * FROM sale_properties')
    for row in cur.fetchall():
        db.session.add(SaleProperty(
            name=row['name'], address=row['address'], district=row['district'],
            area=row['area'], floors=row['floors'], year=row['year'],
            price=row['price'], roi=row['roi'], status=row['status'],
            agent=row['agent'], memo=row['memo']
        ))

    db.session.commit()
    src.close()
    print(f'[seed] 완료: 건물 {len(id_map)}개 복사')


def _bg_seed():
    import time
    time.sleep(3)
    with app.app_context():
        try:
            if Building.query.count() == 0:
                print('[seed] DB가 비어 있습니다. SQLite에서 데이터를 복사합니다...')
                seed_from_sqlite()
        except Exception as e:
            print(f'[seed] 오류: {e}')

with app.app_context():
    try:
        db.create_all()
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE floors ADD COLUMN lease_end VARCHAR(20)"))
                conn.commit()
        except Exception:
            pass  # 이미 존재하면 무시
        if Building.query.count() == 0:
            threading.Thread(target=_bg_seed, daemon=True).start()
    except Exception as e:
        print(f'[init] DB 연결 오류: {e}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
