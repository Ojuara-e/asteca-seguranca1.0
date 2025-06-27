from flask import Blueprint, request, jsonify
import jwt
import datetime

courses_bp = Blueprint('courses', __name__)

# Dados dos cursos disponíveis
COURSES_DATA = {
    'nr35': {
        'id': 'nr35',
        'title': 'NR-35 - Trabalho em Altura',
        'description': 'Treinamento completo para trabalhos acima de 2 metros. Inclui teoria, prática e certificação válida por 2 anos.',
        'price': 180.00,
        'duration': '16 horas',
        'modules': [
            'Introdução à NR-35',
            'Equipamentos de Proteção Individual',
            'Sistemas de Ancoragem',
            'Técnicas de Resgate',
            'Prática Supervisionada',
            'Avaliação Final'
        ],
        'points_reward': 50
    },
    'nr10': {
        'id': 'nr10',
        'title': 'NR-10 - Segurança em Eletricidade',
        'description': 'Capacitação obrigatória para trabalhos com eletricidade. Ministrado por profissional bombeiro experiente.',
        'price': 220.00,
        'duration': '40 horas',
        'modules': [
            'Fundamentos de Eletricidade',
            'Riscos Elétricos',
            'Medidas de Proteção',
            'Equipamentos de Segurança',
            'Primeiros Socorros',
            'Prática de Campo'
        ],
        'points_reward': 60
    },
    'nr18': {
        'id': 'nr18',
        'title': 'NR-18 - Construção Civil',
        'description': 'Segurança específica para canteiros de obras. Ideal para pedreiros, pintores e operadores de máquinas.',
        'price': 160.00,
        'duration': '20 horas',
        'modules': [
            'Segurança em Canteiros',
            'Proteção contra Quedas',
            'Máquinas e Equipamentos',
            'Sinalização de Segurança',
            'Ordem e Limpeza',
            'Avaliação Prática'
        ],
        'points_reward': 40
    },
    'primeiros-socorros': {
        'id': 'primeiros-socorros',
        'title': 'Primeiros Socorros',
        'description': 'Aprenda a salvar vidas no ambiente de trabalho. Curso prático com simulações reais.',
        'price': 120.00,
        'duration': '12 horas',
        'modules': [
            'Avaliação da Vítima',
            'Reanimação Cardiopulmonar',
            'Controle de Hemorragias',
            'Fraturas e Luxações',
            'Queimaduras',
            'Simulações Práticas'
        ],
        'points_reward': 30
    },
    'cipa': {
        'id': 'cipa',
        'title': 'CIPA - Comissão Interna',
        'description': 'Formação completa para membros da CIPA. Desenvolva habilidades de liderança em segurança.',
        'price': 280.00,
        'duration': '20 horas',
        'modules': [
            'Legislação de Segurança',
            'Análise de Riscos',
            'Investigação de Acidentes',
            'Comunicação Efetiva',
            'Liderança em Segurança',
            'Projeto Final'
        ],
        'points_reward': 70
    },
    'empilhadeira': {
        'id': 'empilhadeira',
        'title': 'Operador de Empilhadeira',
        'description': 'Habilitação completa para operação segura de empilhadeiras. Teoria + prática + certificação.',
        'price': 350.00,
        'duration': '40 horas',
        'modules': [
            'Tipos de Empilhadeiras',
            'Inspeção Diária',
            'Técnicas de Operação',
            'Segurança Operacional',
            'Manutenção Básica',
            'Prova Prática'
        ],
        'points_reward': 80
    }
}

# Dados de ranking das equipes
TEAM_RANKING = [
    {'name': 'Equipe Construção A', 'members': 5, 'points': 1250, 'position': 1},
    {'name': 'Pintores Pro', 'members': 4, 'points': 980, 'position': 2},
    {'name': 'Equipe Operadores', 'members': 6, 'points': 750, 'position': 3},
    {'name': 'Soldadores Unidos', 'members': 3, 'points': 620, 'position': 4},
    {'name': 'Eletricistas Pro', 'members': 4, 'points': 580, 'position': 5}
]

# Dados de ranking individual
INDIVIDUAL_RANKING = [
    {'name': 'João Silva', 'team': 'Equipe Construção A', 'points': 320, 'position': 1},
    {'name': 'Aluno Teste', 'team': 'Pintores Pro', 'points': 250, 'position': 2},
    {'name': 'Maria Santos', 'team': 'Equipe Operadores', 'points': 180, 'position': 3},
    {'name': 'Carlos Oliveira', 'team': 'Soldadores Unidos', 'points': 160, 'position': 4},
    {'name': 'Ana Costa', 'team': 'Eletricistas Pro', 'points': 140, 'position': 5}
]

# Badges disponíveis
BADGES_DATA = {
    'safety_expert': {
        'id': 'safety_expert',
        'name': 'Especialista em Segurança',
        'description': 'Concluiu 3 cursos',
        'icon': 'badge-safety-expert.png',
        'points_required': 150
    },
    'team_player': {
        'id': 'team_player',
        'name': 'Colaborador Exemplar',
        'description': 'Ajudou colegas de equipe',
        'icon': 'trophy-team-ranking.png',
        'points_required': 100
    },
    'perfect_attendance': {
        'id': 'perfect_attendance',
        'name': 'Sempre Presente',
        'description': '100% de presença',
        'icon': 'calendar-schedule.png',
        'points_required': 50
    },
    'safety_master': {
        'id': 'safety_master',
        'name': 'Mestre da Segurança',
        'description': 'Concluir todos os cursos',
        'icon': 'badge-safety-expert.png',
        'points_required': 400
    }
}

def verify_token_decorator(f):
    """Decorator para verificar token JWT"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            request.user_email = payload['email']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    """Obter lista de todos os cursos disponíveis"""
    courses_list = []
    for course_id, course_data in COURSES_DATA.items():
        courses_list.append(course_data)
    
    return jsonify({
        'success': True,
        'courses': courses_list
    }), 200

@courses_bp.route('/courses/<course_id>', methods=['GET'])
def get_course_details(course_id):
    """Obter detalhes de um curso específico"""
    if course_id not in COURSES_DATA:
        return jsonify({'error': 'Curso não encontrado'}), 404
    
    return jsonify({
        'success': True,
        'course': COURSES_DATA[course_id]
    }), 200

@courses_bp.route('/user-progress', methods=['GET'])
@verify_token_decorator
def get_user_progress():
    """Obter progresso do usuário logado"""
    # Dados simulados de progresso
    user_progress = {
        'completed_courses': ['nr35'],
        'in_progress_courses': [
            {
                'course_id': 'nr10',
                'progress': 65,
                'current_module': 4,
                'total_modules': 6
            }
        ],
        'available_courses': ['nr18', 'primeiros-socorros', 'cipa', 'empilhadeira'],
        'total_points': 250,
        'level': 3,
        'badges': ['safety_expert', 'team_player', 'perfect_attendance'],
        'team': 'Pintores Pro',
        'team_ranking': 2
    }
    
    return jsonify({
        'success': True,
        'progress': user_progress
    }), 200

@courses_bp.route('/ranking/teams', methods=['GET'])
def get_team_ranking():
    """Obter ranking das equipes"""
    return jsonify({
        'success': True,
        'ranking': TEAM_RANKING
    }), 200

@courses_bp.route('/ranking/individual', methods=['GET'])
def get_individual_ranking():
    """Obter ranking individual"""
    return jsonify({
        'success': True,
        'ranking': INDIVIDUAL_RANKING
    }), 200

@courses_bp.route('/badges', methods=['GET'])
def get_badges():
    """Obter lista de badges disponíveis"""
    badges_list = []
    for badge_id, badge_data in BADGES_DATA.items():
        badges_list.append(badge_data)
    
    return jsonify({
        'success': True,
        'badges': badges_list
    }), 200

@courses_bp.route('/user-badges', methods=['GET'])
@verify_token_decorator
def get_user_badges():
    """Obter badges do usuário logado"""
    user_badges = ['safety_expert', 'team_player', 'perfect_attendance']
    
    badges_details = []
    for badge_id in user_badges:
        if badge_id in BADGES_DATA:
            badges_details.append(BADGES_DATA[badge_id])
    
    return jsonify({
        'success': True,
        'user_badges': badges_details,
        'available_badges': [badge for badge_id, badge in BADGES_DATA.items() if badge_id not in user_badges]
    }), 200

@courses_bp.route('/enroll/<course_id>', methods=['POST'])
@verify_token_decorator
def enroll_course(course_id):
    """Inscrever usuário em um curso"""
    if course_id not in COURSES_DATA:
        return jsonify({'error': 'Curso não encontrado'}), 404
    
    # Simular inscrição
    return jsonify({
        'success': True,
        'message': f'Inscrição no curso {COURSES_DATA[course_id]["title"]} realizada com sucesso!',
        'course': COURSES_DATA[course_id]
    }), 200

@courses_bp.route('/complete-module', methods=['POST'])
@verify_token_decorator
def complete_module():
    """Marcar módulo como concluído"""
    data = request.get_json()
    
    if not data or 'course_id' not in data or 'module_id' not in data:
        return jsonify({'error': 'course_id e module_id são obrigatórios'}), 400
    
    course_id = data['course_id']
    module_id = data['module_id']
    
    if course_id not in COURSES_DATA:
        return jsonify({'error': 'Curso não encontrado'}), 404
    
    # Simular conclusão de módulo e ganho de pontos
    points_earned = 10
    
    return jsonify({
        'success': True,
        'message': f'Módulo concluído! Você ganhou {points_earned} pontos.',
        'points_earned': points_earned,
        'new_total_points': 260  # Simulado
    }), 200

