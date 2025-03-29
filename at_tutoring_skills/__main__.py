import asyncio
import logging
import os

from at_queue.core.session import ConnectionParameters
from uvicorn import Config
from uvicorn import Server

from at_tutoring_skills.absolute.django_init import django_application
from at_tutoring_skills.absolute.django_init import get_args
from at_tutoring_skills.core.IMskills import ATTutoringIMSkills
from at_tutoring_skills.core.KBskills import ATTutoringKBSkills


def get_skills():
    """Инициализация и возврат навыков (KB и IM)."""
    args = get_args()
    connection_parameters = ConnectionParameters(**args)

    # Создание PID-файла (опционально)
    try:
        if not os.path.exists("/var/run/at_tutoring_skills/"):
            os.makedirs("/var/run/at_tutoring_skills/")

        with open("/var/run/at_tutoring_skills/pidfile.pid", "w") as f:
            f.write(str(os.getpid()))
    except PermissionError:
        pass

    # Инициализация навыков
    kb_skills = ATTutoringKBSkills(connection_parameters=connection_parameters)
    im_skills = ATTutoringIMSkills(connection_parameters=connection_parameters)

    return kb_skills, im_skills, args


async def main_with_django():
    """Основная функция для запуска Django и навыков."""
    kb_skills, im_skills, args = get_skills()
    server_host = args.pop("server_host", "localhost")
    server_port = args.pop("server_port", 8000)

    async def lifespan(app):
        """Пользовательский lifespan для управления жизненным циклом навыков."""
        # Инициализация и регистрация навыков
        logging.basicConfig(level=logging.INFO)

        await kb_skills.initialize()
        await kb_skills.register()

        await im_skills.initialize()
        await im_skills.register()

        loop = asyncio.get_event_loop()
        # Запуск навыков в фоновом режиме
        loop.create_task(kb_skills.start())
        loop.create_task(im_skills.start())

        yield  # Приложение запущено

    # Обертываем Django-приложение с пользовательским lifespan
    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            # Обработка событий lifespan
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    # Запуск lifespan
                    async for _ in lifespan(None):
                        pass
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    # Завершение lifespan
                    await send({"type": "lifespan.shutdown.complete"})
                    break
        else:
            # Обработка HTTP-запросов через Django
            await django_application(scope, receive, send)

    # Конфигурация и запуск сервера Uvicorn
    config = Config(
        app=app,  # Передаем обернутое ASGI-приложение
        host=server_host,
        port=server_port,
        lifespan="on",  # Включаем поддержку lifespan
    )
    server = Server(config=config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main_with_django())
