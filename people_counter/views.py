import json
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from django.shortcuts import render
from django.db.models import Subquery, OuterRef, F
from django.views.generic import TemplateView, DetailView
from django.core.handlers.wsgi import WSGIRequest
from .models import File, Report, ReportDetail, Entrance


class HomeView(TemplateView):
    template_name = "people_counter/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entrances"] = Entrance.objects.all()
        context["yesterday"] = datetime.today() - timedelta(1)
        return context


class EntranceView(TemplateView):
    template_name = "people_counter/entrance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        entrance = Entrance.objects.get(id=self.request.GET["entrance"])

        date_range = self.request.GET["range"]
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
