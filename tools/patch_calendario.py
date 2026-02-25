import re

with open('app/templates/main/eventos.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Esconde os dias "sobressalentes" de outros meses via CSS
if ".fc-day-other {" not in content:
    content = content.replace("</style>", "    .fc-day-other { visibility: hidden; }\n</style>")

# 2. Ajusta a configuração inicial do FullCalendar
old_calendar_config = """headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek' },
        buttonText: { today: 'Hoje', month: 'Mês', week: 'Semana' },"""

new_calendar_config = """headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth' },
        buttonText: { today: 'Mês Atual' },
        fixedWeekCount: false,
        showNonCurrentDates: false,"""

content = content.replace(old_calendar_config, new_calendar_config)

with open('app/templates/main/eventos.html', 'w', encoding='utf-8') as f:
    f.write(content)
