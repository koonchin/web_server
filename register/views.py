from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import EmployeeForm
from function import get_api_register
# Create your views here.


def register(req):
    if req.method == 'POST':
        employee_form = EmployeeForm(req.POST)
        user_form = UserCreationForm(req.POST)
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.apikey = get_api_register(str(employee.department),'apikey')
            employee.apisecret =  get_api_register(str(employee.department),'apisecret')
            employee.storename =  get_api_register(str(employee.department),'storename')
            employee.vrich_user =  get_api_register(str(employee.department),'vrich_user')
            employee.vrich_password =  get_api_register(str(employee.department),'vrich_password')
            employee.databasename =  get_api_register(str(employee.department),'databasename')
            user.save()
            employee.save()
            
        return redirect('/login/')
    else:
        user_form = UserCreationForm()
        employee_form = EmployeeForm()
    return render(req, "register.html", {'form': user_form, 'emp': employee_form})
