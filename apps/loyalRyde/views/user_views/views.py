from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import (CreateView, ListView, UpdateView, DeleteView, TemplateView)

from django.contrib import messages

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *

from apps.loyalRyde.views_initial import send_styled_email

#  Agregar usuario
class UserAdd(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'loyal_ryde_system/add_user.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            random_password = get_random_string(length=10)
            user.set_password(random_password)
            user.save()
            send_styled_email(user, random_password)
            if user.role == 'administrador':
                return HttpResponseRedirect(reverse_lazy('core:user_list_admin'))
            elif user.role == 'despachador':
                return HttpResponseRedirect(reverse_lazy('core:user_list_dispatcher'))
            elif user.role == 'supervisor':
                return HttpResponseRedirect(reverse_lazy('core:user_list_supervisor'))
            elif user.role == 'operator':
                return HttpResponseRedirect(reverse_lazy('core:user_list_operator'))
        return render(request, self.template_name, {'form': form})

#  Agregar usuario (de las eempresas)
class UserCompanyAdd(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'loyal_ryde_system/add_user_company.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Verifica el nombre de la compañía antes de guardar el usuario
            if user.company.name != "Loyal ride":
                # Asigna permisos de usuario normal
                user.is_staff = False
                # Puedes agregar el usuario a un grupo con permisos específicos si es necesario
                # group = Group.objects.get(name='Normal Users')
                # user.groups.add(group)

            random_password = get_random_string(length=10)
            user.set_password(random_password)
            user.save()
            send_styled_email(user,random_password)
            return HttpResponseRedirect(reverse_lazy('core:user_list_supervisor'))
        return render(request, self.template_name, {'form': form})

# Lista de administradores
class UserAdminListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'loyal_ryde_system/user_list_view.html'
    context_object_name = "users"

    def get_queryset(self):
        return CustomUser.objects.filter(role='administrador')

# Lista de despacahdores
class UserDispatchListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'loyal_ryde_system/user_list_view_dispatcher.html'
    context_object_name = "users"

    def get_queryset(self):
        return CustomUser.objects.filter(role='despachador')

# Lista de Operadores (Usuarios del cliente)
class UserOperatorListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'loyal_ryde_system/user_list_view_operators.html'
    context_object_name = 'users'

    def get_queryset(self):
        # Filtra el queryset para incluir solo usuarios con el rol 'operator'
        return CustomUser.objects.filter(role='operator')

# Lista de Supervisores (Usuarios del cliente)
class UserSupervisorListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'loyal_ryde_system/user_list_view_supervisors.html'
    context_object_name = 'users'

    def get_queryset(self):
        # Filtra el queryset para incluir solo usuarios con el rol 'operator'
        return CustomUser.objects.filter(role='supervisor')

# Actualizar usuario Operador
class UserOperatorUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'loyal_ryde_system/add_user_company.html'
    context_object_name = 'user'

    def get_success_url(self):
        return reverse_lazy('core:user_list_operator')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_title'] = "Actualizar"
        return context

# Actualizar usuario Supervisor
class UserSupervisorUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'loyal_ryde_system/add_user_company.html'
    context_object_name = 'user'

    def get_success_url(self):
        return reverse_lazy('core:user_list_supervisor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_title'] = "Actualizar"
        return context
    
# eliminación de conductores
class DeleteUser(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'loyal_ryde_system/delete_departure.html'
    success_url = reverse_lazy('core:index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario eliminado correctamente')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Eliminar Usuario"
        context['text'] = "¿Está seguro de eliminar este usuario?"
        context['url_cancel'] = self.success_url
        return context
    
# perfil
class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = 'loyal_ryde_system/perfil.html'
# perfil