from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm, UserEditForm
from rango.models import Category, UserProfile
from rango.models import Page
from registration.backends.simple.views import RegistrationView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list
    visitor_cookie_handler(request)
    #obtain response object early so we can add cooking information
    response = render(request, 'rango/index.html', context=context_dict)
    #return response back to the user, updating any cookies that need changed
    return response


class AboutView(View):
    def get(self, request):
        context_dict = {}
        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        return render(request, 'rango/about.html',context_dict)


def show_category(request, category_name_slug):
    # create a context dictionary to pass to template rendering engine
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
        
    if request.method == 'POST':
        if request.method == 'POST':
            query = request.POST['query'].strip()
        if query:
            # Assuming run_query is your function to perform the search
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

def get_category_list(max_results=0, starts_with=''): 
    category_list = []
    
    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)
        
    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results] 
    return category_list

class CategorySuggestionView(View): 
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
            
        category_list = get_category_list(max_results=8, starts_with=suggestion)
            
        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')
            
        return render(request, 'rango/categories.html', {'categories': category_list})

class LikeCategoryView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        category_id = request.GET['category_id'] 
        try:
            category = Category.objects.get(id=int(category_id)) 
        except Category.DoesNotExist:
            return HttpResponse(-1) 
        except ValueError:
            return HttpResponse(-1) 
        
        category.likes = category.likes + 1
        category.save()
        return HttpResponse(category.likes)


class SearchAddPageView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']
    
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')
        except ValueError:
            return HttpResponse('Error - bad category ID.')
            
        p = Page.objects.get_or_create(category=category, title=title, url=url)
        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})

@login_required
def add_page(request, category_name_slug): 
    try:
        category = Category.objects.get(slug=category_name_slug) 
    except Category.DoesNotExist:
           category = None
    if category is None:
        return redirect('/rango/')
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid(): 
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
            else: print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def search(request): 
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip() 
        if query:
        # Run our Bing function to get the results list!
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list})

class MyRegistrationView(RegistrationView): 
    def get_success_url(self, user):
        return reverse('rango:register_profile')
    
@login_required
def register_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            # Ensure we associate the profile with the current user
            user_profile = profile_form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('rango:index')
        else:
            print(profile_form.errors)
    context_dict = {'form': profile_form}
    return render(request, 'rango/profile_registration.html', context=context_dict)

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist: 
            return None
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
        'picture': user_profile.picture}) 
        return (user, user_profile, form)

    @method_decorator(login_required) 
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        context_dict = {'user_profile': user_profile, 'selected_user': user, 'form': form}
        return render(request, 'rango/profile.html', context_dict)
    
    @method_decorator(login_required) 
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else: 
            print(form.errors)
        
        context_dict = {'user_profile': user_profile, 'selected_user': user, 'form': form}
        return render(request, 'rango/profile.html', context_dict)

def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('rango:profile') 
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'rango/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})

class ListProfilesView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request, 'rango/list_profiles.html', {'userprofile_list': profiles})
    
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

def goto_url(request):
    page_id = request.GET.get('page_id')
    if page_id:
        try:
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            return redirect(page.url)
        except Page.DoesNotExist:
            # If no Page is found, redirect to the homepage
            return HttpResponseRedirect(reverse('rango:index'))
    else:
        # If page_id is not provided, also redirect to the homepage
        return HttpResponseRedirect(reverse('rango:index'))

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1')) 
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    
    #if it's been more than a day since last visit 
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie 
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


#@login_required
#def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

#def register(request):
    #indicates whether reg was succesful
    registered = False
    #if it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        #attempt to grab info from raw info, make use of both UserForm & UserProfileForm 
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        #if the two forms are valide 
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            #setting the user attributes ourselves so set commit=False, avoids integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user
            #handle profile pics
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})

#def user_login(request):
    if request.method == 'POST':
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>'] # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the # blank dictionary object...
        return render(request, 'rango/login.html')
