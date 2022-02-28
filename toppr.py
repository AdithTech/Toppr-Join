from json.decoder import JSONDecodeError
import requests
import sys
import datetime
import threading
import time

class Toppr:
    def __init__(self, domain):
        self.session = requests.Session()
        self.domain = domain

    def login(self, enrollment: int, password):
        r = self.session.post(
            f"https://{self.domain}/schoolApi/api/v1/authentication/ecode-login/",
            data={"ecode": enrollment, "password": password},
            headers={
                "origin": f"https://{self.domain}",
            },
        )
        try:
            r.json()
        except JSONDecodeError:
            print(r.text)
            sys.exit(1)
        if r.json().get("status_code") == 200:
            self.session.cookies.set(
                name="__cf_bm", value=r.cookies["__cf_bm"], domain=self.domain
            ),
            self.session.cookies.set(
                name="admin_sessionid",
                value=r.cookies["admin_sessionid"],
                domain=self.domain,
            ),
            self.jwt_token()
            def get_jwt_token_thread():
                while True:
                    self.jwt_token()
                    time.sleep(1000)
            threading.Thread(target=get_jwt_token_thread, args=()).start()
            return True
        else:
            return False

    def jwt_token(self):
        r = self.session.get(
            f"https://{self.domain}/api/v1/schools/get-jwt-token/",
            headers={
                "origin": f"https://{self.domain}",
            },
        ).json()
        if r["status_code"] == 200:
            self.token = r["data"]["token"]
            return r["data"]["token"]

    def lectures(
        self, start_date: datetime.datetime = None, end_date: datetime.datetime = None
    ):
        if start_date != None:
            assert isinstance(start_date, datetime.datetime)
        if end_date != None:
            assert isinstance(end_date, datetime.datetime)
        if start_date == None:
            start_date = datetime.datetime.now()
        if end_date == None:
            end_date = datetime.datetime.now()

        end_date = end_date.strftime("%Y-%m-%d")
        start_date = start_date.strftime("%Y-%m-%d")

        r = self.session.get(
            f"https://paathshala.toppr.school/api/v1.1/timetable/?group_by=day_of_week_and_start_time&user_type=student&start_date={start_date}&end_date={end_date}&add_student_attendance=true&add_lecture_media=true",
            headers={
                "authorization": f"token {self.token}",
                "view-type": "student",
                "origin": f"https://{self.domain}",
            },
            allow_redirects=True,
        )
        if r.status_code == 502:
            print("502 Error: Bad Gateway")
            return self.lectures()
        return r.json()

    def assignments(
        self,
        pending: bool = True,
        completed: bool = True,
        expired: bool = False,
        max_assignments: int = 5,
    ):
        data = {}
        if pending:
            r = self.session.get(
                f"https://paathshala.toppr.school/api/v1/homeworks/student/?page=1&page_size={max_assignments}&section=pending_live&view_type=student",
                headers={
                    "authorization": f"token {self.token}",
                    "origin": f"https://{self.domain}",
                },
            )
            data.update({"pending": r.json()})
        if expired:
            r = self.session.get(
                f"https://paathshala.toppr.school/api/v1/homeworks/student/?page=1&page_size={max_assignments}&section=pending_expired&view_type=student",
                headers={
                    "authorization": f"token {self.token}",
                    "origin": f"https://{self.domain}",
                },
            )
            data.update({"expired": r.json()})
        if completed:
            r = self.session.get(
                f"https://paathshala.toppr.school/api/v1/homeworks/student/?page=1&page_size={max_assignments}&section=completed&view_type=student",
                headers={
                    "authorization": f"token {self.token}",
                    "origin": f"https://{self.domain}",
                },
            )
            data.update({"completed": r.json()})
        return data

    def lecture_detail(self, code: int, auth_token: str):
        r = self.session.get(
            f"https://toppr-live.toppr.com/live-classes/api/v1/live-classes/lecture/{code}/?fetch_questions=true&type=3&fetch_attachments=true&fetch_source_details=true&add_ws_host=true",
            headers={
                "authorization": f"token {auth_token}",
                "origin": f"https://{self.domain}",
            },
        ).json()
        return r
