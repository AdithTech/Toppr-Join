import json
from datetime import datetime, timedelta
import pytz, time, webbrowser, pyttsx3
from urllib.parse import urlparse, parse_qs
from discord_bot import send_message
from toppr import Toppr

settings = json.loads(open("settings.json", "r").read())
tpr = Toppr(settings['school_domain'])

if tpr.login(settings["enrollment"], settings["password"]):
    print("Successfully logged in")
else:
    print("Failed to login. Please try again."), quit()


def speak(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()


joined = []
ongoing_class = None
while True:
    data = tpr.lectures()
    if not "data" in data.keys():
        raise ValueError(json.dumps(data, indent=4))
    if len(data["data"]["groups"]) > 0:
        today = data["data"]["groups"][0]["groups"]
        for group in today:
            for _class_ in group["lectures"]:
                if (
                    (_class_["state"] == "live")
                    and (not _class_["id"] in joined)
                    and (not _class_["title"] in settings["ignored_classes"])
                ):
                    parsed_url = urlparse(_class_["streaming_url"])
                    token = parse_qs(parsed_url.query)["token"][0]
                    details = tpr.lecture_detail(
                        code=_class_["live_lecture_id"], auth_token=token
                    )
                    start_time = datetime.strptime(
                        details["start_time"], "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=pytz.timezone("Etc/GMT")) + timedelta(
                        hours=5, minutes=30
                    )
                    end_time = datetime.strptime(
                        details["end_time"], "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=pytz.timezone("Etc/GMT")) + timedelta(
                        hours=5, minutes=30
                    )
                    subject_text = details["title"]
                    date_text = start_time.strftime("%d %b %Y")
                    start_time__text = start_time.strftime("%I:%M %p")
                    end_time__text = end_time.strftime("%I:%M %p")
                    lecturer_text = details["tutor"]["name"]

                    if details["state"]["value"] == "live":
                        # open("data.json", "w").write(json.dumps(details, indent=4))
                        print(
                            f"""
Ongoing class details:
\tSubject: {subject_text}
\tDate: {date_text}
\tTime period: {start_time__text} - {end_time__text}
\tLecturer: {lecturer_text}
\tToppr Link: {_class_["streaming_url"]}
"""
                            # \tZoom link: https://zoom.us/j/{details['streaming_platform']['lc_zoom']['meeting_id']}?pwd={details['streaming_platform']['lc_zoom']['encrypted_password']}
                        )
                        if settings["alertByVoice"]:
                            speak(f"{_class_['title']} started")
                        joined.append(_class_["id"])
                        ongoing_class = True
                        wb_path = f"{settings['browser_path']} %s"
                        # from Greeting import greet
                        # greet(
                        send_message(
                            subject_name=subject_text,
                            date=date_text,
                            start_time=start_time__text,
                            end_time=end_time__text,
                            lecturer_name=lecturer_text,
                            webhook_url=settings["discord_webhook_url"],
                        )
                        webbrowser.get(wb_path).open(
                            _class_["streaming_url"] + "&use_bot=true"
                        )
    # except Exception as e:
    #     print("Network error", e)
    time.sleep(5)
