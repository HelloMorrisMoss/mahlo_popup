"""Check the project planning file's to do sections for lines without fixed"""

path = './project_planning.md'
with open(path, 'r') as plan_file:
    lines = plan_file.readlines()

completed_tags = 'fixed', 'built', 'done', 'complete'

# the last date line
todate = ''

for ln, line in enumerate(lines):
    if 'todo' in line:
        todate = line.replace('\n', '')
    if '*' in line and not any(tag in line for tag in completed_tags):
        oldline = line.replace('\n', '').replace('*', '').strip()  # that is to say, with no newline
        print(f'{todate:10}, {ln:3}, {oldline}')
