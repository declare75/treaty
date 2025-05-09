from django.shortcuts import render

def main_view(request):
    room_id = request.GET.get('roomID', '')
    context = {
        'room_id': room_id,
        'user': request.user,
    }
    return render(request, 'videocall/main.html', context)