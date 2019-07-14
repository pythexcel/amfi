from todo.models import Scheme, AMC, Nav


# this will caculate 1yr return of all funds
# problem is nav is daily calculated and 1yr return will change daily
# need to find an effecient way to do this fast accross all schemes
def one_year_abs_return():  
    # the logic to this is we will calculate abs return for all scheme daily annd store it db
    # even if nav is not present for that day it will extrapolate and calculate based on nearest nav
    # and update to db the scheme 1yr return etc 
    # this is the most easist logic for now that always calculate and update to db
    # more effecient way need to be thought of but first need to start with something simple

    scheme = Scheme.objects.all().first()

    print(scheme)

    # ret = scheme.previous_yr_abs_today(extrapolateNav=False)

    ret = scheme.previous_yr_abs_today()

    print(ret)
    # Nav.objects.filter()

    pass

# this is data of yearly return e.g return between 2017-2018 etc
# this doesn't change with time as such unless full year changes


def fixed_year_return():
    pass
