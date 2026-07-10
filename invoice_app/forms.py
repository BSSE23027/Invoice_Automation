from django import forms


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel Invoice",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    def clean_excel_file(self):

        file = self.cleaned_data["excel_file"]

        if not file.name.endswith(".xlsx"):
            raise forms.ValidationError(
                "Please upload an Excel (.xlsx) file."
            )

        return file
