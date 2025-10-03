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
