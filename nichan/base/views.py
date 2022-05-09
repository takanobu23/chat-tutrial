from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room,Topic,Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

# rooms = [
#     {'id':1,'name': 'Lets learn python'},
#     {'id':2,'name': 'Design with me'},
#     {'id':3,'name': 'Fronted developers'},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
    
        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist ')
# django flash message っていうオブジェクトからやってきました。https://docs.djangoproject.com/en/4.0/ref/contrib/messages/


        user = authenticate(request, username=username,password=password)
# ここではおそらくauthenticate内に元からあるやつに、ここで定義した要素を入れてってる感じ？
# それで、userがNoneじゃなかったらdjango.contrib.authに備わっているlogin機能にrequestとuser入れて、homeに返す感じ？
# でもしエラーが出たら、エラーメッセージを出す感じやな
        if user is not None:
            login(request,user)
            return redirect ('home')
        else:
            messages.error(request, 'username or password does not exist')
    context = {'page':page}
    return render(request, 'base/login_register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect ('home')
        else:
            messages.error(request,'An error occured during registration')

    return render(request, 'base/login_register.html',{'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # 検索のやつらしいんだけど、なぜそうなった？’q’がこれから受けるパスのurlみたいなこと言っとったけどわかるのそんだけやねん。-> なんか print でrequest.GETしたらそれっぽいのとってたわ...たぶんそれとって、もし空じゃなかったら下のやつ実行するんかなぁ

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains= q) |
        Q(description__icontains = q)
        )

    # これはfilterメソッドでよく使うやつ。topicはmodels.py から持ってきたやつでその中のnameをicontains つまり部分一致の大文字小文字区別なしで調べるもの。
    # それで上で定義した q を条件に部分一致の検索かけて表示させてる感じ。
    # ちなみにicontainsを抜くとAllの欄が消える。参考はこちら（https://codelab.website/django-queryset-filter/#toc1）
    topics = Topic.objects.all()
    room_count = rooms.count()
    context =  {'rooms':rooms,'topics':topics, 'room_count':room_count}
    return render(request, 'base/home.html',context)


def room(request,pk): 
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    # 子要素を取ってきてるらしい？なんかmodels.py のMessageのやつ。
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('body')
        )
        return redirect('room', pk=room.id)
    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    # これがforms.py の中のRoomFormを持ってきてform として定義、からの room_form.htmlへ
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('your are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        # RoomFormの役割わからなすぎ問題 -> フォーム画面作るのに便利とか？
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('消させないけど？')
        
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})