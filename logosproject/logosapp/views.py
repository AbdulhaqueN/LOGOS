from django.shortcuts import render,redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Room,Topic,Message
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from .forms import RoomForm
from django.contrib import messages


# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    username = request.POST.get('username')
    password = request.POST.get('password')
    try:
        user = User.objects.get(username=username)
    except:
        messages.error(request, "User does not exist.")

    user = authenticate(request,username=username,password=password)

    if user is not None:
        login(request,user)
        return redirect('home')
    else:
        messages.error(request, "Username or password incorrect.")
    context = {'page':page}
    return render(request,'logosapp/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = UserCreationForm()
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect ('home')
        else:
            messages.error(request,'An Error has occured')
    else:
            messages.error(request,'An Error has occured')

    return render(request,'logosapp/login_register.html',{'form':form,'page':page})

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
    return render(request,'logosapp/home.html',{'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages})

def room(request,pk):
    room = Room.objects.get(id=pk)
    # Calling all the children of a parent
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect ('room',pk=room.id)
    context={'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'logosapp/room.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render (request,'logosapp/profile.html',context)


def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect ('home')

    context={'form':form}
    return render(request,'logosapp/room_form.html',context)

def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.method == 'POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid:
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request,'logosapp/room_form.html',context)

def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect ('home')
    return render(request,'logosapp/delete.html',{'obj':room})

def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if request.method == 'POST':
        message.delete()
        return redirect ('home')
    return render(request,'logosapp/delete.html',{'obj':message})