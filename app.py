"""
====================================================================
  ECO-QUEST: İKLİM DEĞİŞİKLİĞİ VE FARKINDALIK PORTALI (FLASK BACKEND)
====================================================================
"""

from flask import Flask, render_template, request, session, flash

app = Flask(__name__)
# Oturum (Session) güvenliği için gizli anahtar
app.secret_key = "eco_quest_super_secret_key_2026"

# -------------------------------------------------------------------
# QUIZ SORULARI VE BİLGİLERİ
# -------------------------------------------------------------------
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Küresel ısınmaya en çok katkıda bulunan sera gazı hangisidir?",
        "options": ["Oksijen", "Karbondioksit (CO2)", "Azot", "Helyum"],
        "answer": "Karbondioksit (CO2)",
        "explanation": "Karbondioksit, fosil yakıt kullanımı nedeniyle en büyük sera etkisini yaratır."
    },
    {
        "id": 2,
        "question": "Bireysel karbon ayak izini azaltmanın en etkili yollarından biri nedir?",
        "options": [
            "Daha fazla plastik kullanmak",
            "Toplu taşıma veya bisiklet tercih etmek",
            "Işıkları sürekli açık bırakmak",
            "Kırmızı et tüketimini aşırı artırmak"
        ],
        "answer": "Toplu taşıma veya bisiklet tercih etmek",
        "explanation": "Ulaşımda bisiklet veya toplu taşıma kullanmak emisyonu ciddi oranda düşürür."
    },
    {
        "id": 3,
        "question": "Yenilenebilir enerji kaynaklarına hangisi örnek verilebilir?",
        "options": ["Kömür", "Rüzgar Enerjisi", "Petrol", "Doğalgaz"],
        "answer": "Rüzgar Enerjisi",
        "explanation": "Rüzgar, güneş ve hidroelektrik gibi kaynaklar doğa tarafından sürekli yenilenir."
    }
]

# -------------------------------------------------------------------
# SAYFA YÖNLENDİRMELERİ (ROUTING)
# -------------------------------------------------------------------

@app.route('/')
def home():
    """Ana sayfa."""
    return render_template('index.html', title="Eco-Quest - Ana Sayfa")


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """İklim quizi ve puan hesaplaması."""
    if request.method == 'POST':
        user_score = 0
        results = []
        for q in QUIZ_QUESTIONS:
            selected = request.form.get(f"q_{q['id']}")
            is_correct = (selected == q['answer'])
            if is_correct:
                user_score += 1
            results.append({
                "question": q['question'],
                "selected": selected,
                "correct_answer": q['answer'],
                "is_correct": is_correct,
                "explanation": q['explanation']
            })
        session['quiz_score'] = user_score
        return render_template(
            'quiz.html', 
            questions=QUIZ_QUESTIONS, 
            submitted=True, 
            score=user_score, 
            total=len(QUIZ_QUESTIONS), 
            results=results
        )
    return render_template('quiz.html', questions=QUIZ_QUESTIONS, submitted=False)


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    """Günlük karbon ayak izi hesaplayıcı."""
    carbon_result = None
    if request.method == 'POST':
        try:
            km = float(request.form.get('km', 0))
            kwh = float(request.form.get('kwh', 0))
            meat = float(request.form.get('meat', 0))
            
            # Karbon Ayak İzi Formülü (kg CO2)
            total_co2 = (km * 0.12) + (kwh * 0.45) + (meat * 2.5)
            carbon_result = round(total_co2, 2)
        except ValueError:
            flash("Lütfen geçerli sayılar girin!", "error")
            
    return render_template('calculator.html', carbon_result=carbon_result)


# -------------------------------------------------------------------
# UYGULAMA BAŞLATICI
# -------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)