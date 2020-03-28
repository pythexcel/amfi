from todo.logs import getDataSource
from todo.logs import serialize_doc
from todo.models import AMC,Nav,Scheme,NavSerializer
import datetime


def mf_last(process_name):
    db = getDataSource()
    ret = db.logs.find({"process_name": process_name}).sort('time',-1).limit(1)
    ret = [serialize_doc(doc) for doc in ret]
    for data in ret:
        return data['time']




def nav_details(nav_type=None):    
    latest_date = Nav.get_latest_nav_date()
    print("latest nav data found ", latest_date)

    if nav_type == "updated":
        days = 2
        date = datetime.date.today() - datetime.timedelta(days=days)
        print(date)

        objects = Nav.objects.raw("SELECT max(todo_nav.date) as `max_date`, todo_nav.scheme_id, todo_scheme.* from todo_nav join todo_scheme on todo_scheme.id = todo_nav.scheme_id where todo_scheme.fund_active = True and todo_scheme.scheme_category =\"Open Ended Schemes\" GROUP by scheme_id ORDER BY `max_date` ASC")

        updated_funds = []
        for nav in objects:
            max_date = getattr(nav, "max_date")
            if max_date > date:
                updated_funds.append({
                    "id" : getattr(nav, "scheme_id"),
                    "fund_name": getattr(nav, "fund_name"),
                    "line": getattr(nav, "max_date"),
                    "scheme_id": getattr(nav, "scheme_id"),
                    "scheme_category": getattr(nav, "scheme_category"),
                    "scheme_type": getattr(nav, "scheme_type"),
                    "fund_code": getattr(nav, "fund_code"),
                    "fund_option": getattr(nav, "fund_option"),
                    "fund_type": getattr(nav, "fund_type"),
                })

        return {
            "updated_funds": updated_funds,
            "latest_nav_date": latest_date
        }
    else:
        if nav_type == "un_updated":
            days = 10
            date = datetime.date.today() - datetime.timedelta(days=days)
            print(date)
            objects = Nav.objects.raw("SELECT max(todo_nav.date) as `max_date`, todo_nav.scheme_id, todo_scheme.* from todo_nav join todo_scheme on todo_scheme.id = todo_nav.scheme_id where todo_scheme.fund_active = True and todo_scheme.scheme_category =\"Open Ended Schemes\" GROUP by scheme_id ORDER BY `max_date` ASC")
            problem_funds = []
            for nav in objects:
                max_date = getattr(nav, "max_date")
                if max_date < date:
                    problem_funds.append({
                        "id" : getattr(nav, "scheme_id"),
                        "fund_name": getattr(nav, "fund_name"),
                        "line": getattr(nav, "max_date"),
                        "scheme_id": getattr(nav, "scheme_id"),
                        "scheme_category": getattr(nav, "scheme_category"),
                        "scheme_type": getattr(nav, "scheme_type"),
                        "fund_code": getattr(nav, "fund_code"),
                        "fund_option": getattr(nav, "fund_option"),
                        "fund_type": getattr(nav, "fund_type"),
                    })
            return {
                "problem_funds": problem_funds,
                "latest_nav_date": latest_date
            }