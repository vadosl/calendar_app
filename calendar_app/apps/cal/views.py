import time
import calendar
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.core.context_processors import csrf
from .models import Entry

MNAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def _show_users(request):
    """Return show_users setting; if it does not exist, initialize it."""
    s = request.session
    if not "show_users" in s:
        s["show_users"] = True
    return s["show_users"]

@login_required
def settings(request):
    """Settings screen."""
    s = request.session
    _show_users(request)
    if request.method == "POST":
        s["show_users"] = (True if "show_users" in request.POST else False)
    context = RequestContext(request)
    context_dict = {'show_users': s["show_users"]}
    return render_to_response("cal/settings.html", context_dict, context )


def reminders(request):
    """Return the list of reminders for today and tomorrow."""
    year, month, day = time.localtime()[:3]
    reminders = Entry.objects.filter(date__year=year, date__month=month,
                                   date__day=day, creator=request.user, remind=True)
    tomorrow = datetime.now() + timedelta(days=1)
    year, month, day = tomorrow.timetuple()[:3]
    reminders_tom = Entry.objects.filter(date__year=year, date__month=month,
                                   date__day=day, creator=request.user, remind=True)
    return list(reminders) + list(reminders_tom)


# @login_required
def main(request, year=None):
    """Main listing, years and months; three years per page."""
    # prev / next years
    if year:
        year = int(year)
    else:
        year = time.localtime()[0]

    nowy, nowm = time.localtime()[:2]
    lst = []

    # create a list of months for each year, indicating ones that contain entries and current
    all_entries = Entry.objects.all()
    for y in [year, year+1, year+2]:
        mlst = []
        for n, month in enumerate(MNAMES):
            entry = current = False   # are there entry(s) for this month; current month?
            entries = all_entries.filter(date__year=y, date__month=n+1)
            if not _show_users(request):
                entries = entries.filter(creator=request.user)

            if entries:
                entry = True
            if y == nowy and n+1 == nowm:
                current = True
            mlst.append(dict(n=n+1, name=month, entry=entry, current=current))
        lst.append((y, mlst))

    context = RequestContext(request)
    context_dict = dict(years=lst, year=year, reminders=reminders(request))
    return render_to_response("cal/main.html", context_dict, context)

# @login_required
def month(request, year, month, change=None):
    print "in month function"
    """Listing of days in `month`."""
    year, month = int(year), int(month)

    # apply next / previous change
    if change in ("next", "prev"):
        now, mdelta = date(year, month, 15), timedelta(days=31)
        if change == "next":   mod = mdelta
        elif change == "prev": mod = -mdelta

        year, month = (now+mod).timetuple()[:2]

    # init variables
    cal = calendar.Calendar()
    month_days = cal.itermonthdays(year, month)
    # print("month_day=", list(month_days))
    nyear, nmonth, nday = time.localtime()[:3]
    lst = [[]]
    week = 0

    # make month lists containing list of days for each week
    # each day tuple will contain list of entries and 'current' indicator
    for day in month_days:
        entries = current = False   # are there entries for this day; current day?
        if day:
            entries = Entry.objects.filter(date__year=year, date__month=month, date__day=day)
            if day == nday and year == nyear and month == nmonth:
                current = True

        lst[week].append((day, entries, current))
        if len(lst[week]) == 7:
            lst.append([])
            week += 1

    context = RequestContext(request)
    context_dict = dict(year=year, month=month, month_days=lst, mname=MNAMES[month-1], reminders=reminders(request))
    return render_to_response("cal/month.html", context_dict, context)






#@login_required
def day(request, year, month, day):
    """Entries for the day."""
    EntriesFormset = modelformset_factory(Entry, extra=2, exclude=("creator", "date"),
                                          can_delete=True)

    other_entries = []
    if _show_users(request):
        other_entries = Entry.objects.filter(date__year=year, date__month=month,
                                       date__day=day).exclude(creator=request.user)


    if request.method == 'POST':
        formset = EntriesFormset(request.POST)
        if formset.is_valid():
            # add current user and date to each entry & save
            entries = formset.save(commit=False)
            for entry in entries:
                entry.creator = request.user
                entry.date = date(int(year), int(month), int(day))
                entry.save()
            return HttpResponseRedirect(reverse("cal:month", args=(year, month)))
        else:
            print(formset.errors)

    else:
        # display formset for existing enties and one extra form
        queryset = Entry.objects.filter(date__year=year, date__month=month, date__day=day, creator=request.user)
        formset = EntriesFormset(queryset=queryset)
        # formset = EntriesFormset()

    context = RequestContext(request)
    context_dict = dict(entries=formset, year=year, month=month, day=day,
                        other_entries=other_entries, reminders=reminders(request))
    return render_to_response("cal/day.html", context_dict, context)

