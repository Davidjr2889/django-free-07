
def get_client_ip(request):
    """
    Obtem o ip remoto
    Funciona quando o Django esta atras de um reverse proxy, como o nginx
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
