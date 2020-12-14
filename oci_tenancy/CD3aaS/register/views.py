import simplejson as json
import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, FormView
from . import IdcsClient

# Custom functions
# Function used to load the configurations from the config.json file
def getOptions():
    # print(os.getcwd())
    file_path = os.path.join(settings.BASE_DIR, 'register', 'config.json')
    # readjson = open(os.getcwd() + "/register/config.json", "r") #os.getcwd() + "/register/config.json"
    config = open(file_path, 'r').read()
    options = json.loads(config)
    return options


# Create your views here.
class Cd3welcome(TemplateView):
    template_name = 'register/cd3login.html'


class Cd3login(View):
    def get(self, request):
        options = getOptions()
        am = IdcsClient.AuthenticationManager(options)
        url = am.getAuthorizationCodeUrl(options["redirectURL"], options["scope"], "1234", "code")
        return HttpResponseRedirect(url)


# Definition of the /callback route
class Callback(FormView):
    def get(self, request):
        # print("----------------- def callback(request) ---------------")
        code = request.GET.get('code')
        # print(code)
        # Authentication Manager loaded with the configurations.
        am = IdcsClient.AuthenticationManager(getOptions())
        # Using the Authentication Manager to exchange the Authorization Code to an Access Token.
        ar = am.authorizationCode(code)
        # Get the access token as a variable
        access_token = ar.getAccessToken()
        id_token = ar.getIdToken()

        # print("--------")
        # print("access_token = %s" % (access_token))

        # Validating id token to acquire information such as UserID, DisplayName, list of groups and AppRoles assigned to the user
        id_token_verified = am.verifyIdToken(id_token)

        displayname = id_token_verified.getDisplayName()
        # The application then adds these information to the User Session.
        request.session['access_token'] = access_token
        request.session['id_token'] = id_token
        request.session['displayname'] = displayname

        # Rendering the home page and adding displayname to be printed in the page.
        return render(request, 'register/cd3db.html', {'displayname': displayname})

# Definition of the /logout route
class Cd3logout(View):
    def get(self, request):
        # print("----------------- def logout(request) ---------------")
        # Getting the Access Token value from the session
        access_token = request.session.get('access_token', 'none')
        if access_token == 'none':
            # If the access token isn't present redirects to login page.
            return render(request, 'register/cd3login.html')
        else:
            options = getOptions()
            url = options["BaseUrl"]
            url += options["logoutSufix"]
            url += '?post_logout_redirect_uri=http%3A//localhost%3A8000&id_token_hint='
            url += request.session.get('id_token', 'none')
            url = options["BaseUrl"] +"cloudgate/v1/oauth2/logout"
            # Clear session attributes
            del request.session['access_token']
            del request.session['id_token']
            del request.session['displayname']
            # Redirect to Oracle Identity Cloud Service logout URL.
            return HttpResponseRedirect(url)


# Definition of the /home route
class Cd3home(View):
    def get(self, request):
        # print("----------------- def home(request) ---------------")
        access_token = request.session.get('access_token', 'none')
        if access_token == 'none':
            return render(request, 'register/cd3login.html')
        else:
            displayname = request.session.get('displayname', 'displayname')
            return render(request, 'register/cd3db.html', {'displayname': displayname})
