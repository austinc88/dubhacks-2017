# Django
from django.shortcuts import render, render_to_response
from django.contrib.auth import logout
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.db import models

# Django REST Framework
from rest_framework import viewsets, mixins

# Scripts
from scripts.facebook import *

# Python
import oauth2 as oauth
import simplejson as json
import requests
import os
import os.path

# Models
from hackathon.models import *
from hackathon.serializers import SnippetSerializer
from hackathon.forms import UserForm
from hackathon.forms import DocumentForm


profile_track = None
getFacebook = FacebookOauthClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)

def index(request):
    print "index: " + str(request.user)

    if not request.user.is_active:
        if request.GET.items():
            if profile_track == 'facebook':
                code = request.GET['code']
                getFacebook.get_access_token(code)
                userInfo = getFacebook.get_user_info()
                username = userInfo['first_name'] + userInfo['last_name']

                try:
                    user = User.objects.get(username=username+'_facebook')
                except User.DoesNotExist:
                    new_user = User.objects.create_user(username+'_facebook', username+'@madewithfacbook', 'password')
                    new_user.save()
                    try:
                        profile = FacebookProfile.objects.get(user=new_user.id)
                        profile.access_token = getFacebook.access_token
                    except:
                        profile = FacebookProfile()
                        profile.user = new_user
                        profile.fb_user_id = userInfo['id']
                        profile.profile_url = userInfo['link']
                        profile.access_token = getFacebook.access_token
                    profile.save()
                user = authenticate(username=username+'_facebook', password='password')
                login(request, user)
    context = {'hello': 'world'}
    return render(request, 'hackathon/index.html', context)


##################
#  API Examples  #
##################

def api_examples(request):
    context = {'title': 'API Examples Page'}
    return render(request, 'hackathon/api_examples.html', context)

#################
#  FACEBOOK API #
#################

def facebook(request):
    '''
    This is an example of getting basic user info and display it
    '''
    userInfo = getFacebook.get_user_info()
    return render(request, 'hackathon/facebookAPIExample.html', { 'userInfo' : userInfo})


#########################
# Snippet RESTful Model #
#########################

class CRUDBaseView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass

class SnippetView(CRUDBaseView):
    serializer_class = SnippetSerializer
    queryset = Snippet.objects.all()


######################
# Registration Views #
######################

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
            return HttpResponseRedirect('/hackathon/login/')
        else:
            print user_form.errors
    else:
        user_form = UserForm()


    return render(request,
            'hackathon/register.html',
            {'user_form': user_form, 'registered': registered} )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/hackathon/api/')
            else:
                return HttpResponse("Your Django Hackathon account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'hackathon/login.html', {})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/hackathon/login/')

def facebook_login(request):
    global profile_track
    profile_track = 'facebook'
    facebook_url = getFacebook.get_authorize_url()
    return HttpResponseRedirect(facebook_url)

#Database

def list(request):
    # Handle file upload
    data = {}
    if request.method == 'POST':
        if request.POST.get('Delete'):
            for obj in Document.objects.all():
                if os.path.exists(obj.docfile.path):
                    os.remove(obj.docfile.path)
                obj.delete()

        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()
            docNames = newdoc.docfile.name.split("/")
            filename = docNames[1]
            data = getImageTags(filename)
            returnData = []
            for d in data :
                returnObj = {'ingredients' : d, 'calories' : data[d]}
                returnData.append(returnObj)
            print(data)
            documents = Document.objects.all()
            return render_to_response(
                'hackathon/list.html',
                {'documents': documents, 'form': form, 'data': returnData},
                context_instance=RequestContext(request)
            )
            # Redirect to the document list after POST
            #call the clarifai api from here
            #return HttpResponseRedirect(reverse('hackathon.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'hackathon/list.html',
        {'documents': documents, 'form': form, 'data': data},
        context_instance=RequestContext(request)
    )

################
# CLARIFAI API #
################
@csrf_exempt
def image(request):
    print("received response")
    name = request.GET.get('name')
    return getImageTags(name)

@csrf_exempt
def getImageTags(name):
    returnData = {}
    try :
        url =  "https://api.clarifai.com/v1/tag/?model=food-items-v1.0"
        headers = {'Authorization' : 'Bearer aA1P5zUg5sjHdQkVETcBZWnbkWApa3'}
        image = {'encoded_data' : open('hackathon/media/uploads/' + name, 'rb')}
        response = requests.post(url, headers=headers, files=image)
        response = json.loads(json.dumps(response.json()))
        print(response)
        data = response['results'][0]['result']['tag']
        for ingredient, prob in zip(data['classes'], data['probs']):
            print(ingredient)
            print(prob)
            if prob > 0.5:
                #look for calories in the db with this key
                print("we are adding this ingredient: " + ingredient)
                print(Ingredients.objects.all())
                print(Ingredients.objects.filter(ingredient=ingredient))
                matchingIngredients = Ingredients.objects.filter(ingredient=ingredient)
                if len(matchingIngredients) > 0 :
                    print(matchingIngredients.values())
                    returnData[ingredient] = matchingIngredients.values()[0]['calories']

        print(returnData)
        return returnData
    except:
        print("image name cannot be found")
        return None

@csrf_exempt
def ingredient(request):
    ingredient = request.GET.get('ingredient')
    print(ingredient)
    try :
        calorieCount = Ingredients.objects.filter(ingredient = ingredient).values('calories')
        print(calorieCount)
      #  for wat in calorieCount:
       #     return HttpResponse(calorieCount[wat])

        # print(calorieCount['calories'])
        return HttpResponse(json.dumps(calorieCount[0]))
    except:
        return HttpResponse({})
