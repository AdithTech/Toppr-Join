from discord_webhooks import DiscordWebhooks

def send_message(subject_name, date, start_time, end_time, lecturer_name, webhook_url):
    WEBHOOK_URL = webhook_url

    webhook = DiscordWebhooks(WEBHOOK_URL)
    # Attaches a footer
    # webhook.set_footer(text='-- Toppr Bot')

    webhook.set_content(title='Lecture started',
                        description=f"Lecture {repr(subject_name)} started. Details: ")

    # Appends a field
    webhook.add_field(name='Subject', value=subject_name)
    webhook.add_field(name='Date', value=date)
    webhook.add_field(name='Start Time', value=start_time)
    webhook.add_field(name='End Time', value=end_time)
    webhook.add_field(name='Lecturer', value=lecturer_name)
    webhook.send()
