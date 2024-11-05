# papers/forms.py
from django import forms
from .models import ResearchPaper, PaperReview, PaperKeyword

class ResearchPaperForm(forms.ModelForm):
    class Meta:
        model = ResearchPaper
        fields = ['title', 'abstract', 'doi', 'citation_count', 'journal_name', 'publication_year', 'pdf_data', 'approval_status', 'version']

class DeleteResearchPaperForm(forms.Form):
    paper_id = forms.IntegerField(label="Paper ID")