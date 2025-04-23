from django.http import JsonResponse
from django.utils.decorators import sync_and_async_middleware

@sync_and_async_middleware
def initialization_check_middleware(get_response):
    async def async_middleware(request):
        # Проверяем наличие scope и инициализированных навыков
        if not hasattr(request, 'scope') or not request.scope.get("kb_skills") or not request.scope.get("im_skills"):
            response = JsonResponse(
                {"detail": "Service Unavailable"}, 
                status=503
            )
            # Для асинхронного режима нужно создать корректный асинхронный ответ
            async def streaming_content():
                yield response.content
            response.streaming_content = streaming_content()
            return response
        
        return await get_response(request)

    return async_middleware