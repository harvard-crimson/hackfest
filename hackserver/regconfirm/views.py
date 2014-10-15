from django.shortcuts import render

from hackserver.regconfirm.models import Registrant

def confirm_reg(request):
    email = request.GET.get('email', None)
    secret = request.GET.get('secret', None)

    if not(email and secret):
        return render(request, 'regconfirm/failure.html', {'reason': 1})

    try:
        person = Registrant.objects.get(email=email)
    except Registrant.DoesNotExist:
        return render(request, 'regconfirm/failure.html', {'reason': 2})

    resp = person.confirm(secret)

    if resp:
        return render(request, 'regconfirm/success.html', {'person': person})
    else:
        return render(request, 'regconfirm/failure.html', {'reason': 3, 'person': person})
