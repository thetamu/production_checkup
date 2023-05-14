from copy import copy

from .models import Jun, Mid, Sen, User, Detail, Jobs, Manager, Order
import xlrd
import os, sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'production_checkup.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
django.setup()


def users_juns():
    f = Jun.objects.all()
    u_list = []
    for row in f:
        if row.user not in u_list:
            u_list.append(row.user)
    return User.objects.filter(id__in=(d.pk for d in u_list))


def users_mids():
    f = Mid.objects.all()
    u_list = []
    for row in f:
        if row.user not in u_list:
            u_list.append(row.user)
    return User.objects.filter(id__in=(d.pk for d in u_list))


def users_sens():
    f = Sen.objects.all()
    u_list = []
    for row in f:
        if row.user not in u_list:
            u_list.append(row.user)
    return User.objects.filter(id__in=(d.pk for d in u_list))


def users_managers():
    f = Manager.objects.all()
    u_list = []
    for row in f:
        if row.user not in u_list:
            u_list.append(row.user)
    return User.objects.filter(id__in=(d.pk for d in u_list))


class UploadingFile(object):
    foreign_key_field = ['']
    model = Detail
    open_sheet = None

    def __init__(self, data):
        data = data
        self.uploaded_file = data.get('file')
        self.parsing()

    def parsing(self):
        uploaded_file = self.uploaded_file
        open_to_parsing = xlrd.open_workbook(file_contents=uploaded_file.read())
        open_sheet = open_to_parsing.sheet_by_index(0)
        self.open_sheet = open_sheet
        headers = self.getting_headers()
        order_num = self.getting_order_num()
        details = self.getting_details()

        Order.objects.create(
            order_num=order_num
        )

        for row in headers:
            for row2 in details:
                if open_sheet.cell(row2, row).value != 0 and open_sheet.cell(row, row2).value is not None:
                    price = copy(open_sheet.cell(row2, row).value)
                    detail_numbers = None
                    job = Jobs.objects.get(job_type=headers.get(row))

                    for row3 in range(open_sheet.ncols):
                        if open_sheet.cell(1, row3).value == "кол-во в заказе":
                            price = price / open_sheet.cell(row2, row3).value
                            if detail_numbers is None:
                                detail_numbers = open_sheet.cell(row2, row3).value
                            else:
                                detail_numbers *= open_sheet.cell(row2, row3).value
                        if open_sheet.cell(1, row3).value == "кол-во на 1 сборку":
                            price = price / open_sheet.cell(row2, row3).value
                            if detail_numbers is None:
                                detail_numbers = open_sheet.cell(row2, row3).value
                            else:
                                detail_numbers *= open_sheet.cell(row2, row3).value

                    Detail.objects.create(
                        order_num=order_num,
                        name=details.get(row2),
                        price=round(price, 2),
                        numbers=detail_numbers,
                        numbers_in_order=detail_numbers,
                        jobs=job,
                        order=Order.objects.all().last()
                    )
        return True

    def getting_details(self):
        open_sheet = self.open_sheet
        details = {}
        for row in range(2, open_sheet.nrows):
            value = open_sheet.cell(row, 1).value
            details[row] = value
        return details

    def getting_headers(self):
        open_sheet = self.open_sheet
        headers = {}
        for row in range(open_sheet.ncols):
            value = open_sheet.cell(1, row).value
            for row2 in Jobs.objects.all():
                if value == row2.job_type:
                    headers[row] = value
                else:
                    continue
        return headers

    def getting_order_num(self):
        open_sheet = self.open_sheet
        order_num = open_sheet.cell(0, 2).value
        return order_num

    def getting_detail_name(self):
        open_sheet = self.open_sheet
        detail_name = {}
        for row in range(open_sheet.ncols):
            value = open_sheet.cell(0, row).value
            detail_name[row] = value
        return detail_name



