import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def connexion_bdd():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mentorlink_bd",
            user="postgres",
            password= "    ",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

def inscrire_etudiant(nom, prenom, email, telephone, filiere, role, mot_de_passe):
    conn = connexion_bdd()
    if conn is None:
        return False, "Impossible de se connecter à la base de données."
    
    password_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
    
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO users (nom, prenom, email, telephone, filiere, role, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (nom, prenom, email, telephone, filiere, role, password_hash))
            conn.commit()
            return True, "Inscription réussie !"
            
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "Sécurité : Cet email ou ce numéro de téléphone est déjà utilisé."
    except Exception as e:
        conn.rollback()
        return False, f"Une erreur est survenue : {e}"
    finally:
        conn.close()

def verifier_connexion(email, mot_de_passe_saisi):
    conn = connexion_bdd()
    if conn is None:
        return None, "Erreur de connexion."
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s;"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            
            if user:
                if bcrypt.check_password_hash(user['password_hash'], mot_de_passe_saisi):
                    return user, "Connexion réussie !"
                else:
                    return None, "Mot de passe incorrect."
            else:
                return None, "Aucun utilisateur trouvé avec cet email."
    except Exception as e:
        return None, f"Erreur : {e}"
    finally:
        conn.close()