from django.shortcuts import render

def home(request):
    return render(request, 'salary_pdf_template.html')  