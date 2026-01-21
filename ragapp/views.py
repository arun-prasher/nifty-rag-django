from django.shortcuts import render
from ragapp.services import generate_outlook


def ask_view(request):
    answer = None
    q = ''

    if request.method == 'POST':
        q = (request.POST.get('query') or '').strip()
        if q:
            answer = generate_outlook(q)

    return render(request, 'ragapp/ask.html', {'answer': answer, 'query': q})
