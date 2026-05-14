from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from dotenv import load_dotenv
import re

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medication_monitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicializar banco de dados
db = SQLAlchemy(app)

# Variáveis de ambiente para e-mail
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# ==================== MODELOS DO BANCO DE DADOS ====================

class Medication(db.Model):
    """Modelo para armazenar informações de medicamentos"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(5), nullable=False)  # HH:MM
    dosage = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    interval_hours = db.Column(db.Integer, default=24)
    next_intake = db.Column(db.DateTime, default=datetime.now)
    last_intake = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Converte para dicionário para JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'time': self.time,
            'dosage': self.dosage,
            'email': self.email,
            'interval_hours': self.interval_hours,
            'next_intake': self.next_intake.isoformat() if self.next_intake else None,
            'last_intake': self.last_intake.isoformat() if self.last_intake else None,
            'created_at': self.created_at.isoformat(),
            'active': self.active
        }

class IntakeHistory(db.Model):
    """Modelo para manter histórico de ingestões"""
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    confirmed_at = db.Column(db.DateTime, default=datetime.now)
    next_scheduled = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'medication_id': self.medication_id,
            'confirmed_at': self.confirmed_at.isoformat(),
            'next_scheduled': self.next_scheduled.isoformat() if self.next_scheduled else None
        }

# ==================== FUNÇÕES DE E-MAIL ====================

def send_alert_email(medication):
    """
    Envia e-mail de alerta para o usuário
    """
    if not EMAIL_USER or not EMAIL_PASS:
        logger.error('Credenciais de e-mail não configuradas no arquivo .env')
        return False
    
    try:
        # Calcular próximo horário
        next_time = (datetime.now() + timedelta(hours=medication.interval_hours)).isoformat()
        confirm_link = f"http://localhost:5000/confirm-intake?med={medication.id}"
        
        # Criar mensagem HTML
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 8px;
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .header {{
                        background-color: #00008B;
                        color: white;
                        padding: 20px;
                        border-radius: 8px 8px 0 0;
                        text-align: center;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .info-box {{
                        background-color: #f0f0f0;
                        padding: 15px;
                        border-left: 4px solid #00008B;
                        margin: 15px 0;
                    }}
                    .btn {{
                        display: inline-block;
                        background-color: #00008B;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-top: 20px;
                    }}
                    .btn:hover {{
                        background-color: #000060;
                    }}
                    .footer {{
                        color: #666;
                        font-size: 12px;
                        margin-top: 20px;
                        border-top: 1px solid #ddd;
                        padding-top: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💊 Hora de Tomar seu Medicamento</h1>
                    </div>
                    <div class="content">
                        <p>Olá! É hora de tomar seu medicamento. Aqui estão os detalhes:</p>
                        
                        <div class="info-box">
                            <strong>Medicamento:</strong> {medication.name}<br>
                            <strong>Dosagem:</strong> {medication.dosage}<br>
                            <strong>Horário:</strong> {medication.time}<br>
                            <strong>Próximo agendado:</strong> {medication.interval_hours} horas
                        </div>
                        
                        <p>Após tomar o medicamento, clique no botão abaixo para confirmar a ingestão:</p>
                        
                        <center>
                            <a href="{confirm_link}" class="btn">✓ Confirmar Ingestão</a>
                        </center>
                        
                        <div class="footer">
                            <p>Este é um e-mail automático gerado pelo sistema MediControl. Não responda a este e-mail.</p>
                            <p>Se você não solicitou este e-mail, ignore-o.</p>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Configurar e enviar e-mail
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_USER
        msg['To'] = medication.email
        msg['Subject'] = f'💊 Alerta: Hora de tomar {medication.name}'
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Conectar ao SMTP e enviar
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        
        logger.info(f'E-mail enviado com sucesso para {medication.email} - Medicamento: {medication.name}')
        return True
    
    except smtplib.SMTPAuthenticationError:
        logger.error('Erro de autenticação SMTP. Verifique EMAIL_USER e EMAIL_PASS no arquivo .env')
        logger.error('Para Gmail, use: https://myaccount.google.com/apppasswords')
        return False
    
    except smtplib.SMTPException as e:
        logger.error(f'Erro SMTP ao enviar e-mail: {str(e)}')
        return False
    
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail: {str(e)}')
        return False

# ==================== FUNÇÕES DE AGENDAMENTO ====================

def check_medication_alerts():
    """
    Verifica se há medicamentos que precisam de alerta
    Executada a cada 1 minuto pelo scheduler
    """
    try:
        medications = Medication.query.filter_by(active=True).all()
        current_time = datetime.now().strftime('%H:%M')
        
        for med in medications:
            # Verificar se é hora de tomar o medicamento
            if med.time == current_time:
                # Verificar se já enviou alerta hoje
                if med.last_intake is None or (datetime.now() - med.last_intake).total_seconds() > 3600:
                    send_alert_email(med)
                    logger.info(f'Alerta enviado para medicamento: {med.name}')
    
    except Exception as e:
        logger.error(f'Erro ao verificar alertas: {str(e)}')

# ==================== ROTAS DA APLICAÇÃO ====================

@app.route('/')
def dashboard():
    """Página principal - Dashboard"""
    return render_template('dashboard.html')

@app.route('/register')
def register():
    """Página de cadastro de medicamento"""
    return render_template('register.html')

@app.route('/success')
def success():
    """Página de sucesso"""
    return render_template('success.html')

@app.route('/error')
def error():
    """Página de erro"""
    return render_template('error.html')

# ==================== API REST ====================

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """Retorna lista de todos os medicamentos"""
    try:
        medications = Medication.query.filter_by(active=True).all()
        return jsonify([med.to_dict() for med in medications])
    except Exception as e:
        logger.error(f'Erro ao buscar medicamentos: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/medications', methods=['POST'])
def create_medication():
    """Cria novo medicamento"""
    try:
        data = request.get_json()
        
        # Validar dados
        if not all(key in data for key in ['name', 'time', 'dosage', 'email']):
            return jsonify({'error': 'Campos obrigatórios faltando'}), 400
        
        # Validar formato de hora
        if not re.match(r'^\d{2}:\d{2}$', data['time']):
            return jsonify({'error': 'Formato de hora inválido. Use HH:MM'}), 400
        
        # Validar e-mail
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
            return jsonify({'error': 'E-mail inválido'}), 400
        
        # Criar medicamento
        new_med = Medication(
            name=data['name'],
            time=data['time'],
            dosage=data['dosage'],
            email=data['email'],
            interval_hours=data.get('interval_hours', 24)
        )
        
        # Calcular próximo agendamento
        now = datetime.now()
        med_time = datetime.strptime(data['time'], '%H:%M').time()
        next_intake = datetime.combine(now.date(), med_time)
        
        # Se o horário já passou hoje, agendar para amanhã
        if next_intake <= now:
            next_intake += timedelta(days=1)
        
        new_med.next_intake = next_intake
        
        db.session.add(new_med)
        db.session.commit()
        
        logger.info(f'Medicamento criado: {new_med.name}')
        return jsonify(new_med.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao criar medicamento: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/medications/<int:med_id>', methods=['DELETE'])
def delete_medication(med_id):
    """Remove um medicamento"""
    try:
        med = Medication.query.get(med_id)
        
        if not med:
            return jsonify({'error': 'Medicamento não encontrado'}), 404
        
        # Marcar como inativo em vez de deletar
        med.active = False
        db.session.commit()
        
        logger.info(f'Medicamento removido: {med.name}')
        return jsonify({'message': 'Medicamento removido com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao remover medicamento: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:med_id>', methods=['GET'])
def get_history(med_id):
    """Retorna histórico de ingestões de um medicamento"""
    try:
        history = IntakeHistory.query.filter_by(medication_id=med_id).all()
        return jsonify([item.to_dict() for item in history])
    except Exception as e:
        logger.error(f'Erro ao buscar histórico: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/confirm-intake', methods=['GET'])
def confirm_intake():
    """Confirma a ingestão de um medicamento"""
    try:
        med_id = request.args.get('med')
        
        if not med_id:
            return redirect(url_for('error'))
        
        med = Medication.query.get(int(med_id))
        
        if not med:
            return redirect(url_for('error'))
        
        # Atualizar data da última ingestão
        med.last_intake = datetime.now()
        
        # Agendar próxima ingestão
        med.next_intake = datetime.now() + timedelta(hours=med.interval_hours)
        
        # Registrar no histórico
        history = IntakeHistory(
            medication_id=med.id,
            confirmed_at=datetime.now(),
            next_scheduled=med.next_intake
        )
        
        db.session.add(history)
        db.session.commit()
        
        logger.info(f'Ingestão confirmada: {med.name}')
        return redirect(url_for('success'))
    
    except Exception as e:
        logger.error(f'Erro ao confirmar ingestão: {str(e)}')
        return redirect(url_for('error'))

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        logger.info('Banco de dados inicializado')
    
    # Configurar e iniciar scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_medication_alerts, trigger='interval', minutes=1)
    scheduler.start()
    logger.info('Scheduler iniciado com sucesso')
    
    # Executar aplicação
    app.run(debug=False, host='localhost', port=5000)
