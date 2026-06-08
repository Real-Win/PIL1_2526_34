from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

# 1. Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle_secrete_ifri_mentorlink'

# 2. [span_0](start_span)[span_1](start_span)Configuration de SocketIO pour activer le temps réel[span_0](end_span)[span_1](end_span)
socketio = SocketIO(app, cors_allowed_origins="*")

# 3. [span_2](start_span)[span_3](start_span)Route de base pour vérifier que le serveur web fonctionne[span_2](end_span)[span_3](end_span)
@app.route('/')
def index():
    return render_template("index.html") 

# 4. Événement : Quand un utilisateur envoie un message
@socketio.on('nouveau_message')
def gerer_message(data):
    print("Message reçu : " + str(data['contenu']))
    # broadcast=True permet de renvoyer le message à TOUS les utilisateurs connectés
    emit('diffusion_message', {'pseudo': data['pseudo'], 'msg': data['contenu']}, broadcast=True)

# 5. [span_4](start_span)[span_5](start_span)Démarrage du serveur sur le port 5000[span_4](end_span)[span_5](end_span)
if __name__ == '__main__':
    socketio.run(app, debug=True)