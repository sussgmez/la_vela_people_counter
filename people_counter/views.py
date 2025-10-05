import json
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from django.core.handlers.wsgi import WSGIRequest
from .models import File, Report, ReportDetail, Entrance


class HomeView(TemplateView):
    template_name = "people_counter/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entrances"] = Entrance.objects.all()
        return context


class EntranceView(TemplateView):
    template_name = "people_counter/entrance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        entrance = Entrance.objects.get(id=self.request.GET["entrance"])

        date_range = self.request.GET["range"]

        if date_range == "day":

            try:
                enter_report = entrance.reports.get(
                    date=datetime.today() - timedelta(days=1), direction="entran"
                )
                enter_report_before1 = entrance.reports.get(
                    date=datetime.today() - timedelta(days=2), direction="entran"
                )

                enter_percentage = round(
                    (
                        (enter_report.total - enter_report_before1.total)
                        / enter_report_before1.total
                    )
                    * 100,
                    2,
                )

                enter_reportdetails = list(
                    ReportDetail.objects.filter(report=enter_report).values_list(
                        "quantity", flat=True
                    )
                )
            except:
                enter_report = None
                enter_reportdetails = []

            try:
                exit_report = entrance.reports.get(
                    date=datetime.today() - timedelta(days=1), direction="salen"
                )
                exit_report_before1 = entrance.reports.get(
                    date=datetime.today() - timedelta(days=2), direction="salen"
                )

                exit_percentage = round(
                    (
                        (exit_report.total - exit_report_before1.total)
                        / exit_report_before1.total
                    )
                    * 100,
                    2,
                )

                exit_reportdetails = list(
                    ReportDetail.objects.filter(report=exit_report).values_list(
                        "quantity", flat=True
                    )
                )
            except:
                exit_report = None
                exit_reportdetails = []

            hours = [f"{x}:00" for x in range(1, 25)]

            context["labels"] = json.dumps(hours)

            context["enter_report"] = enter_report
            context["enter_report_before1"] = enter_report_before1
            context["enter_reportdetails"] = enter_reportdetails
            context["enter_percentage"] = enter_percentage

            context["exit_report"] = exit_report
            context["exit_report_before1"] = exit_report_before1
            context["exit_reportdetails"] = exit_reportdetails
            context["exit_percentage"] = exit_percentage

        elif date_range == "week":

            start_date = datetime.today() - timedelta(days=1)
            week = [start_date - timedelta(days=x) for x in range(7)][::-1]

            context["labels"] = json.dumps([date.strftime("%d/%m") for date in week])

            enter_report = []
            exit_report = []
            for date in week:
                try:
                    enter_report.append(
                        entrance.reports.get(date=date, direction="entran").total
                    )
                    exit_report.append(
                        entrance.reports.get(date=date, direction="salen").total
                    )
                except:
                    enter_report.append(0)
                    exit_report.append(0)

            context["enter_reportdetails"] = enter_report
            context["exit_reportdetails"] = exit_report

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
