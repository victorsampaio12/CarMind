from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, request, current_app
from flask_login import login_required, current_user
from models.user_model import db, Garagem, Carro, Comentario  
from werkzeug.utils import secure_filename
from datetime import datetime
import os


garage_bp = Blueprint('garage_bp', __name__)

def allowed_file(filename):
    allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


@garage_bp.route('/menu')
@login_required
def menu():
    garagens = Garagem.query.filter_by(user_id=current_user.id).all()
    
    if not garagens:
        nova_garagem = Garagem(user_id=current_user.id)
        db.session.add(nova_garagem)
        db.session.commit()
        garagens = [nova_garagem]

    print("IDs de garagens do usuário:", [g.id for g in garagens])
    return render_template('menu.html', garagens=garagens)


@garage_bp.route('/adicionar_carro/<int:garagem_id>')
@login_required
def adicionar_carro(garagem_id):
    garagem = Garagem.query.get_or_404(garagem_id)
    if garagem.user_id != current_user.id:
        flash("Acesso negado.", "danger")
        return redirect(url_for('garage_bp.menu'))

    novo_carro = Carro(garagem_id=garagem.id, imagem_filename='image.png')
    db.session.add(novo_carro)
    db.session.commit()
    return redirect(url_for('garage_bp.menu'))


@garage_bp.route('/adicionar_garagem', methods=['POST'])
@login_required
def adicionar_garagem():
    try:
        nova_garagem = Garagem(user_id=current_user.id)
        db.session.add(nova_garagem)
        db.session.flush()  # gera o ID sem commit ainda
        garagem_id = nova_garagem.id
        db.session.commit()
        return jsonify({'id': garagem_id}), 200
    except Exception as e:
        print("Erro ao adicionar garagem:", e)
        return jsonify({'erro': 'Erro ao criar garagem'}), 400


@garage_bp.route('/salvar_comentario', methods=['POST'])
@login_required
def salvar_comentario():
    garagem_id = request.form.get('garagem_id')
    texto = request.form.get('texto')
    garagem = Garagem.query.get_or_404(garagem_id)

    if garagem.user_id != current_user.id:
        return "Acesso negado", 403

    if garagem.comentario:
        garagem.comentario.texto = texto
    else:
        novo_comentario = Comentario(garagem_id=garagem.id, texto=texto)
        db.session.add(novo_comentario)

    db.session.commit()

    # Retornar URL de redirecionamento
    return jsonify({"redirect_url": url_for('garage_bp.menu')})

@garage_bp.route('/excluir_garagem/<int:garagem_id>', methods=['POST'])
@login_required
def excluir_garagem(garagem_id):
    garagem = Garagem.query.get_or_404(garagem_id)

    # Segurança: só o dono pode excluir
    if garagem.user_id != current_user.id:
        flash("Acesso negado.", "danger")
        return redirect(url_for('garage_bp.menu'))

    # Excluir carros e comentário vinculados antes
    for carro in garagem.carros:
        db.session.delete(carro)
    if garagem.comentario:
        db.session.delete(garagem.comentario)

    db.session.delete(garagem)
    db.session.commit()
    return redirect(url_for('garage_bp.menu'))


@garage_bp.route('/upload_carro/<int:carro_id>', methods=['POST'])
@login_required
def upload_carro(carro_id):
    carro = Carro.query.get_or_404(carro_id)
    garagem = Garagem.query.get_or_404(carro.garagem_id)
    if garagem.user_id != current_user.id:
        return jsonify({"error": "Acesso negado"}), 403

    if 'imagem' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    arquivo = request.files['imagem']

    if arquivo.filename == '':
        return jsonify({"error": "Arquivo sem nome"}), 400

    if not allowed_file(arquivo.filename):
        return jsonify({"error": "Formato não permitido"}), 400

    filename = secure_filename(f"{datetime.utcnow().timestamp()}_{arquivo.filename}")
    pasta_upload = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(pasta_upload, exist_ok=True)
    caminho_completo = os.path.join(pasta_upload, filename)
    arquivo.save(caminho_completo)

    carro.imagem_filename = filename  # Atualiza o carro com a nova imagem
    db.session.commit()

    return jsonify({
        "id": carro.id,
        "imagem_url": url_for('static', filename=f'uploads/{filename}')
    })

@garage_bp.route('/api/adicionar_carro/<int:garagem_id>', methods=['POST'])
@login_required
def api_adicionar_carro(garagem_id):
    garagem = Garagem.query.get_or_404(garagem_id)
    if garagem.user_id != current_user.id:
        return jsonify({"error": "Acesso negado"}), 403

    novo_carro = Carro(garagem_id=garagem.id, imagem_filename='image.png')
    db.session.add(novo_carro)
    db.session.commit()

    return jsonify({
        "id": novo_carro.id,
        "imagem_url": url_for('static', filename='imagens/image.png')
    })
