from todo.models import Scheme


def find_best_fund(sub_category):
    # sub_category = "Multi Cap Fund"

    funds = Scheme.objects.filter(scheme_sub_type=sub_category)

    """
    how to determind if a fund is better what all factors to consider
    equity fund
    1. absolute return
    2. rolling return and how many times its beat its index
    3. downward protection compared to index
    4. TER expensive ratio
    5. AUM increase or how much is aum. this factor also depends on category of fund e.g multi cap/small cap aum matters but not for large cap
    6. portfolio churn?

    debt fund
    1. mainly returns
    2. type of funds in portfolio depends on fund type e.g liquid fund should have low duration funds, aa+ more funds etc 
    3. bond concentration? 
    4. TER
    """

    fund = Scheme.objects.get(pk=12)

    fund.rolling_yr_today("W",1)

    # for fund in funds:
    #     fund.rolling_yr_today(3)
    #     pass
        

    pass
