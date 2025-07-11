from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import json
import os
import random
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# File paths
DATA_FILE = "questions.json"
PENDING_FILE = "pending_questions.json"
CONFIG_FILE = "admin_config.json"


# Helper functions
def load_admin_password():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"admin_password": "Aslankeren"}, f)
        return "Aslankeren"

    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"admin_password": "Aslankeren"}, f)
                return "Aslankeren"
            data = json.loads(content)
            return data.get("admin_password", "Aslankeren")
    except (json.JSONDecodeError, FileNotFoundError):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"admin_password": "Aslankeren"}, f)
        return "Aslankeren"


def load_questions():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        return []

    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                with open(DATA_FILE, "w") as f:
                    json.dump([], f)
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        return []


def load_pending():
    if not os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "w") as f:
            json.dump([], f)
        return []

    try:
        with open(PENDING_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                with open(PENDING_FILE, "w") as f:
                    json.dump([], f)
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        with open(PENDING_FILE, "w") as f:
            json.dump([], f)
        return []


def save_question(new_q):
    try:
        data = load_questions()
        data.append(new_q)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving question: {e}")


def save_pending(new_q):
    try:
        data = load_pending()
        data.append(new_q)
        with open(PENDING_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving pending question: {e}")


def save_admin_password(new_password):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"admin_password": new_password}, f)
    except Exception as e:
        print(f"Error saving admin password: {e}")


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bobytdb - Kuis Trivia</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }

        .bg-animation::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: float 20s linear infinite;
        }

        @keyframes float {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-100px) rotate(360deg); }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .logo {
            font-size: 3rem;
            font-weight: 800;
            color: white;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            margin-bottom: 10px;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { text-shadow: 0 4px 20px rgba(0,0,0,0.3); }
            to { text-shadow: 0 4px 30px rgba(255,255,255,0.6); }
        }

        .subtitle {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.9);
            margin-bottom: 20px;
        }

        .card {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            background: rgba(255,255,255,0.2);
        }

        .btn {
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }

        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
        }

        .btn-success {
            background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        }

        .btn-danger {
            background: linear-gradient(45deg, #ff416c, #ff4757);
        }

        .btn-warning {
            background: linear-gradient(45deg, #f7b733, #fc4a1a);
        }

        .btn-admin {
            background: linear-gradient(45deg, #2c3e50, #34495e);
            font-size: 0.8rem;
            padding: 8px 16px;
            position: absolute;
            top: 20px;
            right: 20px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: white;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .form-control {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: rgba(255,255,255,0.6);
            background: rgba(255,255,255,0.2);
        }

        .form-control::placeholder {
            color: rgba(255,255,255,0.6);
        }

        .quiz-question {
            font-size: 1.5rem;
            color: white;
            margin-bottom: 30px;
            text-align: center;
            font-weight: 600;
        }

        .quiz-choices {
            display: grid;
            gap: 15px;
            margin-bottom: 30px;
        }

        .choice-btn {
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 15px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1rem;
        }

        .choice-btn:hover {
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.5);
            transform: translateX(10px);
        }

        .timer {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1rem;
        }

        .score-display {
            text-align: center;
            color: white;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }

        .admin-panel {
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }

        .question-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .question-item {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
        }

        .modal-content {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            margin: 5% auto;
            padding: 30px;
            border-radius: 20px;
            width: 80%;
            max-width: 500px;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .hidden {
            display: none;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .nav-tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 5px;
        }

        .nav-tab {
            flex: 1;
            padding: 15px 20px;
            background: transparent;
            border: none;
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .nav-tab.active {
            background: rgba(255,255,255,0.2);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 10px;
            color: white;
        }

        .alert-success {
            background: rgba(40, 167, 69, 0.8);
        }

        .alert-danger {
            background: rgba(220, 53, 69, 0.8);
        }

        .alert-info {
            background: rgba(23, 162, 184, 0.8);
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            .logo {
                font-size: 2rem;
            }

            .btn {
                padding: 12px 24px;
                font-size: 0.9rem;
            }

            .modal-content {
                width: 95%;
                margin: 10% auto;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>

    {% if session.get('admin_mode') %}
        <button class="btn btn-admin" onclick="logout()">
            <i class="fas fa-sign-out-alt"></i> Logout Admin
        </button>
    {% else %}
        <button class="btn btn-admin" onclick="showAdminLogin()">
            <i class="fas fa-user-shield"></i> Admin
        </button>
    {% endif %}

    <div class="container">
        <div class="header">
            <h1 class="logo">
                <i class="fas fa-brain"></i> Bobytdb
            </h1>
            <p class="subtitle">Kuis Trivia Modern & Interaktif</p>
        </div>

        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('home')">
                <i class="fas fa-home"></i> Home
            </button>
            <button class="nav-tab" onclick="showTab('add-question')">
                <i class="fas fa-plus"></i> Tambah Soal
            </button>
            {% if session.get('admin_mode') %}
                <button class="nav-tab" onclick="showTab('admin')">
                    <i class="fas fa-cog"></i> Admin Panel
                </button>
            {% endif %}
        </div>

        <div id="home" class="tab-content active">
            <div class="card">
                <h2 style="color: white; text-align: center; margin-bottom: 30px;">
                    <i class="fas fa-play-circle"></i> Mulai Petualangan Quiz
                </h2>
                <div style="text-align: center;">
                    <button class="btn btn-primary" onclick="startQuiz()">
                        <i class="fas fa-rocket"></i> Mulai Kuis
                    </button>
                    <div style="margin-top: 20px; color: rgba(255,255,255,0.8);">
                        <p><i class="fas fa-info-circle"></i> Total Pertanyaan: {{ total_questions }}</p>
                    </div>
                </div>
            </div>
        </div>

        <div id="add-question" class="tab-content">
            <div class="card">
                <h2 style="color: white; text-align: center; margin-bottom: 30px;">
                    <i class="fas fa-plus-circle"></i> Tambah Pertanyaan Baru
                </h2>
                <form id="questionForm">
                    <div class="form-group">
                        <label>Jenis Pertanyaan:</label>
                        <select class="form-control" id="questionType" onchange="updateQuestionType()">
                            <option value="custom">Pilihan Ganda</option>
                            <option value="tf">True/False</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Pertanyaan:</label>
                        <input type="text" class="form-control" id="questionText" placeholder="Masukkan pertanyaan..." required>
                    </div>

                    <div id="choicesContainer">
                        <div class="form-group">
                            <label>Pilihan A:</label>
                            <input type="text" class="form-control" id="choiceA" placeholder="Pilihan A" required>
                        </div>
                        <div class="form-group">
                            <label>Pilihan B:</label>
                            <input type="text" class="form-control" id="choiceB" placeholder="Pilihan B" required>
                        </div>
                        <div class="form-group">
                            <label>Pilihan C:</label>
                            <input type="text" class="form-control" id="choiceC" placeholder="Pilihan C" required>
                        </div>
                        <div class="form-group">
                            <label>Pilihan D:</label>
                            <input type="text" class="form-control" id="choiceD" placeholder="Pilihan D" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Jawaban Benar:</label>
                        <input type="text" class="form-control" id="correctAnswer" placeholder="Masukkan jawaban yang benar..." required>
                    </div>

                    <div style="text-align: center;">
                        <button type="submit" class="btn btn-success">
                            <i class="fas fa-save"></i> Simpan Pertanyaan
                        </button>
                    </div>
                </form>
            </div>
        </div>

        {% if session.get('admin_mode') %}
        <div id="admin" class="tab-content">
            <div class="card">
                <h2 style="color: white; text-align: center; margin-bottom: 30px;">
                    <i class="fas fa-shield-alt"></i> Panel Admin
                </h2>

                <div style="text-align: center; margin-bottom: 30px;">
                    <button class="btn btn-warning" onclick="showPendingQuestions()">
                        <i class="fas fa-clock"></i> Pertanyaan Pending ({{ pending_count }})
                    </button>
                    <button class="btn btn-danger" onclick="showManageQuestions()">
                        <i class="fas fa-trash"></i> Kelola Pertanyaan
                    </button>
                    <button class="btn btn-primary" onclick="showChangePassword()">
                        <i class="fas fa-key"></i> Ubah Password
                    </button>
                </div>

                <div id="adminContent">
                    <div class="admin-panel">
                        <h3><i class="fas fa-chart-bar"></i> Statistik</h3>
                        <p>Total Pertanyaan: {{ total_questions }}</p>
                        <p>Pertanyaan Pending: {{ pending_count }}</p>
                        <p>Status: Admin Mode Aktif</p>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <div id="quizModal" class="modal">
        <div class="modal-content">
            <div id="quizContent">
                </div>
        </div>
    </div>

    <div id="adminLoginModal" class="modal">
        <div class="modal-content">
            <h3 style="color: white; text-align: center; margin-bottom: 20px;">
                <i class="fas fa-lock"></i> Login Admin
            </h3>
            <form id="adminLoginForm">
                <div class="form-group">
                    <label>Password Admin:</label>
                    <input type="password" class="form-control" id="adminPassword" placeholder="Masukkan password..." required>
                </div>
                <div style="text-align: center;">
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </button>
                    <button type="button" class="btn btn-danger" onclick="closeModal('adminLoginModal')">
                        <i class="fas fa-times"></i> Batal
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let currentQuestion = 0;
        let questions = [];
        let score = 0;
        let startTime = 0;
        let timerInterval;

        // Tab management
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });

            document.getElementById(tabName).classList.add('active');
            // This is a common pattern for event listeners; passing event as an argument
            // and using event.target. For simplicity, we assume the button click triggers this.
            // If called programmatically, `event` might be undefined, so a more robust approach
            // would be to pass the button element or its ID.
            const clickedButton = Array.from(document.querySelectorAll('.nav-tab')).find(button => button.onclick.toString().includes(`showTab('${tabName}')`));
            if (clickedButton) {
                clickedButton.classList.add('active');
            }
        }

        // Question type management
        function updateQuestionType() {
            const type = document.getElementById('questionType').value;
            const choicesContainer = document.getElementById('choicesContainer');

            if (type === 'tf') {
                choicesContainer.innerHTML = `
                    <div class="form-group">
                        <label>Pilihan A:</label>
                        <input type="text" class="form-control" id="choiceA" value="True" readonly>
                    </div>
                    <div class="form-group">
                        <label>Pilihan B:</label>
                        <input type="text" class="form-control" id="choiceB" value="False" readonly>
                    </div>
                `;
            } else {
                choicesContainer.innerHTML = `
                    <div class="form-group">
                        <label>Pilihan A:</label>
                        <input type="text" class="form-control" id="choiceA" placeholder="Pilihan A" required>
                    </div>
                    <div class="form-group">
                        <label>Pilihan B:</label>
                        <input type="text" class="form-control" id="choiceB" placeholder="Pilihan B" required>
                    </div>
                    <div class="form-group">
                        <label>Pilihan C:</label>
                        <input type="text" class="form-control" id="choiceC" placeholder="Pilihan C" required>
                    </div>
                    <div class="form-group">
                        <label>Pilihan D:</label>
                        <input type="text" class="form-control" id="choiceD" placeholder="Pilihan D" required>
                    </div>
                `;
            }
        }

        // Quiz functions
        function startQuiz() {
            fetch('/start-quiz')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        questions = data.questions;
                        currentQuestion = 0;
                        score = 0;
                        startTime = Date.now();
                        showQuestion();
                        document.getElementById('quizModal').style.display = 'block';
                        startTimer();
                    } else {
                        alert(data.message);
                    }
                });
        }

        function showQuestion() {
            if (currentQuestion >= questions.length) {
                showResult();
                return;
            }

            const question = questions[currentQuestion];
            const progressPercent = ((currentQuestion + 1) / questions.length) * 100;

            document.getElementById('quizContent').innerHTML = `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progressPercent}%"></div>
                </div>
                <h3 style="color: white; text-align: center; margin-bottom: 20px;">
                    Pertanyaan ${currentQuestion + 1} dari ${questions.length}
                </h3>
                <div class="quiz-question">${question.question}</div>
                <div class="quiz-choices">
                    ${question.choices.map((choice, index) => `
                        <button class="choice-btn" onclick="selectAnswer('${choice}')">
                            ${String.fromCharCode(65 + index)}. ${choice}
                        </button>
                    `).join('')}
                </div>
                <div style="text-align: center;">
                    <button class="btn btn-danger" onclick="closeModal('quizModal')">
                        <i class="fas fa-times"></i> Keluar
                    </button>
                </div>
            `;
        }

        function selectAnswer(answer) {
            const question = questions[currentQuestion];
            if (answer === question.answer) {
                score++;
            }
            currentQuestion++;
            setTimeout(showQuestion, 500);
        }

        function showResult() {
            clearInterval(timerInterval);
            const totalTime = Math.floor((Date.now() - startTime) / 1000);
            const percentage = questions.length > 0 ? Math.round((score / questions.length) * 100) : 0;

            let message = '';
            let color = '';

            if (percentage >= 80) {
                message = '🎉 Excellent! Anda sangat pintar!';
                color = '#4CAF50';
            } else if (percentage >= 60) {
                message = '👍 Good job! Tidak buruk!';
                color = '#FF9800';
            } else {
                message = '📚 Keep learning! Terus belajar!';
                color = '#F44336';
            }

            document.getElementById('quizContent').innerHTML = `
                <div style="text-align: center;">
                    <h2 style="color: white; margin-bottom: 20px;">
                        <i class="fas fa-trophy"></i> Kuis Selesai!
                    </h2>
                    <div class="score-display">
                        Skor: ${score}/${questions.length}
                    </div>
                    <div style="color: white; font-size: 1.2rem; margin-bottom: 20px;">
                        Persentase: ${percentage}%
                    </div>
                    <div style="color: ${color}; font-size: 1.1rem; margin-bottom: 20px; font-weight: 600;">
                        ${message}
                    </div>
                    <div style="color: rgba(255,255,255,0.8); margin-bottom: 30px;">
                        Waktu: ${totalTime} detik
                    </div>
                    <button class="btn btn-primary" onclick="startQuiz()">
                        <i class="fas fa-redo"></i> Ulangi Kuis
                    </button>
                    <button class="btn btn-success" onclick="closeModal('quizModal')">
                        <i class="fas fa-home"></i> Kembali
                    </button>
                </div>
            `;
        }

        function startTimer() {
            const timerElement = document.getElementById('quizTimer');
            if (timerElement) timerElement.remove(); // Remove existing timer if any

            const newTimerElement = document.createElement('div');
            newTimerElement.className = 'timer';
            newTimerElement.id = 'quizTimer';
            document.body.appendChild(newTimerElement);

            timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                document.getElementById('quizTimer').innerHTML = `
                    <i class="fas fa-clock"></i> ${elapsed}s
                `;
            }, 1000);
        }

        // Admin functions
        function showAdminLogin() {
            document.getElementById('adminLoginModal').style.display = 'block';
        }

        function logout() {
            fetch('/logout', {method: 'POST'})
                .then(() => location.reload());
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
            if (modalId === 'quizModal') {
                clearInterval(timerInterval);
                const timer = document.getElementById('quizTimer');
                if (timer) timer.remove();
            }
        }

        // Form submissions
        document.getElementById('questionForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = {
                question: document.getElementById('questionText').value,
                type: document.getElementById('questionType').value,
                choices: [],
                answer: document.getElementById('correctAnswer').value
            };

            // Get choices based on type
            if (formData.type === 'tf') {
                formData.choices = ['True', 'False'];
            } else {
                formData.choices = [
                    document.getElementById('choiceA').value,
                    document.getElementById('choiceB').value,
                    document.getElementById('choiceC').value,
                    document.getElementById('choiceD').value
                ].filter(choice => choice.trim());
            }

            fetch('/add-question', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    document.getElementById('questionForm').reset();
                    updateQuestionType(); // Reset choices container
                    location.reload(); // Reload page to update question count
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        });

        document.getElementById('adminLoginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const password = document.getElementById('adminPassword').value;
            fetch('/admin-login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: password})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    closeModal('adminLoginModal');
                    location.reload(); // Reload page to show admin panel
                } else {
                    alert('Login gagal: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        });

        function showPendingQuestions() {
            fetch('/admin/pending-questions')
                .then(response => response.json())
                .then(data => {
                    let html = '<h3 style="color: white; text-align: center; margin-bottom: 20px;"><i class="fas fa-clock"></i> Pertanyaan Pending</h3>';
                    if (data.length === 0) {
                        html += '<p style="color: rgba(255,255,255,0.8); text-align: center;">Tidak ada pertanyaan pending.</p>';
                    } else {
                        html += '<div class="question-list">';
                        data.forEach(q => {
                            html += `
                                <div class="question-item">
                                    <p style="color: white; font-weight: 600;">Q: ${q.question}</p>
                                    <p style="color: rgba(255,255,255,0.9);">Choices: ${q.choices.join(', ')}</p>
                                    <p style="color: rgba(255,255,255,0.9);">Answer: ${q.answer}</p>
                                    <div style="margin-top: 10px;">
                                        <button class="btn btn-success" style="padding: 5px 10px; font-size: 0.9rem;" onclick="approveQuestion('${q.question}')">
                                            <i class="fas fa-check"></i> Setujui
                                        </button>
                                        <button class="btn btn-danger" style="padding: 5px 10px; font-size: 0.9rem;" onclick="deletePendingQuestion('${q.question}')">
                                            <i class="fas fa-trash"></i> Hapus
                                        </button>
                                    </div>
                                </div>
                            `;
                        });
                        html += '</div>';
                    }
                    document.getElementById('adminContent').innerHTML = html;
                })
                .catch(error => console.error('Error:', error));
        }

        function approveQuestion(questionText) {
            if (confirm('Anda yakin ingin menyetujui pertanyaan ini?')) {
                fetch('/admin/approve-question', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: questionText})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    showPendingQuestions(); // Refresh the list
                    location.reload(); // Reload main page to update total question count
                })
                .catch(error => console.error('Error:', error));
            }
        }

        function deletePendingQuestion(questionText) {
            if (confirm('Anda yakin ingin menghapus pertanyaan pending ini?')) {
                fetch('/admin/delete-pending-question', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: questionText})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    showPendingQuestions(); // Refresh the list
                })
                .catch(error => console.error('Error:', error));
            }
        }

        function showManageQuestions() {
            fetch('/admin/all-questions')
                .then(response => response.json())
                .then(data => {
                    let html = '<h3 style="color: white; text-align: center; margin-bottom: 20px;"><i class="fas fa-list"></i> Kelola Semua Pertanyaan</h3>';
                    if (data.length === 0) {
                        html += '<p style="color: rgba(255,255,255,0.8); text-align: center;">Tidak ada pertanyaan tersimpan.</p>';
                    } else {
                        html += '<div class="question-list">';
                        data.forEach(q => {
                            html += `
                                <div class="question-item">
                                    <p style="color: white; font-weight: 600;">Q: ${q.question}</p>
                                    <p style="color: rgba(255,255,255,0.9);">Choices: ${q.choices.join(', ')}</p>
                                    <p style="color: rgba(255,255,255,0.9);">Answer: ${q.answer}</p>
                                    <div style="margin-top: 10px;">
                                        <button class="btn btn-danger" style="padding: 5px 10px; font-size: 0.9rem;" onclick="deleteQuestion('${q.question}')">
                                            <i class="fas fa-trash"></i> Hapus
                                        </button>
                                    </div>
                                </div>
                            `;
                        });
                        html += '</div>';
                    }
                    document.getElementById('adminContent').innerHTML = html;
                })
                .catch(error => console.error('Error:', error));
        }

        function deleteQuestion(questionText) {
            if (confirm('Anda yakin ingin menghapus pertanyaan ini secara permanen?')) {
                fetch('/admin/delete-question', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: questionText})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    showManageQuestions(); // Refresh the list
                    location.reload(); // Reload main page to update total question count
                })
                .catch(error => console.error('Error:', error));
            }
        }

        function showChangePassword() {
            let html = `
                <h3 style="color: white; text-align: center; margin-bottom: 20px;">
                    <i class="fas fa-key"></i> Ubah Password Admin
                </h3>
                <form id="changePasswordForm">
                    <div class="form-group">
                        <label>Password Baru:</label>
                        <input type="password" class="form-control" id="newAdminPassword" placeholder="Masukkan password baru..." required>
                    </div>
                    <div class="form-group">
                        <label>Konfirmasi Password Baru:</label>
                        <input type="password" class="form-control" id="confirmAdminPassword" placeholder="Konfirmasi password baru..." required>
                    </div>
                    <div style="text-align: center;">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Simpan Password Baru
                        </button>
                    </div>
                </form>
            `;
            document.getElementById('adminContent').innerHTML = html;

            document.getElementById('changePasswordForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const newPass = document.getElementById('newAdminPassword').value;
                const confirmPass = document.getElementById('confirmAdminPassword').value;

                if (newPass !== confirmPass) {
                    alert('Konfirmasi password tidak cocok!');
                    return;
                }

                fetch('/admin/change-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({new_password: newPass})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        document.getElementById('changePasswordForm').reset();
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    total_questions = len(load_questions())
    pending_count = len(load_pending())
    return render_template_string(HTML_TEMPLATE, total_questions=total_questions, pending_count=pending_count)


@app.route('/add-question', methods=['POST'])
def add_question():
    data = request.get_json()
    question_text = data.get('question')
    choices = data.get('choices')
    answer = data.get('answer')
    q_type = data.get('type')

    if not question_text or not choices or not answer:
        return jsonify({"success": False, "message": "Semua bidang harus diisi."}), 400

    new_question = {
        "question": question_text,
        "choices": choices,
        "answer": answer,
        "type": q_type
    }

    if session.get('admin_mode'):
        save_question(new_question)
        message = "Pertanyaan berhasil ditambahkan ke daftar utama!"
    else:
        save_pending(new_question)
        message = "Pertanyaan Anda telah dikirim untuk ditinjau oleh admin."

    return jsonify({"success": True, "message": message})


@app.route('/start-quiz')
def start_quiz():
    questions = load_questions()
    if not questions:
        return jsonify({"success": False, "message": "Belum ada pertanyaan yang tersedia."})

    # Shuffle questions for a new quiz experience each time
    random.shuffle(questions)

    # Only send necessary data to the client for the quiz
    quiz_questions = []
    for q in questions:
        # Shuffle choices for each question
        shuffled_choices = random.sample(q['choices'], len(q['choices']))
        quiz_questions.append({
            "question": q['question'],
            "choices": shuffled_choices,
            "answer": q['answer']  # The client needs the answer to check
        })

    return jsonify({"success": True, "questions": quiz_questions})


@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    password = data.get('password')
    admin_password = load_admin_password()

    if password == admin_password:
        session['admin_mode'] = True
        return jsonify({"success": True, "message": "Login admin berhasil!"})
    else:
        session['admin_mode'] = False
        return jsonify({"success": False, "message": "Password salah."}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_mode', None)
    return jsonify({"success": True, "message": "Logout berhasil."})


@app.route('/admin/pending-questions')
def get_pending_questions():
    if not session.get('admin_mode'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    return jsonify(load_pending())


@app.route('/admin/approve-question', methods=['POST'])
def approve_question():
    if not session.get('admin_mode'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    question_text = data.get('question')

    pending_questions = load_pending()
    question_to_approve = None
    remaining_pending = []

    for q in pending_questions:
        if q['question'] == question_text:
            question_to_approve = q
        else:
            remaining_pending.append(q)

    if question_to_approve:
        save_question(question_to_approve)  # Add to main questions
        with open(PENDING_FILE, "w") as f:  # Update pending questions
            json.dump(remaining_pending, f, indent=2)
        return jsonify({"success": True, "message": "Pertanyaan disetujui dan ditambahkan!"})
    else:
        return jsonify({"success": False, "message": "Pertanyaan pending tidak ditemukan."}), 404


@app.route('/admin/delete-pending-question', methods=['POST'])
def delete_pending_question():
    if not session.get('admin_mode'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    question_text = data.get('question')

    pending_questions = load_pending()
    updated_pending = [q for q in pending_questions if q['question'] != question_text]

    if len(pending_questions) != len(updated_pending):
        with open(PENDING_FILE, "w") as f:
            json.dump(updated_pending, f, indent=2)
        return jsonify({"success": True, "message": "Pertanyaan pending berhasil dihapus."})
    else:
        return jsonify({"success": False, "message": "Pertanyaan pending tidak ditemukan."}), 404


@app.route('/admin/all-questions')
def get_all_questions():
    if not session.get('admin_mode'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    return jsonify(load_questions())


@app.route('/admin/delete-question', methods=['POST'])
def delete_question():
    if not session.get('admin_mode'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    question_text = data.get('question')

    questions = load_questions()
    updated_questions = [q for q in questions if q['question'] != question_text]

    if len(questions) != len(updated_questions):
        with open(DATA_FILE, "w") as f:
            json.dump(updated_questions, f, indent=2)
        return jsonify({"success": True, "message": "Pertanyaan berhasil dihapus."})
    else:
        return jsonify({"success": False, "message": "Pertanyaan tidak ditemukan."}), 404


@app.route('/admin/change-password', methods=['POST'])
def change_admin_password():
    if not session.get('admin_mode'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password or len(new_password) < 4:  # Simple validation
        return jsonify({"success": False, "message": "Password baru minimal 4 karakter."}), 400

    save_admin_password(new_password)
    return jsonify({"success": True, "message": "Password admin berhasil diubah."})


if __name__ == '__main__':
    app.run(debug=True)