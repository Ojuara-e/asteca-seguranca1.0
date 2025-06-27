from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.user import db, User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

# Dados de teste para demonstração
TEST_USERS = {
    'teste@astecaseguranca.com.br': {
        'password': 'asteca2025',
        'name': 'Aluno Teste',
        'team': 'Pintores Pro',
        'level': 3,
        'points': 250,
        'completed_courses': ['nr35'],
        'badges': ['safety_expert', 'team_player', 'perfect_attendance']
    }
}

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    # Verificar usuário de teste
    if email in TEST_USERS:
        if TEST_USERS[email]['password'] == password:
            # Criar token JWT
            token = jwt.encode({
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, 'secret_key', algorithm='HS256')
            
            user_data = TEST_USERS[email].copy()
            user_data['email'] = email
            del user_data['password']
            
            return jsonify({
                'success': True,
                'token': token,
                'user': user_data,
                'message': 'Login realizado com sucesso!'
            }), 200
    
    return jsonify({'error': 'Email ou senha incorretos'}), 401

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verificar se o token JWT é válido"""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Token é obrigatório'}), 400
    
    try:
        payload = jwt.decode(data['token'], 'secret_key', algorithms=['HS256'])
        email = payload['email']
        
        if email in TEST_USERS:
            user_data = TEST_USERS[email].copy()
            user_data['email'] = email
            del user_data['password']
            
            return jsonify({
                'valid': True,
                'user': user_data
            }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    
    return jsonify({'error': 'Usuário não encontrado'}), 404

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint para logout"""
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Obter perfil do usuário logado"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token de autorização necessário'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        email = payload['email']
        
        if email in TEST_USERS:
            user_data = TEST_USERS[email].copy()
            user_data['email'] = email
            del user_data['password']
            
            return jsonify({
                'success': True,
                'user': user_data
            }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    
    return jsonify({'error': 'Usuário não encontrado'}), 404

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novos usuários (demo)"""
    data = request.get_json()
    
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if not data or field not in data:
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    email = data['email'].lower().strip()
    
    if email in TEST_USERS:
        return jsonify({'error': 'Email já cadastrado'}), 409
    
    # Simular registro (em produção, salvaria no banco de dados)
    return jsonify({
        'success': True,
        'message': 'Para se registrar, entre em contato com a Vanessa pelo WhatsApp: (47) 99695-0869'
    }), 200

