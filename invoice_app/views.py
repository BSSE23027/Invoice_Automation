from django.http import FileResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from invoice_app.forms import ExcelUploadForm
from invoice_app.services.file_manager import FileManager
from invoice_app.services.invoice_service import InvoiceService

def home(request):

    service = InvoiceService()

    invoice = None
    error = None

    try:

        invoice = service.get_latest_invoice()

    except Exception as e:

        messages.error(
            request,
            str(e)
        )

    form = ExcelUploadForm()

    return render(
        request,
        "invoice_app/home.html",
        {
            "invoice": invoice,
            "form": form,
        },
    )


def process_invoice(request):

    if request.method != "POST":
        return redirect("home")

    form = ExcelUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        return redirect("home")

    manager = FileManager()
    excel_path = None

    try:
        uploaded_file = form.cleaned_data["excel_file"]

        excel_path = manager.save_uploaded_excel(uploaded_file)

        service = InvoiceService()

        updated_file = service.process_invoice(excel_path)

        messages.success(
            request,
            "Invoice processed successfully."
        )

        response = FileResponse(
            open(updated_file, "rb"),
            as_attachment=True,
            filename="Updated_Invoice.xlsx"
        )

        return response

    except Exception as e:

        messages.error(
            request,
            str(e)
        )

        service = InvoiceService()

        return render(
            request,
            "invoice_app/home.html",
            {
                "invoice": service.get_latest_invoice(),
                "form": ExcelUploadForm(),
            },
        )

    finally:

        if excel_path:
            manager.delete_file(excel_path)



def refresh_invoice(request):

    service = InvoiceService()

    try:
        invoice = service.refresh_latest_invoice()

        if invoice is None:
            messages.warning(
                request,
                "No invoice email found."
            )
        else:
            messages.success(
                request,
                "Latest invoice refreshed successfully."
            )

    except Exception as e:

        messages.error(
            request,
            str(e)
        )

    return redirect("home")