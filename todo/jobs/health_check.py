from todo.models import AMC, Scheme, Nav, Index
import datetime
from django.db.models import Max


def health_check():
    # general health check for all cron jobs running and reporting

    # health check for daily nav
    ret = nav_check()

    print("nav health check")
    print(ret)

    ret = index_check()
    print("index health check")
    print(ret)

    pass


def index_check():
    index_data = Index.get_latest_index_date()
    ret = []
    for index in index_data:
        max_date = getattr(index, "max_date")
        name = getattr(index, "name")
        type_name = getattr(index, "type")
        ret.append({
            "max_date": max_date,
            "name": name,
            "type_name": type_name
        })

    return ret
    pass


def nav_check(nav_type=None):
    # first check and update the last nav updated date

    latest_date = Nav.get_latest_nav_date()
    print("latest nav data found ", latest_date)

    count = Nav.count_navs_date(latest_date)
    print("total nav's found on date", count)

    # find if for any scheme nav is not updated for a long time let's say 10days
    if nav_type == "updated":
        days = 2
        date = datetime.date.today() - datetime.timedelta(days=days)
        print(date)

        # objects = Nav.objects.order_by(
        #     "-scheme").annotate(date__max=Max("date")).filter(date__max__lt=date)
        # print(objects.query)

        objects = Nav.objects.raw("SELECT max(todo_nav.date) as `max_date`, todo_nav.scheme_id, todo_scheme.* from todo_nav join todo_scheme on todo_scheme.id = todo_nav.scheme_id where todo_scheme.fund_active = True and todo_scheme.scheme_category =\"Open Ended Schemes\" GROUP by scheme_id ORDER BY `max_date` ASC")

        updated_funds = []
        for nav in objects:
            max_date = getattr(nav, "max_date")
            if max_date > date:
                updated_funds.append({
                    "fund_name": getattr(nav, "fund_name"),
                    "max_date": getattr(nav, "max_date"),
                    "scheme_id": getattr(nav, "scheme_id"),
                    "scheme_category": getattr(nav, "scheme_category"),
                    "scheme_type": getattr(nav, "scheme_type"),
                    "fund_code": getattr(nav, "fund_code"),
                    "fund_option": getattr(nav, "fund_option"),
                    "fund_type": getattr(nav, "fund_type"),
                })
                # print(getattr(nav, "fund_name"))
                # print(getattr(nav, "max_date"))
                # print(getattr(nav, "scheme_id"))
                # print(getattr(nav, "scheme_category"))
                # print(getattr(nav, "scheme_type"))
                # print(getattr(nav, "fund_code"))
                # print(getattr(nav, "fund_option"))
                # print(getattr(nav, "fund_type"))

            # if max_date < (datetime.date.today() - datetime.timedelta(days=days)):
                # these funds are defuct or merged usually
                # temporary first time only
                # Scheme.objects.filter(pk=getattr(nav, "scheme_id")).update(fund_active=False)
                # Scheme.objects.raw("UPDATE `todo_scheme` SET `fund_active` = '0' WHERE `todo_scheme`.`id` = " + str(getattr(nav, "scheme_id")))

                # for nav in objects:
                #     scheme = nav["scheme"]
                #     date = nav["date__max"]

                #     print(scheme, "xxxx", date)

                # print(objects)
                # print(objects.count())

        return {
            "updated_funds": updated_funds,
            "latest_nav_date": latest_date,
            "count_navs_date": count
        }
    else:
        if nav_type == "un_updated":
            days = 2
            date = datetime.date.today() - datetime.timedelta(days=days)
            print(date)
            objects = Nav.objects.raw("SELECT max(todo_nav.date) as `max_date`, todo_nav.scheme_id, todo_scheme.* from todo_nav join todo_scheme on todo_scheme.id = todo_nav.scheme_id where todo_scheme.fund_active = True and todo_scheme.scheme_category =\"Open Ended Schemes\" GROUP by scheme_id ORDER BY `max_date` ASC")
            problem_funds = []
            for nav in objects:
                max_date = getattr(nav, "max_date")
                if max_date < date:
                    problem_funds.append({
                        "fund_name": getattr(nav, "fund_name"),
                        "max_date": getattr(nav, "max_date"),
                        "scheme_id": getattr(nav, "scheme_id"),
                        "scheme_category": getattr(nav, "scheme_category"),
                        "scheme_type": getattr(nav, "scheme_type"),
                        "fund_code": getattr(nav, "fund_code"),
                        "fund_option": getattr(nav, "fund_option"),
                        "fund_type": getattr(nav, "fund_type"),
                    })
            return {
                "problem_funds": problem_funds,
                "latest_nav_date": latest_date,
                "count_navs_date": count
            }
        else:
            if nav_type == "latest_date":
                objects = Nav.objects.raw("SELECT max(todo_nav.date) as `max_date`, todo_nav.scheme_id, todo_scheme.* from todo_nav join todo_scheme on todo_scheme.id = todo_nav.scheme_id where todo_scheme.fund_active = True and todo_scheme.scheme_category =\"Open Ended Schemes\" GROUP by scheme_id ORDER BY `max_date` ASC")
                funds = []
                for nav in objects:
                    funds.append({
                        "fund_name": getattr(nav, "fund_name"),
                        "last_update_date": getattr(nav, "max_date"),
                        "scheme_id": getattr(nav, "scheme_id"),
                        "scheme_category": getattr(nav, "scheme_category"),
                        "scheme_type": getattr(nav, "scheme_type"),
                        "fund_code": getattr(nav, "fund_code"),
                        "fund_option": getattr(nav, "fund_option"),
                        "fund_type": getattr(nav, "fund_type"),
                    })
            return {
                "funds":funds
            }    
