from django.shortcuts import render,HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def home(request):
    return render(request,'home/home.html')

def handleSignup(request):
    if request.method == 'POST':
       email= request.POST['email']
       Username= request.POST['Username']
       fname= request.POST['fname']
       lname= request.POST['lname']
       pass1= request.POST['pass1']
       pass2= request.POST['pass2']

       if len(Username)> 10:
           messages.success(request, "Username must be under 10 characters")
           return redirect('home')
       if not  Username.isalnum():
           messages.success(request, "Username should only letters")
           return redirect('home')
       if pass1 != pass2:
           messages.success(request, "Password doesnt match")
           return redirect('home')

       myuser = User.objects.create_user(Username,email,pass1)
       myuser.first_name = fname
       myuser.last_name=lname
       myuser.save()
       messages.success(request,"Your account has been created")
       return redirect('home')


    else:
        return HttpResponse('404- Not Found')



def handleLogin(request):
    if request.method == 'POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername,password=loginpassword)

        if user is not None:
            login(request,user)
            messages.success(request,"Sucessfuly login")
            return redirect('home')
        else:
            messages.error(request, "invalid username and password to login")
            return redirect('home')


            return HttpResponse('handleLogin')

def handleLogout(request):
        logout(request)
        messages.success(request, "Sucessfuly logout")
        return redirect('home')

