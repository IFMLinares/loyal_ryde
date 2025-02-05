import calendar
import locale
import json
from babel.dates import format_date
from datetime import datetime
from io import BytesIO

import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.image import Image
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AnonymousUser, Group, User
from django.core import serializers
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_date
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, DetailView, 
                                ListView,TemplateView, UpdateView, View)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *


# Agregar Cupones de descuento
class DiscountCouponCreateView(CreateView):
    model = DiscountCoupon
    form_class = DiscountCouponForm
    template_name = 'loyal_ryde_system/add_discount_coupon.html'
    success_url = reverse_lazy('loyalRyde:discount_coupon_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        company = form.cleaned_data['company']
        users = CustomUser.objects.filter(company=company)
        for user in users:
            subject = 'New Discount Coupon Available'
            html_message = render_to_string('emails/discount_coupon.html', {'coupon': self.object})
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, 'from@example.com', [user.email], html_message=html_message)
        return response

class DiscountCouponListView(ListView):
    model = DiscountCoupon
    template_name = 'loyal_ryde_system/discount_coupon_list.html'
    context_object_name = 'coupons'

class DiscountCouponUpdateView(UpdateView):
    model = DiscountCoupon
    form_class = DiscountCouponForm
    template_name = 'loyal_ryde_system/update_discount_coupon.html'
    success_url = reverse_lazy('discount_coupon_list')

class DiscountCouponDetailView(DetailView):
    model = DiscountCoupon
    template_name = 'loyal_ryde_system/discount_coupon_detail.html'
    context_object_name = 'coupon'
