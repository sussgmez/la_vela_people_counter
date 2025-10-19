import json
import locale
import pandas as pd
import openpyxl
import calendar
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Sum, Case, When, Q
from django.views.generic import TemplateView
from django.core.handlers.wsgi import WSGIRequest
from .models import File, Report, ReportDetail, Entrance


class HomeView(TemplateView):
    template_name = "people_counter/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entrances"] = Entrance.objects.all().order_by("id")
        context["yesterday"] = datetime.today() - timedelta(1)
        context["year_month"] = (
            f"{datetime.today().year}-{str(datetime.today().month).zfill(2)}"
        )
        return context


class EntranceView(TemplateView):
    template_name = "people_counter/entrance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_range = self.request.GET["range"]

        if self.request.GET["entrance"] == "all":
            date = datetime.strptime(self.request.GET["max-date"], "%Y-%m-%d")
            if date_range == "day":
                labels = json.dumps([f"{x}:00" for x in range(1, 25)])

                enter_data = []
                exit_data = []

                for x in range(0, 24):
                    enter_reportdetails = ReportDetail.objects.filter(
                        report__date=date, report__direction="entran", time=f"{x}:00"
                    ).values_list("quantity", flat=True)
                    enter_data.append(sum(enter_reportdetails))

                    exit_reportdetails = ReportDetail.objects.filter(
                        report__date=date, report__direction="salen", time=f"{x}:00"
                    ).values_list("quantity", flat=True)
                    exit_data.append(sum(exit_reportdetails))

                prev_enter_total = sum(
                    Report.objects.filter(
                        date=date - timedelta(days=1), direction="entran"
                    ).values_list("total", flat=True)
                )
                prev_exit_total = sum(
                    Report.objects.filter(
                        date=date - timedelta(days=1), direction="salen"
                    ).values_list("total", flat=True)
                )

            elif date_range == "week":
                week = [date - timedelta(days=x) for x in range(7)][::-1]
                labels = json.dumps([date.strftime("%d/%m") for date in week])

                enter_data = []
                exit_data = []

                for date in week:
                    enter_data.append(
                        sum(
                            Report.objects.filter(
                                date=date, direction="entran"
                            ).values_list("total", flat=True)
                        )
                    )
                    exit_data.append(
                        sum(
                            Report.objects.filter(
                                date=date, direction="salen"
                            ).values_list("total", flat=True)
                        )
                    )
                prev_enter_total = sum(
                    Report.objects.filter(
                        date__gte=date - timedelta(days=13),
                        date__lte=date - timedelta(days=7),
                        direction="entran",
                    ).values_list("total", flat=True)
                )
                prev_exit_total = sum(
                    Report.objects.filter(
                        date__gte=date - timedelta(days=13),
                        date__lte=date - timedelta(days=7),
                        direction="salen",
                    ).values_list("total", flat=True)
                )

            context["labels"] = labels
            context["enter_data"] = enter_data
            context["exit_data"] = exit_data

            context["enter_total"] = sum(enter_data)
            context["exit_total"] = sum(exit_data)
            context["prev_enter_total"] = prev_enter_total
            context["prev_exit_total"] = prev_exit_total

        else:
            entrance = Entrance.objects.get(id=self.request.GET["entrance"])

            date = datetime.strptime(self.request.GET["max-date"], "%Y-%m-%d")

            enter_total = 0
            exit_total = 0
            prev_enter_total = 0
            prev_exit_total = 0

            exit_report = None

            labels = []
            enter_data = []
            exit_data = []

            if date_range == "day":
                labels = json.dumps([f"{x}:00" for x in range(1, 25)])
                try:
                    enter_report = entrance.reports.get(date=date, direction="entran")
                    exit_report = entrance.reports.get(date=date, direction="salen")
                    enter_reportdetails = list(
                        ReportDetail.objects.filter(report=enter_report).values_list(
                            "quantity", flat=True
                        )
                    )
                    enter_data = enter_reportdetails
                    exit_reportdetails = list(
                        ReportDetail.objects.filter(report=exit_report).values_list(
                            "quantity", flat=True
                        )
                    )
                    exit_data = exit_reportdetails

                    enter_total = enter_report.total
                    exit_total = exit_report.total

                    prev_enter_total = entrance.reports.get(
                        date=date - timedelta(1), direction="entran"
                    ).total
                    prev_exit_total = entrance.reports.get(
                        date=date - timedelta(1), direction="salen"
                    ).total

                except Exception as e:
                    print(e)

            elif date_range == "week":

                week = [date - timedelta(days=x) for x in range(7)][::-1]

                labels = json.dumps([date.strftime("%d/%m") for date in week])

                for date in week:
                    try:
                        enter_data.append(
                            entrance.reports.get(date=date, direction="entran").total
                        )
                        exit_data.append(
                            entrance.reports.get(date=date, direction="salen").total
                        )
                    except:
                        enter_data.append(0)
                        exit_data.append(0)

                prev_enter_total = sum(
                    Report.objects.filter(
                        date__gte=date - timedelta(days=13),
                        date__lte=date - timedelta(days=7),
                        direction="entran",
                        entrance=entrance,
                    ).values_list("total", flat=True)
                )
                prev_exit_total = sum(
                    Report.objects.filter(
                        date__gte=date - timedelta(days=13),
                        date__lte=date - timedelta(days=7),
                        direction="salen",
                        entrance=entrance,
                    ).values_list("total", flat=True)
                )

                enter_total = sum(enter_data)
                exit_total = sum(exit_data)

            context["labels"] = labels
            context["enter_data"] = enter_data
            context["exit_data"] = exit_data

            context["enter_total"] = enter_total
            context["exit_total"] = exit_total
            context["prev_enter_total"] = prev_enter_total
            context["prev_exit_total"] = prev_exit_total

        return context


class EntrancesView(TemplateView):
    template_name = "people_counter/entrances.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        entrances = Entrance.objects.all()

        date = datetime.today() - timedelta(days=1)

        entrances = entrances.annotate(
            total_enter=Sum(
                Case(
                    When(
                        Q(reports__date=date) & Q(reports__direction="entran"),
                        then="reports__total",
                    ),
                    default=0,
                )
            )
        )
        entrances = entrances.annotate(
            total_exit=Sum(
                Case(
                    When(
                        Q(reports__date=date) & Q(reports__direction="salen"),
                        then="reports__total",
                    ),
                    default=0,
                )
            )
        )

        entrances = entrances.annotate(
            total_enter_week=Sum(
                Case(
                    When(
                        Q(reports__date__gte=date - timedelta(days=6))
                        & Q(reports__date__lte=date)
                        & Q(reports__direction="entran"),
                        then="reports__total",
                    ),
                    default=0,
                )
            )
        )
        entrances = entrances.annotate(
            total_exit_week=Sum(
                Case(
                    When(
                        Q(reports__date__gte=date - timedelta(days=6))
                        & Q(reports__date__lte=date)
                        & Q(reports__direction="salen"),
                        then="reports__total",
                    ),
                    default=0,
                )
            )
        )

        context["entrances"] = entrances.order_by("-total_enter")
        context["total_enter_week"] = sum(
            entrances.values_list("total_enter_week", flat=True)
        )
        context["total_exit_week"] = sum(
            entrances.values_list("total_exit_week", flat=True)
        )

        return context


class EntrancesMontView(TemplateView):
    template_name = "people_counter/entrances_month.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year, month = self.request.GET["year_month"].split("-")

        reports = (
            Report.objects.filter(date__month=month, date__year=year)
            .values("entrance__name", "date", "direction", "total")
            .order_by("date", "entrance__name")
        )

        table = {}
        days = set()
        entrances = set()
        directions = set()
        total_days = {}

        for report in reports:
            entrance = report["entrance__name"]
            date = report["date"].strftime("%Y-%m-%d")
            total = report["total"]
            direction = report["direction"]

            days.add(date)
            entrances.add(entrance)
            directions.add(direction)

            if entrance not in table:
                table[entrance] = {}

            if date not in table[entrance]:
                table[entrance][date] = {}

            table[entrance][date][direction] = total

        for entrance in entrances:
            total_enter = 0
            total_exit = 0
            for value in table.get(entrance, {}).values():
                total_enter += value["entran"]
                total_exit += value["salen"]
            table[entrance]["total_enter"] = total_enter
            table[entrance]["total_exit"] = total_exit

        total_total_enter = 0
        total_total_exit = 0

        for day in days:
            total_day_enter = 0
            total_day_exit = 0
            for entrance in entrances:
                total_day_enter += table[entrance][day]["entran"]
                total_total_enter += table[entrance][day]["entran"]
                total_day_exit += table[entrance][day]["salen"]
                total_total_exit += table[entrance][day]["salen"]

            total_days[day] = {"enter": total_day_enter, "exit": total_day_exit}

        context["days_sorted"] = sorted(list(days))
        context["total_days"] = total_days
        context["entrances_sorted"] = sorted(list(entrances))
        context["table"] = table
        context["total_total_enter"] = total_total_enter
        context["total_total_exit"] = total_total_exit

        context["direction"] = self.request.GET["direction"]

        return context


def upload_file(request: WSGIRequest):

    context = {
        "yesterday": datetime.today() - timedelta(days=1),
    }

    if request.method == "POST":

        df = pd.read_excel(request.FILES["file"])

        file = File.objects.create(file=request.FILES["file"])

        for column in df.columns:

            try:
                entrance_id = column.split("Cámara")[1].split("_")[0]
                direction = column.split("El número de personas que ")[1]
            except:
                continue

            report = Report.objects.create(
                entrance_id=entrance_id,
                date=request.POST["date"],
                file=file,
                direction=direction,
            )

            total = 0
            for index, data in df[column].items():
                report_detail = ReportDetail.objects.create(
                    time=df["Tiempo"][index].split("-")[0],
                    quantity=data,
                    report=report,
                )
                total += data

            report.total = total
            report.save()

        return render(request, "people_counter/upload_file.html")
    return render(request, "people_counter/upload_file.html", context=context)


def export_entrances_month(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=datos.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Entradas"

    entrances = Entrance.objects.all().order_by("id")

    columns = ["Fecha", "Día"]
    for entrance in entrances:
        columns.append(f"{entrance} (Entran)")
        columns.append(f"{entrance} (Salen)")
    columns.append("Total entradas")
    columns.append("Total salidas")

    sheet.append(columns)

    year, month = request.GET["year_month"].split("-")

    total_days = calendar.monthrange(int(year), int(month))[1]
    locale.setlocale(locale.LC_ALL, "es_ES")
    for day in range(1, total_days + 1):
        date = datetime(year=int(year), month=int(month), day=day)
        reports = (
            Report.objects.filter(date=date)
            .order_by("direction")
            .order_by("entrance__id")
        )
        row = [date.strftime("%d/%m/%Y"), date.strftime("%A").upper()]

        total_enter = 0
        total_exit = 0
        for report in reports:
            row.append(report.total)
            if report.direction == "entran":
                total_enter += report.total
            else:
                total_exit += report.total

        row.append(total_enter)
        row.append(total_exit)

        sheet.append(row)

    workbook.save(response)

    return response
