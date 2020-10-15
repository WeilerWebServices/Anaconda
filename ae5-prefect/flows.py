import prefect
from prefect import Flow, task
from prefect.schedules import IntervalSchedule
from datetime import timedelta, datetime

import time

schedule = IntervalSchedule(
    start_date=datetime.utcnow() + timedelta(seconds=1),
    interval=timedelta(minutes=5),
)

@task
def run():
    logger = prefect.context.get("logger")
    results = []
    for x in range(3):
        results.append(str(x + 1))
        logger.info("Hello Anaconda Enterprise! run {}".format(x + 1))
        time.sleep(3)
    return results

with Flow("Hello Anaconda Enterprise", schedule=schedule) as flow:
    results = run()

flow.register(project_name="Hello Anaconda Enterprise")
