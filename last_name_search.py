def last_name_search(last_name: str):
    search = lambda x: last_name.endswith(x)
    if search("ов") or search("ин") or search("ын"):
        return last_name + "а"
    elif search("ова") or search("ина") or search("ына") or search("ая"):
        return last_name[:-1] + "ой"
    elif search("ий"):
        return last_name[:-2] + "ого"
    else:
        return last_name