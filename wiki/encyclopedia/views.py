import os
import random

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from .util import list_entries
from . import util
from .util import get_entry, list_entries, save_entry
from django.shortcuts import render, redirect


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry_page(request, title):
    try:
        content = get_entry(title)
        return render(request, 'encyclopedia/entry_page.html', {'title': title, 'content': content})
    except FileNotFoundError:
        return HttpResponse("Page not found!")


def search(request):
    query = request.GET.get('q')
    if query:
            # Get a list of entry names
        all_entries = list_entries()
            # Filter entries where the title contains the query string
        entries = [entry for entry in all_entries if query.lower() in entry.lower()]

        if entries:
            # If exact match found, redirect to the entry page
            for entry in entries:
                if entry.lower() == query.lower():
                    return redirect('entry_page', title=entry)
            # If no exact match, display search results
            return render(request, 'encyclopedia/search_results.html', {'entries': entries, 'query': query})
        else:
            # No match found, redirect to index page
            return redirect('index')
    else:
        # If no query provided, redirect to index page
        return redirect('index')



from django.shortcuts import render, redirect
import os


def create_new_page(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        # Validate if title is not empty
        if title:
            # Check if entry already exists
            if os.path.exists(f'entries/{title}.md'):
                return render(request, 'encyclopedia/new_page.html', {'message': 'Entry already exists'})

            # Save the new entry to disk
            with open(f'entries/{title}.md', 'w') as file:
                file.write(content)

            # Redirect to the new entry's page
            return redirect('entry_page', title=title)
        else:
            return render(request, 'encyclopedia/new_page.html', {'message': 'Title cannot be empty'})
    else:
        return render(request, 'encyclopedia/new_page.html')

def edit_entry(request, title):
    # Get existing content of the entry
    content = get_entry(title)
    if request.method == 'POST':
        # Update entry with new content
        new_content = request.POST.get('content')
        save_entry(title, new_content)
        # Redirect back to entry's page
        return redirect('entry_page', title=title)
    else:
        return render(request, 'encyclopedia/edit_entry.html', {'title': title, 'content': content})

def random_page(request):
    # Get the total number of entries in the database
    en = list_entries()
    total_entries = len(en)

    # Get a random entry from the list of entries
    random_entry = random.choice(en)

    # Redirect the user to the random entry's page
    return redirect('entry_page', title=random_entry)