# jira-issue-notifier
Issue notification script with audio output and GUI in order to inform about newly created issues/tickets within a Jira-Service-Desk/-Managment.

This is more like a template, as e.g. Customer-Request-Type of Jira-Service Management are currently hardcoded.
This could be changed in future by automatically gaining those Request-Types.

Also, the JQL currently contain a template "<Project-Key>" string.

So, if you really want to use it, try to understand the code ;)

Requirements:
- tkinter
- gTTS
- playsound
