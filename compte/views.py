import string
import secrets
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import firebase_admin
from firebase_admin import auth, firestore

from compte.models import AppUser


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)  # Session expire when browser is closed
            return redirect('team_home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    
    return render(request, 'login.html')


def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

@login_required
def signup(request):
    if  request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour créer un compte.")
        return redirect('team_home')

    if request.method == 'POST':
        first_name = request.POST.get('nom')
        email = request.POST.get('email')
        username = request.POST.get('username')
        
        # Générer un mot de passe aléatoire avec chiffres, lettres et caractères spéciaux
        password = generate_password(length=8)

        # Créer un nouvel utilisateur dans Django
        user = AppUser.objects.create_user(first_name=first_name, email=email, username=username, password=password)
        
        try:
            # Créer un nouvel utilisateur Firebase
            user_record = auth.create_user(
                email=email,
                email_verified=False,
                password=password,
                display_name=first_name,
                disabled=False
            )
            
            # Ajouter des informations supplémentaires dans la base de données utilisateur Firebase
            auth.update_user(
                user_record.uid,
                display_name=first_name,
                email=email
            )

            # Ajouter des informations sur l'utilisateur dans Firestore
            db = firestore.client()
            user_ref = db.collection('user').document(user_record.uid)
            user_ref.set({
                'display_name': first_name,
                'email': email,
                'username': username
            })

            messages.success(request, f"Le compte de {first_name} a été créé avec succès. Username : {username} | Mot de passe : {password}")
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de la création de l'utilisateur Firebase : {e}")
            user.delete()  # Supprimer l'utilisateur Django si la création de l'utilisateur Firebase échoue

        # Rediriger vers la page 'membres'
        return redirect('membres')
    
    return render(request, 'signup.html')
    

def logout_user(request):
    logout(request)
    return redirect('login')
