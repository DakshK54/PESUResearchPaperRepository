# papers/forms.py
from django import forms
from .models import ResearchPaper, PaperReview, PaperKeyword, User

class ResearchPaperForm(forms.ModelForm):
    class Meta:
        model = ResearchPaper
        fields = [
            'title', 'abstract', 'doi', 'citation_count', 
            'journal_name', 'publication_year', 'pdf_data', 
            'approval_status', 'version'
        ]

class PaperReviewForm(forms.ModelForm):
    class Meta:
        model = PaperReview
        fields = ['paper', 'reviewer', 'rating', 'comments', 'review_date']
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PaperKeywordForm(forms.ModelForm):
    class Meta:
        model = PaperKeyword
        fields = ['paper', 'keyword']

class DeleteResearchPaperForm(forms.Form):
    paper_id = forms.IntegerField(label="Paper ID")
