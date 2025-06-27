from flask import Blueprint, request, jsonify
import jwt
import datetime

scheduling_bp = Blueprint('scheduling', __name__)

# Horários disponíveis para agendamento
AVAILABLE_TIMES = {
    'weekdays': ['08:00', '09:00', '10:00', '14:00', '15:00', '16:00', '17:00'],
    'saturday': ['08:00', '09:00', '10:00', '11:00']
}

# Agendamentos simulados (em produção seria no banco de dados)
SCHEDULED_EXAMS = [
    {
        'id': 1,
        'user_email': 'teste@astecaseguranca.com.br',
        'course_id': 'nr35',
        'course_name': 'NR-35 - Trabalho em Altura',
        'date': '2025-02-15',
        'time': '14:00',
        'status': 'confirmed',
        'notes': '',
        'created_at': '2025-01-15T10:30:00'
    }
]

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

@scheduling_bp.route('/available-times', methods=['GET'])
def get_available_times():
    """Obter horários disponíveis para agendamento"""
    date_param = request.args.get('date')
    
    if not date_param:
        return jsonify({'error': 'Parâmetro date é obrigatório (formato: YYYY-MM-DD)'}), 400
    
    try:
        selected_date = datetime.datetime.strptime(date_param, '%Y-%m-%d')
        weekday = selected_date.weekday()  # 0 = Monday, 6 = Sunday
        
        # Verificar se é dia útil ou sábado
        if weekday < 5:  # Segunda a sexta
            available_times = AVAILABLE_TIMES['weekdays']
        elif weekday == 5:  # Sábado
            available_times = AVAILABLE_TIMES['saturday']
        else:  # Domingo
            return jsonify({
                'success': True,
                'available_times': [],
                'message': 'Não atendemos aos domingos'
            }), 200
        
        # Filtrar horários já agendados para esta data
        scheduled_times = [
            exam['time'] for exam in SCHEDULED_EXAMS 
            if exam['date'] == date_param and exam['status'] != 'cancelled'
        ]
        
        available_times = [time for time in available_times if time not in scheduled_times]
        
        return jsonify({
            'success': True,
            'date': date_param,
            'available_times': available_times,
            'business_hours': {
                'weekdays': 'Segunda a Sexta: 8h às 18h',
                'saturday': 'Sábado: 8h às 12h',
                'sunday': 'Domingo: Fechado'
            }
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

@scheduling_bp.route('/schedule-exam', methods=['POST'])
@verify_token_decorator
def schedule_exam():
    """Agendar uma prova prática"""
    data = request.get_json()
    
    required_fields = ['course_id', 'date', 'time']
    for field in required_fields:
        if not data or field not in data:
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    course_id = data['course_id']
    exam_date = data['date']
    exam_time = data['time']
    notes = data.get('notes', '')
    
    # Validar data
    try:
        selected_date = datetime.datetime.strptime(exam_date, '%Y-%m-%d')
        if selected_date.date() <= datetime.date.today():
            return jsonify({'error': 'A data deve ser futura'}), 400
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Verificar se o horário está disponível
    weekday = selected_date.weekday()
    if weekday < 5:  # Segunda a sexta
        valid_times = AVAILABLE_TIMES['weekdays']
    elif weekday == 5:  # Sábado
        valid_times = AVAILABLE_TIMES['saturday']
    else:  # Domingo
        return jsonify({'error': 'Não atendemos aos domingos'}), 400
    
    if exam_time not in valid_times:
        return jsonify({'error': 'Horário não disponível'}), 400
    
    # Verificar se já existe agendamento para este horário
    existing_exam = next((
        exam for exam in SCHEDULED_EXAMS 
        if exam['date'] == exam_date and exam['time'] == exam_time and exam['status'] != 'cancelled'
    ), None)
    
    if existing_exam:
        return jsonify({'error': 'Horário já ocupado'}), 409
    
    # Mapear nomes dos cursos
    course_names = {
        'nr35': 'NR-35 - Trabalho em Altura',
        'nr10': 'NR-10 - Segurança em Eletricidade',
        'nr18': 'NR-18 - Construção Civil',
        'primeiros-socorros': 'Primeiros Socorros',
        'cipa': 'CIPA - Comissão Interna',
        'empilhadeira': 'Operador de Empilhadeira'
    }
    
    course_name = course_names.get(course_id, course_id)
    
    # Criar novo agendamento
    new_exam = {
        'id': len(SCHEDULED_EXAMS) + 1,
        'user_email': request.user_email,
        'course_id': course_id,
        'course_name': course_name,
        'date': exam_date,
        'time': exam_time,
        'status': 'pending',  # pending, confirmed, completed, cancelled
        'notes': notes,
        'created_at': datetime.datetime.now().isoformat()
    }
    
    SCHEDULED_EXAMS.append(new_exam)
    
    return jsonify({
        'success': True,
        'message': 'Prova agendada com sucesso! Você receberá uma confirmação por WhatsApp.',
        'exam': new_exam,
        'whatsapp_message': f'Olá! Sua prova de {course_name} foi agendada para {exam_date} às {exam_time}. Confirmaremos em breve!'
    }), 201

@scheduling_bp.route('/my-exams', methods=['GET'])
@verify_token_decorator
def get_my_exams():
    """Obter agendamentos do usuário logado"""
    user_exams = [
        exam for exam in SCHEDULED_EXAMS 
        if exam['user_email'] == request.user_email
    ]
    
    # Ordenar por data
    user_exams.sort(key=lambda x: (x['date'], x['time']))
    
    return jsonify({
        'success': True,
        'exams': user_exams
    }), 200

@scheduling_bp.route('/reschedule-exam/<int:exam_id>', methods=['PUT'])
@verify_token_decorator
def reschedule_exam(exam_id):
    """Reagendar uma prova"""
    data = request.get_json()
    
    required_fields = ['date', 'time']
    for field in required_fields:
        if not data or field not in data:
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    # Encontrar o agendamento
    exam = next((exam for exam in SCHEDULED_EXAMS if exam['id'] == exam_id), None)
    
    if not exam:
        return jsonify({'error': 'Agendamento não encontrado'}), 404
    
    if exam['user_email'] != request.user_email:
        return jsonify({'error': 'Não autorizado'}), 403
    
    new_date = data['date']
    new_time = data['time']
    
    # Validar nova data
    try:
        selected_date = datetime.datetime.strptime(new_date, '%Y-%m-%d')
        if selected_date.date() <= datetime.date.today():
            return jsonify({'error': 'A data deve ser futura'}), 400
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Verificar disponibilidade do novo horário
    weekday = selected_date.weekday()
    if weekday < 5:
        valid_times = AVAILABLE_TIMES['weekdays']
    elif weekday == 5:
        valid_times = AVAILABLE_TIMES['saturday']
    else:
        return jsonify({'error': 'Não atendemos aos domingos'}), 400
    
    if new_time not in valid_times:
        return jsonify({'error': 'Horário não disponível'}), 400
    
    # Verificar conflitos (exceto o próprio agendamento)
    existing_exam = next((
        e for e in SCHEDULED_EXAMS 
        if e['date'] == new_date and e['time'] == new_time 
        and e['status'] != 'cancelled' and e['id'] != exam_id
    ), None)
    
    if existing_exam:
        return jsonify({'error': 'Horário já ocupado'}), 409
    
    # Atualizar agendamento
    exam['date'] = new_date
    exam['time'] = new_time
    exam['status'] = 'pending'  # Volta para pendente após reagendamento
    
    return jsonify({
        'success': True,
        'message': 'Prova reagendada com sucesso!',
        'exam': exam
    }), 200

@scheduling_bp.route('/cancel-exam/<int:exam_id>', methods=['DELETE'])
@verify_token_decorator
def cancel_exam(exam_id):
    """Cancelar uma prova agendada"""
    exam = next((exam for exam in SCHEDULED_EXAMS if exam['id'] == exam_id), None)
    
    if not exam:
        return jsonify({'error': 'Agendamento não encontrado'}), 404
    
    if exam['user_email'] != request.user_email:
        return jsonify({'error': 'Não autorizado'}), 403
    
    exam['status'] = 'cancelled'
    
    return jsonify({
        'success': True,
        'message': 'Prova cancelada com sucesso!'
    }), 200

@scheduling_bp.route('/business-hours', methods=['GET'])
def get_business_hours():
    """Obter horários de funcionamento"""
    return jsonify({
        'success': True,
        'business_hours': {
            'weekdays': {
                'days': 'Segunda a Sexta',
                'hours': '8h às 18h',
                'available_times': AVAILABLE_TIMES['weekdays']
            },
            'saturday': {
                'days': 'Sábado',
                'hours': '8h às 12h',
                'available_times': AVAILABLE_TIMES['saturday']
            },
            'sunday': {
                'days': 'Domingo',
                'hours': 'Fechado',
                'available_times': []
            }
        },
        'contact': {
            'whatsapp': '(47) 99695-0869',
            'email': 'vanessa.asteca@gmail.com',
            'address': 'Rua Carlos Eggert, 433, Vila Lalau, Jaraguá do Sul/SC'
        }
    }), 200

