from django.shortcuts import render, redirect


def index(request):
    """
    Pagina principal del usuario cuando esta loqueado
    :param request:
    :return: 
    """
    usuario = request.user
    autenticado = request.user.is_authenticated
    if autenticado:
        return render(request, 'index.html', locals())

    return redirect('autenticacion:iniciar_sesion')


