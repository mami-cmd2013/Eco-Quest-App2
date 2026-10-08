import random
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'ecotrack_offline_economy_key'

WASTE_REWARDS = {
    'Plastik Şişe / Kap': 50,
    'Metal İçecek Kutusu': 75,
    'Karton / Kağıt': 30,
    'Elektronik Atık / Pil': 100
}

TREE_TYPES = {
    'pine': {'name': '🌲 Çam Ağacı', 'o2': 1.5, 'cost': 80},
    'oak': {'name': '🌳 Ulu Meşe', 'o2': 2.5, 'cost': 150},
    'palm': {'name': '🌴 Palmiye', 'o2': 3.0, 'cost': 200},
    'cherry': {'name': '🌸 Sakura / Kiraz', 'o2': 4.0, 'cost': 300}
}

BASE_CROP_TYPES = {
    'tomato': {'name': '🍅 Domates', 'seed_cost': 15, 'base_sell_price': 35},
    'pepper': {'name': '🫑 Biber', 'seed_cost': 20, 'base_sell_price': 45},
    'cucumber': {'name': '🥒 Salatalık', 'seed_cost': 10, 'base_sell_price': 25}
}

GARDEN_CUSTOMIZATIONS = {
    'scarecrow': {'name': '🌾 Altın Korkuluk', 'desc': 'Tarlanı korur ve görsellik katar.'},
    'pathway': {'name': '🪨 Taş & Çiçekli Patika', 'desc': 'Bahçene estetik bir yürüyüş yolu ekler.'},
    'greenhouse': {'name': '🪟 Cam Eko-Sera', 'desc': 'Profesyonel bir sera görünümü kazandırır.'}
}

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Plastik bir şişenin doğada yok olması ortalama kaç yıl sürer?",
        "options": {"A": "50 Yıl", "B": "450 Yıl", "C": "10 Yıl"},
        "correct": "B"
    },
    {
        "id": 2,
        "question": "Dünyadaki oksijenin yaklaşık %70'ini aşağıdakilerden hangisi üretir?",
        "options": {"A": "Okyanuslardaki Fitoplanktonlar", "B": "Amazon Ormanları", "C": "Çam Ormanları"},
        "correct": "A"
    },
    {
        "id": 3,
        "question": "Bir damla sızdıran musluk yılda yaklaşık kaç litre su israf eder?",
        "options": {"A": "1.000 Litre", "B": "11.000 Litre", "C": "500 Litre"},
        "correct": "B"
    },
    {
        "id": 4,
        "question": "Sera gazı emisyonlarının en büyük kaynağı hangi sektördür?",
        "options": {"A": "Ulaşım", "B": "Tarım", "C": "Enerji Üretimi"},
        "correct": "C"
    },
    {
        "id": 5,
        "question": "Geri dönüştürülen 1 ton kağıt kaç ağacın kesilmesini önler?",
        "options": {"A": "17 Ağaç", "B": "5 Ağaç", "C": "50 Ağaç"},
        "correct": "A"
    },
    {
        "id": 6,
        "question": "Aşağıdakilerden hangisi yenilenebilir bir enerji kaynağı değildir?",
        "options": {"A": "Güneş", "B": "Doğalgaz", "C": "Rüzgar"},
        "correct": "B"
    },
    {
        "id": 7,
        "question": "Cam ambalajlar doğada kaç yılda yok olur?",
        "options": {"A": "100 Yıl", "B": "1000 Yıl", "C": "4000+ Yıl / Yok Olmaz"},
        "correct": "C"
    },
    {
        "id": 8,
        "question": "Kullanılmış 1 litre atık yağ kaç litre temiz suyu kirletir?",
        "options": {"A": "10.000 Litre", "B": "1.000.000 Litre", "C": "100 Litre"},
        "correct": "B"
    },
    {
        "id": 9,
        "question": "Kompost yapmak ne anlama gelir?",
        "options": {"A": "Plastiği eritmek", "B": "Organik atıkları gübreye dönüştürmek", "C": "Kağıdı yakmak"},
        "correct": "B"
    },
    {
        "id": 10,
        "question": "Karbon ayak izini azaltmak için en etkili bireysel adım nedir?",
        "options": {"A": "Daha az et tüketmek ve toplu taşıma kullanmak", "B": "Daha çok TV izlemek", "C": "Plastik poşet biriktirmek"},
        "correct": "A"
    }
]

DAILY_FACTS = [
    "💧 Bir damla sızdıran musluk, yılda 11.000 litre su israfına neden olur.",
    "🌳 Bir yetişkin ağaç, yılda yaklaşık 22 kg karbondioksit emer.",
    "📱 Eski bir telefonu geri dönüştürmek, 24 kg sera gazı emisyonunu engeller.",
    "🛍️ Bir plastik poşetin ortalama kullanım süresi 12 dakika, doğada kalma süresi 500 yıldır."
]

WORLD_NEWS = [
    {"baslik": "BM İklim Zirvesi", "ozet": "Yenilenebilir enerji yatırımları %40 arttı."},
    {"baslik": "Amazon Ormanları", "ozet": "10 milyon yeni fidan dikimi başlatıldı."}
]

DAILY_TASKS = [
    "Diş fırçalarken musluğu kapalı tut.",
    "Bugün alışverişte bez çanta kullan.",
    "Kısa mesafeleri yürüyerek git.",
    "Evdeki kullanılmayan fişleri prizden çek."
]

def calculate_total_o2():
    tree_o2 = sum(session.get('trees', {}).get(t_key, 0) * data['o2'] for t_key, data in TREE_TYPES.items())
    gardener_o2 = 2.0 if session.get('has_gardener') else 0.0
    fence_o2 = 1.5 if session.get('has_fence') else 0.0
    fertilizer_o2 = session.get('fertilizer_count', 0) * 2.0
    return round(tree_o2 + gardener_o2 + fence_o2 + fertilizer_o2, 1)

def get_dynamic_crop_types(total_o2):
    o2_bonus = int(round(total_o2))
    dynamic_crops = {}
    for key, data in BASE_CROP_TYPES.items():
        dynamic_crops[key] = {
            'name': data['name'],
            'seed_cost': data['seed_cost'],
            'sell_price': data['base_sell_price'] + o2_bonus
        }
    return dynamic_crops

@app.context_processor
def inject_eco_economy():
    if 'eco_coins' not in session:
        session['eco_coins'] = 250
    if 'has_gardener' not in session:
        session['has_gardener'] = False
    if 'has_fence' not in session:
        session['has_fence'] = False
    if 'has_farm' not in session:
        session['has_farm'] = False
    if 'fertilizer_count' not in session:
        session['fertilizer_count'] = 0
    if 'trees' not in session:
        session['trees'] = {'pine': 1, 'oak': 1, 'palm': 0, 'cherry': 0}
    if 'farm_crops' not in session:
        session['farm_crops'] = {'tomato': 0, 'pepper': 0, 'cucumber': 0}
    if 'harvested_crops' not in session:
        session['harvested_crops'] = {'tomato': 0, 'pepper': 0, 'cucumber': 0}
    if 'unlocked_customizations' not in session:
        session['unlocked_customizations'] = []
    if 'streak' not in session:
        session['streak'] = 5
    if 'task_completed' not in session:
        session['task_completed'] = False
    if 'quiz_index' not in session:
        session['quiz_index'] = 0
    if 'carbon_footprint' not in session:
        session['carbon_footprint'] = None

    if 'farmer_quest' not in session or session['farmer_quest'] is None:
        if session.get('has_farm') and random.random() < 0.6:
            crop_key = random.choice(['tomato', 'pepper', 'cucumber'])
            req_amount = random.randint(2, 5)
            
            available_rewards = [k for k in GARDEN_CUSTOMIZATIONS.keys() if k not in session['unlocked_customizations']]
            reward_id = random.choice(available_rewards) if available_rewards else None

            session['farmer_quest'] = {
                'crop_key': crop_key,
                'crop_name': BASE_CROP_TYPES[crop_key]['name'],
                'amount': req_amount,
                'reward_coins': req_amount * 60,
                'reward_id': reward_id
            }

    total_o2 = calculate_total_o2()
    crop_types = get_dynamic_crop_types(total_o2)
    total_tree_count = sum(session['trees'].values())
    today_idx = datetime.now().timetuple().tm_yday % len(DAILY_FACTS)

    quiz_idx = session.get('quiz_index', 0)
    current_question = QUIZ_QUESTIONS[quiz_idx] if quiz_idx < len(QUIZ_QUESTIONS) else None

    return dict(
        eco_coins=session['eco_coins'],
        trees=session['trees'],
        tree_types=TREE_TYPES,
        crop_types=crop_types,
        farm_crops=session['farm_crops'],
        harvested_crops=session['harvested_crops'],
        unlocked_customizations=session['unlocked_customizations'],
        garden_customizations=GARDEN_CUSTOMIZATIONS,
        farmer_quest=session.get('farmer_quest'),
        carbon_footprint=session.get('carbon_footprint'),
        total_tree_count=total_tree_count,
        has_gardener=session['has_gardener'],
        has_fence=session['has_fence'],
        has_farm=session['has_farm'],
        fertilizer_count=session['fertilizer_count'],
        total_o2=total_o2,
        o2_bonus=int(round(total_o2)),
        streak=session['streak'],
        task_completed=session['task_completed'],
        quiz_index=quiz_idx,
        current_question=current_question,
        total_questions=len(QUIZ_QUESTIONS),
        daily_fact=DAILY_FACTS[today_idx],
        world_news=WORLD_NEWS,
        daily_task=DAILY_TASKS[today_idx % len(DAILY_TASKS)]
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan-waste', methods=['POST'])
def scan_waste():
    waste_type = request.form.get('waste_type', 'Plastik Şişe / Kap')
    earned = WASTE_REWARDS.get(waste_type, 50)
    session['eco_coins'] += earned
    
    scan_result = {
        'waste_type': waste_type,
        'earned': earned,
        'bin': 'Sarı Kutu (Geri Dönüştürülebilir Plastik/Metal)' if 'Plastik' in waste_type or 'Metal' in waste_type else 'Mavi Kutu (Kağıt/Karton)'
    }
    return render_template('index.html', scan_result=scan_result)

@app.route('/calculate-carbon', methods=['POST'])
def calculate_carbon():
    transport = float(request.form.get('transport', 1.5))
    diet = float(request.form.get('diet', 1.5))
    energy = float(request.form.get('energy', 1.0))

    total_carbon = round(transport + diet + energy, 1)
    
    # İlk kez hesaplıyorsa 50 Eko-Para ödülü ver
    if session.get('carbon_footprint') is None:
        session['eco_coins'] += 50
        
    session['carbon_footprint'] = total_carbon
    return redirect(url_for('index'))

@app.route('/buy-item/<item_type>/<item_id>')
def buy_item(item_type, item_id):
    coins = session.get('eco_coins', 0)

    if item_type == 'tree' and item_id in TREE_TYPES:
        cost = TREE_TYPES[item_id]['cost']
        if coins >= cost:
            session['eco_coins'] -= cost
            trees = session.get('trees', {})
            trees[item_id] = trees.get(item_id, 0) + 1
            session['trees'] = trees

    elif item_type == 'upgrade':
        if item_id == 'gardener' and coins >= 100 and not session.get('has_gardener'):
            session['eco_coins'] -= 100
            session['has_gardener'] = True
        elif item_id == 'fence' and coins >= 80 and not session.get('has_fence'):
            session['eco_coins'] -= 80
            session['has_fence'] = True
        elif item_id == 'farm' and coins >= 120 and not session.get('has_farm'):
            session['eco_coins'] -= 120
            session['has_farm'] = True
        elif item_id == 'fertilizer' and coins >= 40 and session.get('has_farm'):
            session['eco_coins'] -= 40
            session['fertilizer_count'] = session.get('fertilizer_count', 0) + 1

    return redirect(url_for('index'))

@app.route('/plant-crop/<crop_id>')
def plant_crop(crop_id):
    coins = session.get('eco_coins', 0)
    if crop_id in BASE_CROP_TYPES and session.get('has_farm'):
        cost = BASE_CROP_TYPES[crop_id]['seed_cost']
        if coins >= cost:
            session['eco_coins'] -= cost
            farm_crops = session.get('farm_crops', {})
            farm_crops[crop_id] = farm_crops.get(crop_id, 0) + 1
            session['farm_crops'] = farm_crops
    return redirect(url_for('index'))

@app.route('/harvest_crop/<crop_id>')
def harvest_crop(crop_id):
    farm_crops = session.get('farm_crops', {})
    if farm_crops.get(crop_id, 0) > 0:
        farm_crops[crop_id] -= 1
        session['farm_crops'] = farm_crops
        
        harvested = session.get('harvested_crops', {})
        harvested[crop_id] = harvested.get(crop_id, 0) + 1
        session['harvested_crops'] = harvested
    return redirect(url_for('index'))

@app.route('/sell_crop/<crop_id>')
def sell_crop(crop_id):
    harvested = session.get('harvested_crops', {})
    if harvested.get(crop_id, 0) > 0 and crop_id in BASE_CROP_TYPES:
        total_o2 = calculate_total_o2()
        crop_types = get_dynamic_crop_types(total_o2)
        
        harvested[crop_id] -= 1
        session['harvested_crops'] = harvested
        session['eco_coins'] += crop_types[crop_id]['sell_price']
    return redirect(url_for('index'))

@app.route('/complete-farmer-quest')
def complete_farmer_quest():
    quest = session.get('farmer_quest')
    harvested = session.get('harvested_crops', {})

    if quest and harvested.get(quest['crop_key'], 0) >= quest['amount']:
        harvested[quest['crop_key']] -= quest['amount']
        session['harvested_crops'] = harvested

        session['eco_coins'] += quest['reward_coins']
        if quest['reward_id'] and quest['reward_id'] not in session['unlocked_customizations']:
            unlocked = session.get('unlocked_customizations', [])
            unlocked.append(quest['reward_id'])
            session['unlocked_customizations'] = unlocked

        session['farmer_quest'] = None
    return redirect(url_for('index'))

@app.route('/dismiss-farmer-quest')
def dismiss_farmer_quest():
    session['farmer_quest'] = None
    return redirect(url_for('index'))

@app.route('/answer-quiz', methods=['POST'])
def answer_quiz():
    selected_option = request.form.get('option')
    quiz_idx = session.get('quiz_index', 0)

    if quiz_idx < len(QUIZ_QUESTIONS):
        q = QUIZ_QUESTIONS[quiz_idx]
        if selected_option == q['correct']:
            session['eco_coins'] += 20
            session['quiz_index'] += 1
            quiz_msg = "✅ Doğru cevap! +20 Eko-Para kazandınız. Sonraki soruya geçildi."
        else:
            quiz_msg = "❌ Yanlış cevap! Tekrar deneyin."
    else:
        quiz_msg = "🎉 Tüm quizi zaten bitirdiniz!"

    return render_template('index.html', quiz_msg=quiz_msg)

@app.route('/complete-task', methods=['POST'])
def complete_task():
    if not session.get('task_completed', False):
        session['streak'] += 1
        session['eco_coins'] += 30
        session['task_completed'] = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)