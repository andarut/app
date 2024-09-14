#!.venv/bin/python3

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Sequence

from gtts import gTTS
import os
import random

# -9, ..., 9
NUMBERS_RANGE = range(-9,10)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sequences.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_number_audio_files():
    for num in list(NUMBERS_RANGE):
        tts = gTTS(text=str(num), lang='ru')
        path = f"static/audio/{num}.mp3"
        if not os.path.exists(path):
            tts.save(path)

create_number_audio_files()

def calculate_answer(sequence_str):
    return sum(parse_sequence(sequence_str))

def parse_sequence(sequence_str):
    parts = sequence_str.replace(' ', '').replace('+', ' +').replace('-', ' -').split()
    sequence = [int(part) for part in parts]
    return sequence

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/teacher')
def teacher():
    sequences = Sequence.query.all()
    return render_template('teacher.html', sequences=sequences)

@app.route('/sequence')
def sequence():
    sequence_id = request.args.get('id', type=int)
    sound = request.args.get('sound', type=lambda v: v.lower() == 'true')
    speed = request.args.get('speed', type=int)
    sequence = Sequence.query.get_or_404(sequence_id)
    return render_template('sequence.html', 
                           sequence={
                               'id': sequence.id,
                               'speed': speed
                           },
                           sound=sound)

@app.route('/api/sequence/<int:id>')
def get_sequence(id):
    sequence = Sequence.query.get_or_404(id)
    return jsonify({
        'name': sequence.name,
        'numbers': parse_sequence(sequence.content),
        'answer': sequence.answer
    })


@app.route('/student')
def student():
    sequences = Sequence.query.all()
    return render_template('student.html', sequences=sequences)

@app.route('/create_sequence', methods=['POST'])
def create_sequence():
    name = request.form['name']
    content = request.form['content']
    answer = calculate_answer(request.form['content'])
    new_sequence = Sequence(name=name, content=content, answer=answer)
    db.session.add(new_sequence)
    db.session.commit()
    flash('Последовательность создана успешно!', 'success')
    return redirect(url_for('teacher'))

@app.route('/edit_sequence/<int:id>', methods=['POST'])
def edit_sequence(id):
    sequence = Sequence.query.get_or_404(id)
    sequence.name = request.form['name']
    sequence.content = request.form['content']
    sequence.answer = calculate_answer(request.form['content'])
    db.session.commit()
    flash('Последовательность обновлена успешно!', 'success')
    return redirect(url_for('teacher'))

@app.route('/delete_sequence/<int:id>', methods=['POST'])
def delete_sequence(id):
    sequence = Sequence.query.get_or_404(id)
    db.session.delete(sequence)
    db.session.commit()
    return jsonify({"success": True, "message": "Последовательность успешно удалена!"})

@app.route('/generate_sequence', methods=['POST'])
def generate_sequence():
    name = request.form['name']
    length = int(request.form['length'])
    min_number = int(request.form['min_number'])
    max_number = int(request.form['max_number'])

    sequence = []
    result = random.randint(min_number, max_number)  # Начинаем с случайного числа от 1 до 10
    sequence.append(str(result))

    for _ in range(length - 1):  # Уменьшаем на 1, так как первое число уже добавлено
        op = random.choice(['+', '-'])
        num = random.randint(min_number, max_number)  # Используем положительные числа для простоты

        if op == '+':
            result += num
        elif op == '-':
            result -= num
        
        sequence.append(f" {op} {num}")  # Добавляем пробелы вокруг операции и числа

    content = "".join(sequence)  # Объединяем элементы без дополнительных запятых
    answer = result
    
    new_sequence = Sequence(name=name, content=content, answer=answer)
    db.session.add(new_sequence)
    db.session.commit()

    flash('Последовательность успешно сгенерирована!', 'success')
    return redirect(url_for('teacher'))

if __name__ == '__main__':
    app.run(debug=True)