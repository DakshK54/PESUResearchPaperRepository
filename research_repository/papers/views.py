# papers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import ResearchPaper, PaperReview, PaperKeyword, PaperAuthor, ResearchArea, User
from .forms import ResearchPaperForm, DeleteResearchPaperForm, PaperReviewForm, PaperKeywordForm

def list_papers(request):
    papers = ResearchPaper.objects.all()
    return render(request, 'papers/list_papers.html', {'papers': papers})

@transaction.atomic
def add_paper(request):
    if request.method == 'POST':
        form = ResearchPaperForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save()
            messages.success(request, "Research paper added successfully!")
            return redirect('list_papers')
    else:
        form = ResearchPaperForm()
    
    return render(request, 'papers/add_paper.html', {'form': form})

@transaction.atomic
def delete_paper(request):
    if request.method == 'POST':
        form = DeleteResearchPaperForm(request.POST)
        if form.is_valid():
            paper_id = form.cleaned_data['paper_id']
            try:
                paper = ResearchPaper.objects.get(paper_id=paper_id)
                paper.delete()
                messages.success(request, "Research paper deleted successfully!")
            except ResearchPaper.DoesNotExist:
                messages.error(request, "Paper not found.")
            return redirect('list_papers')
    else:
        form = DeleteResearchPaperForm()
    
    return render(request, 'papers/delete_paper.html', {'form': form})