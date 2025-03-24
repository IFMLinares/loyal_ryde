
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import (CreateView, DetailView, ListView, UpdateView)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context


class DiscountCouponListView(ListView):
    model = DiscountCoupon
    template_name = 'loyal_ryde_system/discount_coupon_list.html'
    context_object_name = 'coupons'
    

class DiscountCouponUpdateView(UpdateView):
    model = DiscountCoupon
    form_class = DiscountCouponForm
    template_name = 'loyal_ryde_system/update_discount_coupon.html'
    success_url = reverse_lazy('discount_coupon_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context


class DiscountCouponDetailView(DetailView):
    model = DiscountCoupon
    template_name = 'loyal_ryde_system/discount_coupon_detail.html'
    context_object_name = 'coupon'
