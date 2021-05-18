# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from common.decorators import has_apigateway_manage_permission_for_classfunc
from esb.apps.mixins import TemplateRenderMixin
from esb.bkcore.models import ESBBuffetComponent, ESBBuffetMapping
from esb.common.django_utils import i18n_form
from .forms import ESBBuffetComponentForm, EditESBBuffetComponentForm, ESBBuffetMappingForm, EditESBBuffetMappingForm
from ..system.forms import ComponentSystemForm

menu_active_item = "buffet_manager"
DEFAULT_HOST = "http://paas.bking.com"


class ApplyBuffetCompView(View, TemplateRenderMixin):
    """Apply for a new buffet component"""

    @has_apigateway_manage_permission_for_classfunc
    def get(self, request):
        form = ESBBuffetComponentForm()
        system_form = ComponentSystemForm()
        form = i18n_form(form)
        system_form = i18n_form(system_form)
        return self.render(
            request,
            "manager/buffet_comp/apply.html",
            {
                "form": form,
                "system_form": system_form,
                "menu_active_item": menu_active_item,
            },
        )

    @has_apigateway_manage_permission_for_classfunc
    def post(self, request):
        form = ESBBuffetComponentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            obj = ESBBuffetComponent(submitter=request.user.username, **data)
            obj.save()
            return HttpResponseRedirect(reverse("manager.buffet_comp.list"))
        system_form = ComponentSystemForm()
        form = i18n_form(form)
        system_form = i18n_form(system_form)
        return self.render(
            request,
            "manager/buffet_comp/apply.html",
            {
                "form": form,
                "system_form": system_form,
                "menu_active_item": menu_active_item,
            },
        )


class BuffetCompsView(View, TemplateRenderMixin):
    """Check and approve all BuffetComps"""

    @has_apigateway_manage_permission_for_classfunc
    def get(self, request):
        items = ESBBuffetComponent.objects.all().order_by("system", "registed_path", "registed_http_method")
        try:
            host = settings.PAAS_DOMAIN
        except Exception:
            host = DEFAULT_HOST
        try:
            schema = settings.HTTP_SCHEMA
        except Exception:
            schema = "http"

        schema_prefix = "%s://" % schema
        if not host.startswith(schema_prefix):
            host = "%s://%s" % (schema, host)

        return self.render(
            request,
            "manager/buffet_comp/list.html",
            {
                "items": items,
                "host": "%s/api/c/self-service-api" % host,
                "menu_active_item": menu_active_item,
            },
        )


class EditBuffetCompView(View, TemplateRenderMixin):
    """Edit a BuffetComponent"""

    @has_apigateway_manage_permission_for_classfunc
    def get(self, request, item_id):
        item = ESBBuffetComponent.objects.get(pk=item_id)
        d = item.__dict__
        d["system"] = item.system
        form = EditESBBuffetComponentForm(initial=dict(**d))
        system_form = ComponentSystemForm()
        form = i18n_form(form)
        system_form = i18n_form(system_form)
        return self.render(
            request,
            "manager/buffet_comp/edit.html",
            {
                "item": item,
                "form": form,
                "system_form": system_form,
                "menu_active_item": menu_active_item,
            },
        )

    @has_apigateway_manage_permission_for_classfunc
    def post(self, request, item_id):
        item = ESBBuffetComponent.objects.get(pk=item_id)
        form = EditESBBuffetComponentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            item.__dict__.update(data)
            item.system = data["system"]
            item.save()
            return HttpResponseRedirect(reverse("manager.buffet_comp.list"))

        system_form = ComponentSystemForm()
        form = i18n_form(form)
        system_form = i18n_form(system_form)
        return self.render(
            request,
            "manager/buffet_comp/edit.html",
            {
                "form": form,
                "system_form": system_form,
                "menu_active_item": menu_active_item,
            },
        )


class BuffetMappingsView(View, TemplateRenderMixin):
    """Check All Mappings"""

    @has_apigateway_manage_permission_for_classfunc
    def get(self, request):
        form = ESBBuffetMappingForm()
        form_edit = EditESBBuffetMappingForm()
        items = ESBBuffetMapping.objects.all().order_by("created_time")
        return self.render(
            request,
            "manager/buffet_comp/mapping/list.html",
            {
                "items": items,
                "form": form,
                "form_edit": form_edit,
                "menu_active_item": menu_active_item,
            },
        )
