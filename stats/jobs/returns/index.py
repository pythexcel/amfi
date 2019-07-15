from todo.models import Index

# logic similar to abs.py see notes there


def abs_return(index_name):

    print("getting for name ", index_name)
    index = Index.objects.get(name=index_name)

    ret = index.since_start()
    print(ret)

    pass
