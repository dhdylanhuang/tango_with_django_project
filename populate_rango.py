import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tango_with_django_project.settings')

import django
django.setup()

from rango.models import Category, Page

def populate():

    python_pages = [
        {'title': 'Official Python Tutorial',
         'url':'http://docs.python.org/3/tutorial/',
         'views': 9282},
        {'title':'How to Think like a Computer Scientist',
         'url':'http://www.greenteapress.com/thinkpython/',
         'views': 8679},
        {'title':'Learn Python in 10 Minutes',
         'url':'http://www.korokithakis.net/tutorials/python/',
         'views': 139494} 
    ]
    
    django_pages = [
        {'title':'Official Django Tutorial',
         'url':'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
         'views': 1023},
        {'title':'Django Rocks',
         'url':'http://www.djangorocks.com/',
         'views': 895},
        {'title':'How to Tango with Django',
         'url':'http://www.tangowithdjango.com/',
         'views': 2748}
    ]

    other_pages = [
        {'title':'Bottle',
         'url':'http://bottlepy.org/docs/dev/',
         'views': 89},
        {'title':'Flask',
         'url':'http://flask.pocoo.org',
         'views': 45}
    ]
    
    pascal_pages = [
        {'title':'Wiki Pascal',
         'url':'https://en.wikipedia.org/wiki/Pascal_(programming_language)',
         'views': 34}
    ]
    
    php_pages = [
        {'title':'PHP Tutorial',
         'url':'https://www.w3schools.com/php/',
         'views': 27}
    ]
    
    prolog = [
        {'title':'Intro into Prolog',
         'url':'https://www.geeksforgeeks.org/prolog-an-introduction/',
         'views': 19}
    ]
    
    post_script_pages = [
        {'title':'What are PostScript Printers',
         'url':'https://www.ibm.com/docs/en/aix/7.2?topic=configuration-postscript-printers',
         'views': 19}
    ]
    
    programming_pages = [
        {'title': 'Best Programming Languages',
         'url':'https://www.hostinger.co.uk/tutorials/best-programming-languages-to-learn',
         'views': 238742}
    ]

    cats = {
        'Python': {'pages': python_pages, 'views': 128, 'likes': 64},
        'Django': {'pages': django_pages, 'views': 64, 'likes': 32},
        'Other Frameworks': {'pages': other_pages, 'views': 32, 'likes': 16},
        'Pascal': {'pages': pascal_pages, 'views':34, 'likes':10},
        'PHP': {'pages': php_pages, 'views':23, 'likes':5},
        'Prolog': {'pages': prolog, 'views':2, 'likes':1},
        'Post Script': {'pages': post_script_pages, 'views':4, 'likes':3},
        'Programming Languages': {'pages': programming_pages, 'views':438, 'likes':345}
    }

    # The code below goes through the cats dictionary and adds all the associated pages for that category
    for cat, cat_data in cats.items():
        c = add_cat(cat, views=cat_data['views'], likes=cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'], p['views'])

    # Print out the categories
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')

def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, views=views)[0] 
    p.url=url
    p.views=views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0] 
    c.save()
    return c

if __name__ == '__main__':
    print('Starting Rango population script...') 
    populate()

