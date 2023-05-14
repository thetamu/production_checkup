from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView
from .filters import CustomSearchFilter, DetailFilter
from .forms import CustomUserForm, CustomJobsForm, SelectMidForm, SelectSenForm, DetailDoneForm, CustomUserUpdateForm, \
    DetailUpdateForm, DoneDetailArchiveForm
from .models import Detail, Jun, Mid, Sen, Manager, Jobs, PermissionToJob, User, DoneDetail, Order
from .extensions import users_juns, users_mids, users_sens, UploadingFile, users_managers


class HomepageView(LoginRequiredMixin, ListView):
    context_object_name = 'details'
    model = Detail
    template_name = 'homepage.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['juns'] = Jun.objects.all()
        context['mids'] = Mid.objects.all()
        context['sens'] = Sen.objects.all()
        context['managers'] = Manager.objects.all()
        context['req_is_sen'] = self.req_is_sen()
        context['req_is_mid'] = self.req_is_mid()
        context['req_is_jun'] = self.req_is_jun()
        context['req_is_manager'] = self.req_is_manager()
        context['detail_done_form'] = DetailDoneForm()
        context['filterset'] = self.filterset
        if self.request.user in users_mids():
            context['mids_juns'] = Jun.objects.filter(mid=Mid.objects.get(user=self.request.user))
        return context

    def get_queryset(self):
        details = Detail.objects.all()
        details_complite_list = []
        for row in details:
            for row2 in self.request.user.permissiontojob_set.all():
                if row.jobs == row2.jobs and row.is_done is False:
                    details_complite_list.append(row.pk)
        self.filterset = DetailFilter(
            self.request.GET,
            Detail.objects.filter(pk__in=details_complite_list).order_by('pk')
        )
        return self.filterset.qs

    def req_is_sen(self):
        if self.request.user in users_sens():
            return True
        else:
            return False

    def req_is_mid(self):
        if self.request.user in users_mids():
            return True
        else:
            return False

    def req_is_jun(self):
        if self.request.user in users_juns():
            return True
        else:
            return False

    def req_is_manager(self):
        if self.request.user in users_managers():
            return True
        else:
            return False


@login_required
def detail_done(request, pk):
    if request.POST:
        user = request.user
        form = DetailDoneForm(request.POST)
        detail = Detail.objects.get(pk=pk)
        order = Order.objects.get(order_num=detail.order_num)
        if request.user in users_mids():
            if form.is_valid():
                if form.cleaned_data['numbers'] <= detail.numbers:
                    if request.POST.get('af') != 'Для себя':
                        jun = Jun.objects.get(pk=request.POST.get('af'))
                        user = jun.user
                    reward = detail.jobs.job_reward * (form.cleaned_data["numbers"] * detail.price)
                    DoneDetail.objects.create(
                        order_num=detail.order_num,
                        name=detail.name,
                        numbers=form.cleaned_data['numbers'],
                        price=detail.price,
                        user=user,
                        jobs=detail.jobs,
                        order=order,
                        reward=round(reward, 2)
                    )

                    detail.numbers -= form.cleaned_data['numbers']
                    detail.save()
                    messages.success(request, 'Успешно')
                    if detail.numbers == 0:
                        detail.is_done = True
                        detail.save()
                        counter = True
                        for row in order.detail_set.all():
                            if row.is_done is True:
                                continue
                            else:
                                counter = False
                        if counter is True:
                            order.is_done = True
                            order.save()
                    return HttpResponseRedirect("/")
                else:
                    messages.error(request, 'Что-пошло не так')
                    return HttpResponseRedirect("/")
        else:
            if form.is_valid():
                if form.cleaned_data['numbers'] <= detail.numbers:
                    reward = detail.jobs.job_reward * (form.cleaned_data["numbers"] * detail.price)
                    DoneDetail.objects.create(
                        order_num=detail.order_num,
                        name=detail.name,
                        numbers=form.cleaned_data['numbers'],
                        price=detail.price,
                        user=user,
                        jobs=detail.jobs,
                        order=order,
                        reward=round(reward, 2)
                    )

                    detail.numbers -= form.cleaned_data['numbers']
                    detail.save()
                    if detail.numbers == 0:
                        detail.is_done = True
                        detail.save()
                        messages.success(request, 'Успешно')
                        counter = True
                        for row in order.detail_set.all():
                            if row.is_done is True:
                                continue
                            else:
                                counter = False
                        if counter is True:
                            order.is_done = True
                            order.save()
                    return HttpResponseRedirect("/")
                else:
                    messages.error(request, 'Что-пошло не так')
                    return HttpResponseRedirect("/")
    return render(request, 'home.html', {'form': form})


@login_required
def detail_update(request, pk):
    if request.POST:
        form = DetailUpdateForm(request.POST)
        done_detail = DoneDetail.objects.get(pk=pk)
        user = done_detail.user
        order = Order.objects.get(order_num=done_detail.order_num)
        detail = Detail.objects.get(order=order, jobs=done_detail.jobs, name=done_detail.name)
        if request.user in users_sens() or request.user.is_superuser:
            if form.is_valid():
                if 0 < form.cleaned_data['numbers'] <= detail.numbers_in_order:
                    change_num = done_detail.numbers - form.cleaned_data['numbers']
                    done_detail.numbers = form.cleaned_data['numbers']
                    done_detail.save()
                    detail.numbers += change_num
                    if detail.is_done is True:
                        detail.is_done = False
                    detail.save()
                    if order.is_done is True:
                        order.is_done = False
                    order.save()
                    messages.success(request, 'Успешно')
                elif form.cleaned_data['numbers'] == 0:
                    detail.numbers += done_detail.numbers
                    done_detail.delete()
                    if detail.is_done is True:
                        detail.is_done = False
                    detail.save()
                    if order.is_done is True:
                        order.is_done = False
                    order.save()
                    messages.success(request, 'Успешно')
                else:
                    messages.error(request, 'Что-пошло не так')
                return HttpResponseRedirect(''.join(f"/profile/{user.pk}"))
    return render(request, 'home.html', {'form': form})


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_sen'] = self.is_sen()
        context['is_mid'] = self.is_mid()
        context['is_jun'] = self.is_jun()
        context['is_manager'] = self.is_manager()
        context['req_is_sen'] = self.req_is_sen()
        context['req_is_mid'] = self.req_is_mid()
        context['req_is_jun'] = self.req_is_jun()
        context['req_is_manager'] = self.req_is_manager()
        context['jobs'] = Jobs.objects.all()
        context['juns'] = Jun.objects.all()
        context['mids'] = Mid.objects.all()
        context['sens'] = Sen.objects.all()
        context['managers'] = Manager.objects.all()
        context['mid_form'] = SelectMidForm()
        context['sen_form'] = SelectSenForm()
        context['permissions'] = self.permission_list()
        context['done_details'] = self.done_details()
        context['full_reward'] = self.full_reward()
        context['team_full_reward'] = self.team_full_reward()
        context['detail_update_form'] = DetailUpdateForm()
        return context

    def done_details(self):
        done_details = []
        for row in DoneDetail.objects.filter(user=self.get_object()):
            if datetime.now().month == row.time_when_done.month\
                    and datetime.now().year == row.time_when_done.year:
                done_details.append(row)
        return done_details

    def full_reward(self):
        full_reward = 0
        for row in DoneDetail.objects.filter(user=self.get_object()):
            if datetime.now().month == row.time_when_done.month\
                    and datetime.now().year == row.time_when_done.year:
                full_reward += row.reward
        return round(full_reward, 2)

    def team_full_reward(self):
        if self.is_mid():
            team_full_reward = 0
            mid = Mid.objects.get(user=self.get_object())
            juns = mid.jun_set.all()
            for row in juns:
                for row2 in DoneDetail.objects.filter(user=row.user):
                    if datetime.now().month == row2.time_when_done.month:
                        team_full_reward += row2.reward
            return team_full_reward

    def permission_list(self):
        permissions = PermissionToJob.objects.filter(user=self.get_object())
        permission_list = []
        for row in permissions:
            permission_list.append(row.jobs)
        return permission_list

    def is_sen(self):
        if self.get_object() in users_sens():
            return True
        else:
            return False

    def is_mid(self):
        if self.get_object() in users_mids():
            return True
        else:
            return False

    def is_jun(self):
        if self.get_object() in users_juns():
            return True
        else:
            return False

    def is_manager(self):
        if self.get_object() in users_managers():
            return True
        else:
            return False

    def req_is_sen(self):
        if self.request.user in users_sens():
            return True
        else:
            return False

    def req_is_mid(self):
        if self.request.user in users_mids():
            return True
        else:
            return False

    def req_is_jun(self):
        if self.request.user in users_juns():
            return True
        else:
            return False

    def req_is_manager(self):
        if self.request.user in users_managers():
            return True
        else:
            return False


@login_required
def select_mid(request, pk):
    if request.POST:
        user = User.objects.get(pk=pk)
        form = SelectMidForm(request.POST)
        if form.is_valid():
            jun = Jun.objects.get(user=user)
            mid = form.cleaned_data['mid']
            jun.mid = mid
            jun.save()
            return HttpResponseRedirect(''.join(f"/profile/{user.pk}"))
    return render(request, 'profile.html', {'form': form})


@login_required
def unselect_mid(request, pk):
    user = User.objects.get(pk=pk)
    jun = Jun.objects.get(user=user)
    jun.mid = None
    jun.save()
    return redirect(''.join(f"/profile/{user.pk}"))


@login_required
def select_sen(request, pk):
    if request.POST:
        user = User.objects.get(pk=pk)
        form = SelectSenForm(request.POST)
        mid_man_check = None
        if user in users_mids():
            mid_man_check = True
        elif user in users_managers():
            mid_man_check = False
        if form.is_valid():
            if mid_man_check:
                mid = Mid.objects.get(user=user)
                sen = form.cleaned_data['sen']
                mid.sen = sen
                mid.save()
            else:
                manager = Manager.objects.get(user=user)
                sen = form.cleaned_data['sen']
                manager.sen = sen
                manager.save()
            return HttpResponseRedirect(''.join(f"/profile/{user.pk}"))
    return render(request, 'profile.html', {'form': form})


@login_required
def unselect_sen(request, pk):
    user = User.objects.get(pk=pk)
    mid_man_check = None
    if user in users_mids():
        mid_man_check = True
    elif user in users_managers():
        mid_man_check = False
    if mid_man_check:
        mid = Mid.objects.get(user=user)
        mid.sen = None
        mid.save()
    else:
        manager = Manager.objects.get(user=user)
        manager.sen = None
        manager.save()
    return redirect(''.join(f"/profile/{user.pk}"))


@login_required
def take_permission(request, pk, jpk):
    user = User.objects.get(pk=pk)
    job = Jobs.objects.get(pk=jpk)
    PermissionToJob.objects.create(user=user, jobs=job)
    return redirect(''.join(f"/profile/{user.pk}"))


@login_required
def untake_permission(request, pk, jpk):
    user = User.objects.get(pk=pk)
    job = Jobs.objects.get(pk=jpk)
    PermissionToJob.objects.get(user=user, jobs=job).delete()
    return redirect(''.join(f"/profile/{user.pk}"))


class ProfileCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('personal_account.add_user',)
    form_class = CustomUserForm
    model = User
    template_name = 'create_new_profile.html'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        finally:
            d = form.cleaned_data['user_status']
            if d == 'Jun':
                Jun.objects.create(user=User.objects.get(username=form.cleaned_data['username']))
            elif d == 'Mid':
                Mid.objects.create(user=User.objects.get(username=form.cleaned_data['username']))
            elif d == 'Sen':
                Sen.objects.create(user=User.objects.get(username=form.cleaned_data['username']))
                user = User.objects.get(username=form.cleaned_data['username'])
                sens_group = Group.objects.get(name='Sens')
                if not user.groups.filter(name='Sens').exists():
                    sens_group.user_set.add(user)
            elif d == 'Manager':
                Manager.objects.create(user=User.objects.get(username=form.cleaned_data['username']))
                user = User.objects.get(username=form.cleaned_data['username'])
                sens_group = Group.objects.get(name='Managers')
                if not user.groups.filter(name='Managers').exists():
                    sens_group.user_set.add(user)


class DoneDetailArchiveView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'done_detail_archive.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DoneDetailArchiveForm
        return context


def done_detail_archive(request):
    if request.POST:
        form = DoneDetailArchiveForm(request.POST)
        pk = request.POST.get('pk')
        if form.is_valid():
            month = request.POST.get('month')
            year = request.POST.get('year')
            print(request.POST.get('pk'), request.POST.get('year'))
            return HttpResponseRedirect(''.join(f"archive/{pk}"))
    return render(request, 'done_detail_archive_success.html', locals(), {'form': form})

class ProfileUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('personal_account.change_user',)
    form_class = CustomUserUpdateForm
    model = User
    template_name = 'update_profile.html'
    success_url = reverse_lazy('search_user')


class ProfileSearchView(PermissionRequiredMixin, ListView):
    permission_required = ('personal_account.add_user',)
    model = User
    ordering = 'id'
    template_name = 'search_user.html'
    context_object_name = 'users'
    paginate_by = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Jobs.objects.all()
        context['filterset'] = self.filterset
        context['is_sen'] = self.is_sen()
        return context

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        self.filterset = CustomSearchFilter(self.request.GET, queryset)
        self.paginate_by = 10
        return self.filterset.qs

    def is_sen(self):
        if self.request.user in users_sens():
            return True
        else:
            return False


class ProfileDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('personal_account.delete_user',)
    model = User
    template_name = 'delete_profile.html'
    success_url = reverse_lazy('search_user')


class JobsCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('personal_account.add_jobs',)
    form_class = CustomJobsForm
    model = Jobs
    template_name = 'create_jobs.html'
    success_url = reverse_lazy('create_job')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Jobs.objects.all().order_by('job_type')
        return context

    def form_valid(self, form):
        jobs = form.save(commit=False)
        jobs.job_reward = jobs.job_reward / 100
        return super().form_valid(form)


class JobsDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('personal_account.delete_job',)
    model = Jobs
    template_name = 'delete_job.html'
    success_url = reverse_lazy('create_job')


class DetailCreateView(PermissionRequiredMixin, ListView):
    permission_required = ('personal_account.add_detail',)
    model = Order
    template_name = 'upload_detail.html'
    context_object_name = 'orders'
    ordering = 'is_done'
    paginate_by = 20


class OrderInfoView(PermissionRequiredMixin, DetailView):
    permission_required = ('personal_account.view_order',)
    model = Order
    context_object_name = 'order'
    template_name = 'order_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.get_object().detail_set.all().order_by('name')
        return context


def download_detail(request):
    if request.POST:
        file = request.FILES['file']
        uploading_file = UploadingFile({'file': file})
        if UploadingFile:
            messages.success(request, 'Успешно. Файл прочитан. Заказ создан')
        else:
            messages.error(request, "Что-то пошло не так. Проверьте содержимое файла")
        return HttpResponseRedirect(''.join(f"/detail/upload"))
    return render(request, 'detail_success.html', locals())











