from datetime import datetime
import json
import os

import django
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from allocation.domain import model
from allocation.service_layer import services, unit_of_work

os.environ["DJANGO_SETTINGS_MODULE"] = "djangoproject.django_project.settings"
django.setup()


@csrf_exempt
def add_batch(request):
    data = json.loads(request.body)
    eta = data["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        data["ref"], data["sku"], data["qty"], eta,
        unit_of_work.DjangoUnitOfWork(),
    )
    return HttpResponse("OK", status=201)


@csrf_exempt
def allocate(request):
    data = json.loads(request.body)
    try:
        batchref = services.allocate(
            data["orderid"],
            data["sku"],
            data["qty"],
            unit_of_work.DjangoUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return JsonResponse({"message": str(e)}, status=400)

    return JsonResponse({"batchref": batchref}, status=201)
