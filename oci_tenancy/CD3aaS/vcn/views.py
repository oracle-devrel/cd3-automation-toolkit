from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView, FormView, TemplateView)
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404
from django.conf import settings
from django.db import IntegrityError

import os, shutil
from .forms import TenancyForm, UpdateForm, PrivatekeyForm
from .models import Tenancy
from .cd3cryto import Cd3Crypto
from .generatorTF import GeneratorTF


class TenancyListView(ListView):
    model = Tenancy
    template_name = 'vcn/tenancy_list.html'

    def get_queryset(self):
        # return Tenancy.objects.filter(Username=self.request.session.get('displayname')).order_by('-Created_Date')
        try:
            query = Tenancy.objects.filter(Username=self.request.session.get('displayname')).order_by('-Created_Date')
            return query
        except:
            raise HttpResponse('No customer list')


class TenancyDetailView(DetailView):
    model = Tenancy
    template_name = 'vcn/tenancy_detail.html'

    def get(self, request, *args, **kwargs):
        # query = Tenancy.objects.filter(pk=self.kwargs.get("pk")).values()[0]
        try:
            query = get_object_or_404(Tenancy, pk=self.kwargs.get("pk"))
            if self.request.session.get('displayname').strip() in query.Username.strip():
                return super().get(request, *args, **kwargs)
        except Tenancy.DoesNotExist:
            raise Http404('Unauthorized access')


class TenancyCreateView(CreateView):
    form_class = TenancyForm
    model = Tenancy
    template_name = 'vcn/tenancy_form.html'
    redirect_field_name = 'vcn/tenancy_detail.html'

    def form_valid(self, form):
        try:
            username = self.request.session.get('displayname')
            tf_form = form.save(commit=False)
            tf_form.Username = username
            keyfile = tf_form.Key_File
            tf_form.Key_File = ""
            tf_form.save()
            gt = GeneratorTF(tf_form, keyfile)
            gt.generate_tf()
            tf_form.save()
            return super().form_valid(form)
        except IntegrityError as e:
            print(e)
            return HttpResponse('Customer already exists')
            # return super().form_invalid(form)


class TenancyUpdateView(UpdateView):
    form_class = UpdateForm
    model = Tenancy
    template_name = 'vcn/tenancy_form.html'
    redirect_field_name = 'vcn/tenancy_detail.html'

    def get(self, request, *args, **kwargs):
        # query = Tenancy.objects.filter(pk=self.kwargs.get("pk")).values()[0]
        try:
            query = get_object_or_404(Tenancy, pk=self.kwargs.get("pk"))
            if self.request.session.get('displayname').strip() in query.Username.strip():
                return super().get(request, *args, **kwargs)
        except Tenancy.DoesNotExist:
            raise Http404('Unauthorized access')

    def form_valid(self, form):
        tf_form = form.save(commit=False)
        keyfile = tf_form.Key_File
        tf_form.Key_File = ""
        tf_form.Stack_Update = True
        tf_form.save()
        gt = GeneratorTF(tf_form, keyfile)
        gt.generate_tf()
        tf_form.save()
        return super().form_valid(form)


class TenancyDeleteView(DeleteView):
    model = Tenancy
    success_url = reverse_lazy('vcn:tenancy_list')

    def get(self, request, *args, **kwargs):
        # query = Tenancy.objects.filter(pk=self.kwargs.get("pk")).values()[0]
        try:
            query = get_object_or_404(Tenancy, pk=self.kwargs.get("pk"))
            if self.request.session.get('displayname').strip() in query.Username.strip():
                return super().get(request, *args, **kwargs)
        except Tenancy.DoesNotExist:
            raise Http404('Unauthorized access')

    def post(self, request, *args, **kwargs):
        try:
            query = get_object_or_404(Tenancy, pk=self.kwargs.get("pk"))
            if os.path.exists(settings.MEDIA_ROOT + query.Terraform_Files):
                os.remove(settings.MEDIA_ROOT + query.Terraform_Files)
            if os.path.exists(settings.MEDIA_ROOT + query.CD3_Excel.name):
                os.remove(settings.MEDIA_ROOT + query.CD3_Excel.name)
            return self.delete(request, *args, **kwargs)
        except Tenancy.DoesNotExist:
            raise Http404('Unauthorized access')



# class GenerateTFView(TemplateView):
#     model = Tenancy
#     template_name = 'vcn/tenancy_detail.html'
#     success_url = 'vcn/tenancy_detail.html'
#
#     def get(self, request, *args, **kwargs):
#         query = Tenancy.objects.get(pk=self.kwargs.get("pk"))
#         gt = GeneratorTF(query)
#         gt.generate_tf()
#         return redirect('vcn:tenancy_detail', pk=self.kwargs.get("pk"))
#
#
# class RMplanView(TemplateView):
#     model = Tenancy
#     template_name = 'vcn/tenancy_detail.html'
#     success_url = 'vcn/tenancy_detail.html'
#
#     def post(self, request, *args, **kwargs):
#         return super(RMplanView, self).post(self, request, *args, **kwargs)
