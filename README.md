# studies_django_drf_tutorial

Django Rest Framework (DRF) tutorials

Quickstart: https://www.django-rest-framework.org/tutorial/quickstart/  
Snippets: https://www.django-rest-framework.org/tutorial/1-serialization/

## Django Rest Framework (DRF) Concepts

For Django configuration, project installation and other prerequisite knowledge, refer to https://github.com/jobsonita/studies_django_w3tutorial

### Serializers

[Serializers](https://www.django-rest-framework.org/api-guide/serializers/) do the job of presenting our models in the right way to our renderers and validating received data so that it matches our models. It can restrict which fields are shown, and also add more rules to be checked before accepting the received data.

```python
# models.py
from django.db import models

class Mymodel(models.Model):
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

# serializers.py
from rest_framework import serializers
from . import models

class MymodelSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    content = serializers.CharField(style={'base_template': 'textarea.html'})

    def create(self, validated_data):
        """
        Create and return a new `Mymodel` instance, given the validated data.
        """
        return models.Mymodel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Mymodel` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
```

#### ModelSerializer

We can greatly simplify our work by extending from the ModelSerializer which takes the base model and automatically configures serialization and deserialization. Our work is reduced to indicating which fields should be presented by that serializer:

```python
# models.py
from django.db import models

class Mymodel(models.Model):
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

# serializers.py
from rest_framework import serializers
from . import models

class MymodelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mymodel
        fields = ['id', 'title', 'content']
```

#### HyperlinkedModelSerializer

This serializer presents a `url` field instead of an `id` one, allowing for quickly navigating through our models. Relationships should use `HyperlinkedRelatedField` instead of `PrimaryKeyRelatedField`. The code below is based on the [Relationships](#relationships) section further down.

```python
# models.py
from django.db import models

class Mymodel(models.Model):
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        'auth.User', related_name='mymodels', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from . import models

class MymodelSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = models.Mymodel
        fields = ['url', 'id', 'title', 'content', 'owner']

class UserSerializer(serializers.HyperlinkedModelSerializer):
    mymodels = serializers.HyperlinkedRelatedField(
        many=True, view_name='mymodel-detail', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'mymodels']
```

For more in-depth information on serializers, read https://www.django-rest-framework.org/api-guide/serializers/

### Views

In this tutorial, we see a gradual evolution from regular Django views to DRF ones.

#### Regular Django views

```python
# views.py
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser

from . import models, serializers

def mymodel_list(request):
    """
    List all mymodels, or create a new mymodel.
    """
    if request.method == 'GET':
        instances = models.Mymodel.objects.all()
        serializer = serializers.MymodelSerializer(instances, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = serializers.MymodelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def mymodel_detail(request, pk):
    """
    Retrieve, update or delete a mymodel.
    """
    try:
        instance = models.Mymodel.objects.get(pk=pk)
    except models.Mymodel.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = serializers.MymodelSerializer(instance)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = serializers.MymodelSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        instance.delete()
        return HttpResponse(status=204)

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('mymodels/', views.mymodel_list),
    path('mymodels/<int:pk>/', views.mymodel_detail),
]
```

#### Requests, Responses, status codes, decorators

DRF introduces a `Request` object that extends from regular `HttpRequest` and has a `request.data` attribute with extended functionality over `request.POST`.

It also introduces a `Response` object, of type `TemplateResponse`, that automatically handles content negotiation for us.

It also offers a `status` module with user friendly status code literals, such as `HTTP_400_BAD_REQUEST`.

Lastly, it introduces an `@api_view` decorator for function based views and an `APIView` base class for class-based views, which make sure we receive Request objects and return Response objects, and handling `405 Method Not Allowed` and `ParseError` exceptions for us.

When we put all above together, we get the next section:

#### DRF "regular" views

```python
# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models, serializers

@api_view(['GET', 'POST'])
def mymodel_list(request):
    """
    List all mymodels, or create a new mymodel.
    """
    if request.method == 'GET':
        instances = models.Mymodel.objects.all()
        serializer = serializers.MymodelSerializer(instances, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = serializers.MymodelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def mymodel_detail(request, pk):
    """
    Retrieve, update or delete a mymodel.
    """
    try:
        instance = models.Mymodel.objects.get(pk=pk)
    except models.Mymodel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = serializers.MymodelSerializer(instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = serializers.MymodelSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# urls.py: NO CHANGE
```

#### Accepting format suffix in our URLs

We can allow format suffixes such as the `.json` part in `https://example.com/api/items/4.json` by using the `format_suffix_patterns` function of `rest_framework.urlpatterns` to transform our urlpatterns:

```python
# urls.py
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('mymodels/', views.mymodel_list),
    path('mymodels/<int:pk>/', views.mymodel_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)
```

In that case, we also need to add a `format` argument to our views:

```python

@api_view(['GET', 'POST'])
def mymodel_list(request, format=None):
...

@api_view(['GET', 'PUT', 'DELETE'])
def mymodel_detail(request, pk, format=None):
```

#### Class-based Views

```python
# views.py
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers

class MymodelList(APIView):
    """
    List all mymodels, or create a new mymodel.
    """
    def get(self, request, format=None):
        instances = models.Mymodel.objects.all()
        serializer = serializers.MymodelSerializer(instances, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = serializers.MymodelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MymodelDetail(APIView):
    """
    Retrieve, update or delete a mymodel.
    """
    def get_object(self, pk):
        try:
            return models.Mymodel.objects.get(pk=pk)
        except models.Mymodel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        instance = self.get_object(pk)
        serializer = serializers.MymodelSerializer(instance)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        instance = self.get_object(pk)
        serializer = serializers.MymodelSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        instance = self.get_object(pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# urls.py
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('mymodels/', views.MymodelList.as_view()),
    path('mymodels/<int:pk>/', views.MymodelDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
```

#### Using Mixins

In general, the usual operations (list + CRUD: create, retrieve, update, delete) are pretty similar for any model-backed API views we create. DRF provides mixins that implement those operations for us, so all we need to do is call them on each http method we want to implement:

```python
# views.py
from rest_framework import mixins, generics

from . import models, serializers

class MymodelList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all mymodels, or create a new mymodel.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class MymodelDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView):
    """
    Retrieve, update or delete a mymodel.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# urls.py: NO CHANGE
```

#### Generic class-based views

DRF provides already mixed-in generic views to reduce our code even more:

```python
# views.py
from rest_framework import generics

from . import models, serializers

class MymodelList(generics.ListCreateAPIView):
    """
    List all mymodels, or create a new mymodel.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

class MymodelDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a mymodel.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

# urls.py: NO CHANGE
```

#### ViewSets and Routers

Unlike `Views` which work with http methods (such as get and put), `ViewSets` provide operations such as `retrieve` and `update` and its methods are only bound when instantiated into sets of views, tipically when a `Router` is handling the url configuration. The code below is a sequence to the [Relationships](#relationships) and [Permissions](#permissions) sections further down, but is presented first due to being related to the Views section.

```python
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from . import permissions as myapp_permissions
from . import serializers

class MymodelViewSet(viewsets.ModelViewSet):
     """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `show_property` action.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer
    [permission_classes] = [
        permissions.IsAuthenticatedOrReadOnly,
        myapp_permissions.IsOwnerOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def show_property(self, request, *args, **kwargs):
        mymodel = self.get_object()
        return Response(mymodel.property)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

# urls.py
from django.urls import path
from rest_framework import renderers
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

mymodel_list = MymodelViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
mymodel_detail = MymodelViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
mymodel_highlight = MymodelViewSet.as_view({
    'get': 'show_property'
}, renderer_classes=[renderers.StaticHTMLRenderer])
user_list = UserViewSet.as_view({
    'get': 'list'
})
user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    path('mymodels/', mymodel_list, name='mymodel-list'),
    path('mymodels/<int:pk>/', mymodel_detail, name='mymodel-detail'),
    path('mymodels/<int:pk>/highlight', mymodel_highlight, name='mymodel-highlight'),
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
```

##### Using Routers

When using `ViewSet` classes, we can use a `Router` to handle url configurations automatically. A `DefaultRouter` also provides an API root view.

```python
from django.urls import include, path
from rest_framework import routers
from . import views

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register('mymodels', views.MymodelViewSet)
router.register('users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
```

### Relationships

Example of associating a model to the `auth.User` model (and back through the `related_name` field).

```python
# models.py
from django.db import models

class Mymodel(models.Model):
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        'auth.User', related_name='mymodels', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from . import models

class MymodelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = models.Mymodel
        fields = ['id', 'title', 'content', 'owner']

class UserSerializer(serializers.ModelSerializer):
    mymodels = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'mymodels']

# views.py
from django.contrib.auth.models import User
from rest_framework import generics

from . import models, serializers

class MymodelList(generics.ListCreateAPIView):
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MymodelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

# urls.py
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('mymodels/', views.MymodelList.as_view()),
    path('mymodels/<int:pk>/', views.MymodelDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
```

### Permissions

We can add a simple access control to our views by setting the `permission_classes` field to a list of permissions matching our access rules and providing endpoints to login/logout into our api. We can also have our own permission classes by extending the `BasePermission` class from `rest_framework.permissions`:

```python
# permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user

# views.py
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from . import models
from . import permissions as myapp_permissions
from . import serializers

class MymodelList(generics.ListCreateAPIView):
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MymodelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        myapp_permissions.IsOwnerOrReadOnly]
...

# urls.py
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('mymodels/', views.MymodelList.as_view()),
    path('mymodels/<int:pk>/', views.MymodelDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
```

## Common problems

### DRF generates localhost hyperlinks instead of Codespace ones

When using DRF's DefaultRouter to generate [HATEOAS](https://en.wikipedia.org/wiki/HATEOAS) REST links (navigable API), DRF generates localhost hyperlinks. In order to make it generate urls that match the Codespace url, we need to set the `USE_X_FORWARDED_HOST` flag to `True` in the project's `settings.py`. Also, since it will be considered a forwarded request, we need to configure `ALLOWED_HOSTS` to include the Codespace domain, or make it accept any domain by using the `"*"` wildcard.

```python
# settings.py

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    USE_X_FORWARDED_HOST = True
else:
    # When in production, configure ALLOWED_HOSTS to accept requests forwarded from the domain where your website is hosted
    ALLOWED_HOSTS = []
```
