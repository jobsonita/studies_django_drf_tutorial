# studies_django_drf_tutorial

Django Rest Framework (DRF) tutorials

Quickstart: https://www.django-rest-framework.org/tutorial/quickstart/  
Snippets: https://www.django-rest-framework.org/tutorial/1-serialization/

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
