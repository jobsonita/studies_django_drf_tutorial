[Read this file in English](../../README.md)

# studies_django_drf_tutorial

Tutoriais de Django Rest Framework (DRF)

Quickstart: https://www.django-rest-framework.org/tutorial/quickstart/  
Snippets: https://www.django-rest-framework.org/tutorial/1-serialization/

## Conceitos de Django Rest Framework (DRF)

Para conhecimentos sobre configuração do Django, instalação do projeto e outros pré-requisitos, consulte https://github.com/jobsonita/studies_django_w3tutorial

### Serializers (Serializadores)

[Serializadores](https://www.django-rest-framework.org/api-guide/serializers/) trabalham na representação correta dos nossos modelos para a exibição externa, e na validação dos dados recebidos de tal forma que correspondam aos nossos modelos. Eles podem ocultar campos a serem exibidos ou adicionar mais regras a serem checadas antes de aceitar os dados recebidos.

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
        Cria e retorna uma nova instância de `Mymodel` com os dados validados.
        """
        return models.Mymodel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Altera e retorna uma instância existente de `Mymodel` com os dados validados.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
```

#### ModelSerializer (Serializador de Modelo)

Podemos simplificar nosso trabalho ao partir de um ModelSerializer que recebe o modelo base e configura automaticamente a serialização e deserialização. Nosso trabalho então se resume a indicar quais campos são abrangidos pelo serializador:

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

#### HyperlinkedModelSerializer (Serializador de Modelo Hiperligado)

Este serializador exibe um campo `url` em vez de um `id`, permitindo a navegação rápida entre modelos. Relacionamentos devem usar `HyperlinkedRelatedField` ao invés de `PrimaryKeyRelatedField`. O código abaixo se baseia na seção [Relacionamentos](#relacionamentos) mais adiante.

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

Para informações mais aprofundadas sobre serializadores, consulte https://www.django-rest-framework.org/api-guide/serializers/

### Views (Visualização, Exibição)

Neste tutorial, vemos uma evolução gradativa de views comuns do Django para views especializadas do DRF.

#### Views comuns do Django

```python
# views.py
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser

from . import models, serializers

def mymodel_list(request):
    """
    Lista todos os mymodels, ou cria um novo.
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
    Obtém, atualiza ou exclui um mymodel.
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

DRF introduz um objeto `Request` (Requisição) que estende o `HttpRequest` comum do Django e que possui o atributo `request.data` com funcionalidades adicionais em comparação com o `request.POST` do Django.

Ele também introduz um objeto `Response` (Resposta), do tipo `TemplateResponse`, que gerencia a negociação de conteúdo automaticamente.

Ele também oferece um módulo `status` com constantes de fácil leitura, como `HTTP_400_BAD_REQUEST` (Falha na Requisição).

E por último, o DRF introduz um decorador `@api_view` para views baseadas em funções e uma classe base `APIView` para views baseadas em classes, que garantem o recebimento de objetos Request, retorno de objetos Response, e gerenciamento de exceções `405 Method Not Allowed` e `ParseError`.

Quando juntamos os pontos acima mencionados, obtemos a seção a seguir:

#### Views "comuns" do DRF

```python
# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models, serializers

@api_view(['GET', 'POST'])
def mymodel_list(request):
    """
    Lista todos os mymodels, ou cria um novo.
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
    Obtém, atualiza ou exclui um mymodel.
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

# urls.py: SEM ALTERAÇÕES
```

#### Aceitando sufixos de formato nas nossas URLs

Podemos permitir sufixos de formato como por exemplo o `.json` em `https://example.com/api/items/4.json` ao usarmos a função `format_suffix_patterns` de `rest_framework.urlpatterns` para transformar nossos urlpatterns:

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

Nesse caso, precisamos adicionar o argumento `format` às nossas views:

```python

@api_view(['GET', 'POST'])
def mymodel_list(request, format=None):
...

@api_view(['GET', 'PUT', 'DELETE'])
def mymodel_detail(request, pk, format=None):
```

#### Views baseadas em Classes

```python
# views.py
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers

class MymodelList(APIView):
    """
    Lista todos os mymodels, ou cria um novo.
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
    Obtém, atualiza ou exclui um mymodel.
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

#### Usando Mixins

Em geral, as operações usuais (list + CRUD: create, retrieve, update, delete) são bastante similares entre quaisquer views relativas a modelos. O DRF oferece mixins que já implementam essas operações, então só precisamos chamá-las nos respectivos métodos http que desejamos implementar:

```python
# views.py
from rest_framework import mixins, generics

from . import models, serializers

class MymodelList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Lista todos os mymodels, ou cria um novo.
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
    Obtém, atualiza ou exclui um mymodel.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# urls.py: SEM ALTERAÇÕES
```

#### Views genéricas baseadas em Classes

O DRF oferece views genéricas já mescladas para reduzir nosso trabalho ainda mais:

```python
# views.py
from rest_framework import generics

from . import models, serializers

class MymodelList(generics.ListCreateAPIView):
    """
    Lista todos os mymodels, ou cria um novo.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

class MymodelDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtém, atualiza ou exclui um mymodel.
    """
    queryset = models.Mymodel.objects.all()
    serializer_class = serializers.MymodelSerializer

# urls.py: SEM ALTERAÇÕES
```

#### ViewSets e Routers

Diferente das `Views` que trabalham com métodos http (como get e put), `ViewSets` (conjuntos de views) oferecem operações como `retrieve` e `update` e seus métodos só são casados quando instanciados em conjuntos de views, tipicamente quando um `Router` (Roteador) está tratando da configuração da url. O código abaixo é uma sequência das seções [Relacionamentos](#relacionamentos) and [Permissões](#permissoes) mais adiante, mas é apresentado primeiro por ser relacionado à seção de Views.

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
    Este conjunto de views exibe ações `list`, `create`, `retrieve`,
    `update` e `destroy` automáticas.

    Também disponibilizamos a ação adicional `show_property`.
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
    Este conjunto de views exibe ações `list` `retrieve`.
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

##### Usando Roteadores

Quando usamos classes `ViewSet`, podemos usar um `Router` para tratar das configurações de url automaticamente. Um `DefaultRouter` também disponibiliza uma view da raíz da API.

```python
from django.urls import include, path
from rest_framework import routers
from . import views

# Cria um roteador e registra nossos conjuntos de views nele.
router = routers.DefaultRouter()
router.register('mymodels', views.MymodelViewSet)
router.register('users', views.UserViewSet)

# As URLs da API são determinadas automaticamente pelo roteador.
urlpatterns = [
    path('', include(router.urls)),
]
```

### Relacionamentos

Exemplo de associação ao modelo `auth.User` (e de volta através do campo `related_name`).

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

### Permissões

Podemos adicionar um controle de acesso simplificado às nossas views ao configurar o campo `permission_classes` com uma lista das permissões adequada e oferecer caminhos de login/logout na nossa api. Também podemos estender nossas permissões a partir da classe `BasePermission` de `rest_framework.permissions`:

```python
# permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Esta permissão só deixa os donos alterarem seus objetos.
    """

    def has_object_permission(self, request, view, obj):
        # Operações de leitura são todas permitidas,
        # então sempre permitimos requisições GET, HEAD e OPTIONS.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Somente os donos têm permissão de escrita.
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

## Problemas comuns

### O DRF gera urls do localhost ao invés de urls do Codespace

Ao usar o DefaultRouter do DRF para gerar as urls de um REST [HATEOAS](https://en.wikipedia.org/wiki/HATEOAS) (API navegável), o DRF gera urls do localhost. Para que ele gere urls do Codespace, precisamos configuar a constante `USE_X_FORWARDED_HOST` como `True` nas configurações do projeto, `settings.py`. Além disso, como a requisição será considerada como encaminhada, precisamos incluir o domínio do Codespace em `ALLOWED_HOSTS`, ou fazê-lo aceitar qualquer domínio usando o caractere coringa `"*"`.

```python
# settings.py

# AVISO DE SEGURANÇA: em produção, não rode com DEBUG ativado!
DEBUG = env("DEBUG")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    USE_X_FORWARDED_HOST = True
else:
    # Em produção, configure ALLOWED_HOSTS para aceitar requisições encaminhadas do domínio onde seu projeto está hospedado
    ALLOWED_HOSTS = []
```
