import asyncio
import os

from at_queue.core.session import ConnectionParameters

from at_tutoring_skills.core.arguments import get_args
from at_tutoring_skills.core.KBskills import ATTutoringKBSkills


async def main():
    connection_parameters = ConnectionParameters(**get_args())

    try:
        if not os.path.exists('/var/run/at_tutoring_skills/'):
            os.makedirs('/var/run/at_tutoring_skills/')

        with open('/var/run/at_tutoring_skills/pidfile.pid', 'w') as f:
            f.write(str(os.getpid()))
    except PermissionError:
        pass

    skills = ATTutoringKBSkills(connection_parameters=connection_parameters)

    await skills.initialize()
    await skills.register()
    await skills.start()


if __name__ == "__main__":
    asyncio.run(main())
