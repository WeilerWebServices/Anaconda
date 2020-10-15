# Bootstrap the Sentry environment
from sentry.utils.runner import configure

# YOU MUST COPY THE SETTINGS FILE TO /root/.sentry/sentry.conf.py
configure()

# Do something crazy
from sentry.models import Team, Project, ProjectKey, User

user = User.objects.get(username="admin")

team = Team()
team.name = 'Sentry'
team.owner = user
team.save()

project = Project()
project.team = team
project.owner = user
project.name = 'Default'
project.save()

key = ProjectKey.objects.filter(project=project)[0]
print '%s' % (key.get_dsn(),)
