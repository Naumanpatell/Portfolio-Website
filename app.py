from flask import Flask, request, jsonify, render_template, send_file
from transformers import pipeline
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import re
from fpdf import FPDF
import json

app = Flask(__name__)
CORS(app)

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'nauman0504@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

class PortfolioAssistant:
    def __init__(self):
        self.qa_model = pipeline('question-answering')
        self.context = self.load_portfolio_data()
    
    def load_portfolio_data(self):
        """Load portfolio data for AI context"""
        return """
        Nauman is a full-stack developer specializing in Python, JavaScript, and modern web technologies.
        Key skills include Flask, React, Three.js, WebGL, and AI integration.
        Projects include interactive 3D portfolio, AI-powered chatbots, and real-time visualization systems.
        """
    
    def answer_question(self, question):
        return self.qa_model(question=question, context=self.context)

class ResumeGenerator:
    def __init__(self):
        self.pdf = FPDF()
        
    def generate(self, selected_skills):
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        # Add custom resume content based on selected skills
        self.pdf.cell(0, 10, 'Customized Resume', 0, 1, 'C')
        for skill in selected_skills:
            self.pdf.cell(0, 10, f'• {skill}', 0, 1)
        return self.pdf.output('resume.pdf', 'F')

def send_email(name, email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f"Portfolio Contact: {subject}"
        
        body = f"""
        New contact form submission:
        Name: {name}
        Email: {email}
        Subject: {subject}
        Message: {message}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def validate_input(data, required_fields):
    errors = []
    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"{field.capitalize()} is required")
    return errors

# Initialize AI assistant
portfolio_assistant = PortfolioAssistant()
resume_generator = ResumeGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_assistant():
    try:
        question = request.json.get('question')
        if not question:
            return jsonify({"error": "Question is required"}), 400
            
        answer = portfolio_assistant.answer_question(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        errors = validate_input(data, ['name', 'email', 'subject', 'message'])
        
        if errors:
            return jsonify({
                'success': False,
                'errors': errors
            }), 400
            
        if send_email(data['name'], data['email'], data['subject'], data['message']):
            return jsonify({'success': True})
        return jsonify({'success': False}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    try:
        skills = request.json.get('skills', [])
        if not skills:
            return jsonify({"error": "No skills selected"}), 400
            
        resume_generator.generate(skills)
        return send_file(
            'resume.pdf',
            mimetype='application/pdf',
            as_attachment=True,
            download_name='custom_resume.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/skills-visualization')
def get_skills_data():
    skills_data = {
        "nodes": [
            {"id": "Python", "level": 90},
            {"id": "JavaScript", "level": 85},
            {"id": "React", "level": 80},
            # Add more skills
        ],
        "links": [
            {"source": "Python", "target": "Flask"},
            {"source": "JavaScript", "target": "React"},
            # Add more connections
        ]
    }
    return jsonify(skills_data)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    if not EMAIL_PASSWORD:
        print("Warning: EMAIL_PASSWORD not set")
    app.run(debug=True, host='0.0.0.0', port=5000)