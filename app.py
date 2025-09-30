from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from fpdf import FPDF

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available - AI features disabled")  

app = Flask(__name__)
CORS(app)

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'nauman0504@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

class PortfolioAssistant:
    def __init__(self):
        self.context = self.load_portfolio_data()
        if TRANSFORMERS_AVAILABLE:
            try:
                self.qa_model = pipeline('question-answering')
            except Exception as e:
                print(f"Warning: Could not initialize AI model: {e}")
                self.qa_model = None
        else:
            self.qa_model = None
    
    def load_portfolio_data(self):
        return """
        Nauman is a full-stack developer specializing in Python, JavaScript, and modern web technologies.
        Key skills include Flask, React, Three.js, WebGL, and AI integration.
        Projects include interactive 3D portfolio, AI-powered chatbots, and real-time visualization systems.
        """
    
    def answer_question(self, question):
        if self.qa_model:
            try:
                return self.qa_model(question=question, context=self.context)
            except Exception as e:
                return {"answer": f"AI model error: {str(e)}", "score": 0.0}
        else:
            return {
                "answer": "I'm a Computer Science student at the University of Leicester with expertise in Python, JavaScript, Flask, and web development. I'm currently working on various projects including this portfolio website.",
                "score": 0.8
            }

class ResumeGenerator:
    def __init__(self):
        self.pdf = FPDF()
        
    def generate(self, selected_skills):
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
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

@app.route('/download-resume')
def download_resume():
    try:
        candidate_paths = [
            os.path.join('static', 'Naumanpatel.pdf'),
            os.path.join('static', 'NaumanPatel.pdf'),
            'Naumanpatel.pdf',
            'NaumanPatel.pdf',
            'resume.pdf',
        ]

        existing_resume = next((p for p in candidate_paths if os.path.exists(p)), None)

        if not existing_resume:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Nauman Patel - Resume', 0, 1, 'C')
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Computer Science Student | AI/ML Enthusiast', 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Contact Information', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, 'Email: nauman0504@gmail.com', 0, 1, 'L')
            pdf.cell(0, 5, 'Phone: +44 7823544825', 0, 1, 'L')
            pdf.cell(0, 5, 'LinkedIn: linkedin.com/in/naumanpatel', 0, 1, 'L')
            pdf.cell(0, 5, 'GitHub: github.com/Naumanpatell', 0, 1, 'L')
            pdf.ln(10)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Education', 0, 1, 'L')
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 5, 'University of Leicester - Computer Science', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, 'Current Student', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Technical Skills', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, 'Programming Languages: Python, Java, JavaScript', 0, 1, 'L')
            pdf.cell(0, 5, 'Web Technologies: HTML/CSS, Flask, MySQL', 0, 1, 'L')
            pdf.cell(0, 5, 'Tools: Git/GitHub, VS Code, Data Structures', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Experience', 0, 1, 'L')
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 5, 'Teaching Assistant - University of Leicester', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, 'Sept 2025 - Present', 0, 1, 'L')
            pdf.cell(0, 5, 'Assisted in teaching Computing and Computer Architecture modules.', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.output('resume.pdf', 'F')
            existing_resume = 'resume.pdf'
        
        return send_file(
            existing_resume,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='NaumanPatel.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    if not EMAIL_PASSWORD:
        print("Warning: EMAIL_PASSWORD not set")
    

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)