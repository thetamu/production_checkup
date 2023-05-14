from django.forms import DateInput
from django_filters import FilterSet, CharFilter, DateFilter, ModelChoiceFilter, ChoiceFilter, DateRangeFilter
from .models import Jun, Mid, Detail, Order, Jobs, DoneDetail


class CustomSearchFilter(FilterSet):
    last_names_in = CharFilter(
        field_name='last_name',
        lookup_expr='contains',
        label="Фамилия сотрудника:"
    )


class DetailFilter(FilterSet):
    time_when_created = DateFilter(
        field_name='time_when_created',
        widget=DateInput(attrs={'type': 'date'}),
        lookup_expr='gte',
        label="Заказы позднее:",
    )

    order_num = ModelChoiceFilter(
        field_name='order_num',
        queryset=Order.objects.filter(is_done=False),
        label="По номеру заказа:",
        empty_label="Все заказы",
    )

    jobs = ModelChoiceFilter(
        field_name='jobs',
        queryset=Jobs.objects.all(),
        label="По типу обработки:",
        empty_label="Обработка",
    )

    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label="По названию:",
    )

