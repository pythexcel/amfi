from todo.models import AMC, Scheme, Nav
import datetime
from django.db.models import Max


def health_check():
    # general health check for all cron jobs running and reporting

    # health check for daily nav
    ret = nav_check()

    print("nav health check")
    print(ret)

    pass


def nav_check():
    # first check and update the last nav updated date

    latest_date = Nav.get_latest_nav_date()
    print("latest nav data found ", latest_date)

    count = Nav.count_navs_date(latest_date)
    print("total nav's found on date", count)

    # find if for any scheme nav is not updated for a long time let's say 10days
    days = 10

    date = datetime.date.today() - datetime.timedelta(days=days)

    objects = Nav.objects.order_by(
        "-scheme").annotate(date__max=Max("date")).filter(date__max__lt=date)
    print(objects.query)

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
        "problem_funds": problem_funds,
        "latest_nav_date": latest_date,
        "count_navs_date": count
    }
