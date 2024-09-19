#!.venv/bin/python3

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Sequence

from gtts import gTTS
import os
import time
import random

MAX_NUMBER = 999
NUMBERS_RANGE = range(-MAX_NUMBER,MAX_NUMBER+1)

application = Flask(__name__)
application.config['SECRET_KEY'] = 'your_secret_key'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sequences.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(application)

def create_number_audio_files():
    for num in list(NUMBERS_RANGE):
        folder = f"{application.static_folder}/audio"
        path = f"{folder}/{num}.mp3"
        if not os.path.exists(path):
            tts = gTTS(text=str(num), lang='ru')
            time.sleep(2)  # to avoid gtts.tts.gTTSError: 429 (Too Many Requests) from TTS API. Probable cause: Unknown
            percent = round((list(NUMBERS_RANGE).index(num) / (MAX_NUMBER * 2)) * 100, 2)
            print(f"AUDIO GEN {percent} %", end="\r")
            if not os.path.exists(folder): os.mkdir(folder)
            tts.save(path)

# create_number_audio_files()

def calculate_answer(sequence_str):
    return sum(parse_sequence(sequence_str))

def parse_sequence(sequence_str):
    parts = sequence_str.replace(' ', '').replace('+', ' +').replace('-', ' -').split()
    sequence = [int(part) for part in parts]
    return sequence

@application.before_first_request
def create_tables():
    db.create_all()

@application.route('/teacher')
def teacher():
    sequences = Sequence.query.all()
    return render_template('teacher.html', sequences=sequences)

@application.route('/sequence')
def sequence():
    sequence_id = request.args.get('id', type=int)
    sound = request.args.get('sound', type=lambda v: v.lower() == 'true')
    speed = request.args.get('speed', type=float)
    sequence = Sequence.query.get_or_404(sequence_id)
    return render_template('sequence.html', 
                           sequence={
                               'id': sequence.id,
                               'speed': speed
                           },
                           sound=sound)

@application.route('/api/sequence/<int:id>')
def get_sequence(id):
    sequence = Sequence.query.get_or_404(id)
    return jsonify({
        'name': sequence.name,
        'numbers': [parse_sequence(content) for content in sequence.content.split(',')],
        'answers': sequence.answers
    })


@application.route('/student')
def student():
    sequences = Sequence.query.all()
    return render_template('student.html', sequences=sequences)

@application.route('/create_sequence', methods=['POST'])
def create_sequence():
    content = request.form['content']
    new_sequence = Sequence(name=request.form['name'], content=content)
    new_sequence.set_answers([calculate_answer(content) for content in content.split(',')])
    db.session.add(new_sequence)
    db.session.commit()
    flash('Последовательность создана успешно!', 'success')
    return redirect(url_for('teacher'))

@application.route('/edit_sequence/<int:id>', methods=['POST'])
def edit_sequence(id):
    sequence = Sequence.query.get_or_404(id)
    content = request.form['content']
    sequence.name = request.form['name']
    sequence.content = content
    sequence.set_answers([calculate_answer(content) for content in content.split(',')])
    db.session.commit()
    flash('Последовательность обновлена успешно!', 'success')
    return redirect(url_for('teacher'))

@application.route('/delete_sequence/<int:id>', methods=['POST'])
def delete_sequence(id):
    sequence = Sequence.query.get_or_404(id)
    db.session.delete(sequence)
    db.session.commit()
    return jsonify({"success": True, "message": "Последовательность успешно удалена!"})

@application.route('/generate_sequence', methods=['POST'])
def generate_sequence():
    name = request.form['name']

    min_count = int(request.form['min_count'])
    max_count = int(request.form['max_count'])
    
    min_length = int(request.form['min_length'])
    max_length = int(request.form['max_length'])

    min_number = int(request.form['min_number'])
    max_number = int(request.form['max_number'])

    content = ""
    count = random.randint(min_count, max_count)
    for i in range(count):
        sequence_content = []
        sequence_content.append(str(random.randint(min_number, max_number)))
        for _ in range(random.randint(min_length, max_length) - 1):
            op = random.choice(['+', '-'])
            num = random.randint(min_number, max_number)
            sequence_content.append(f" {op} {num}")
        content += "".join(sequence_content) + ', ' if i != count - 1 else "".join(sequence_content)
    
    sequence = Sequence(name=name, content=content)
    sequence.set_answers([calculate_answer(content) for content in content.split(',')])
    db.session.add(sequence)
    db.session.commit()

    flash('Последовательность успешно сгенерирована!', 'success')
    return redirect(url_for('teacher'))

if __name__ == '__main__':
    application.run(debug=True)