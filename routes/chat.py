from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.message import Message
from models.user import User
from utils.helpers import login_required

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route('/')
@login_required
def inbox():
    partners = Message.list_partners(session['user_id'])
    return render_template('chat.html', partners=partners, messages=None, active=None)


@chat_bp.route('/<int:recipient_id>')
@login_required
def conversation(recipient_id):
    if recipient_id == session['user_id']:
        flash('Select a different student to chat with.', 'warning')
        return redirect(url_for('chat.inbox'))

    recipient = User.find_by_id(recipient_id)
    if not recipient:
        flash('Student not found.', 'warning')
        return redirect(url_for('chat.inbox'))

    partners = Message.list_partners(session['user_id'])
    messages = Message.list_conversation(session['user_id'], recipient_id)
    return render_template('chat.html', partners=partners, messages=messages, active=recipient)


@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    recipient_id = int(request.form.get('recipient_id', 0))
    content = request.form.get('content', '').strip()

    if recipient_id == session['user_id'] or not content:
        flash('Please choose someone to message and add text before sending.', 'warning')
        return redirect(request.referrer or url_for('chat.inbox'))

    Message.send(session['user_id'], recipient_id, content)
    return redirect(url_for('chat.conversation', recipient_id=recipient_id))
