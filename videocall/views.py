from django.shortcuts import render

def main_view(request):
    room_id = request.GET.get('roomID', '')
    return render(request, 'videocall/main.html', {'room_id': room_id})