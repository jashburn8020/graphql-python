# Getting Started

- See [Core Concepts](fundamentals.md)

## Installing Django and Graphene

```
pip install django graphene-django django-filter django-graphql-jwt
django-admin startproject hackernews
cd hackernews
python manage.py migrate
python manage.py runserver
```

## Configuring Graphene Django

- [`hackernews/settings.py`](hackernews/hackernews/settings.py):

```
INSTALLED_APPS = (
    # After the default packages
    'graphene_django',
)
...
# bottom of the file
GRAPHENE = {
    'SCHEMA': 'hackernews.schema.schema',
}

```

# Queries

- You will have two apps, one for Users and one for the Links

## Creating the Links app

```
python manage.py startapp links
```

- Define a Model – the layer between Django and the database
  - see [`links/models.py`](hackernews/links/models.py)
- Configure Django to use the new `links` app in the [`hackernews/settings.py`](hackernews/hackernews/settings.py) file:

```
INSTALLED_APPS = (
    # After the graphene_django app
    'links',
)
```

- Create the database tables:

```
python manage.py makemigrations
python manage.py migrate
```

- Enter the Django shell with the command `python manage.py shell` and create some links:

```
from links.models import Link
Link.objects.create(url='https://www.howtographql.com/', description='The Fullstack Tutorial for GraphQL')
Link.objects.create(url='https://twitter.com/jonatasbaldin/', description='The Jonatas Baldin Twitter')
```

## Creating your first Type and Schema

- Create the [`links/schema.py`](hackernews/links/schema.py) file
  - `LinkType` was created using the `DjangoObjectType`
    - a custom type available in Graphene Django
  - the special type query was created with a resolver for the field `links`, which returns all the links
- Create the [`hackernews/schema.py`](hackernews/hackernews/schema.py) file, with the query type
  - the query just inherits the query defined in [`links/schema.py`](links/schema.py)
    - this way, you are able to keep every part of the schema isolated in the apps

## Introducing GraphiQL

- Note that you need to disable the Django CSRF protection
- See [`hackernews/urls.py`](hackernews/hackernews/urls.py)
- Open your browser and access <http://localhost:8000/graphql/>
  - create your first query

```
query {
  links {
    id
    description
    url
  }
}
```

# Mutations

# Sources

- "GraphQL-Python Tutorial." <https://www.howtographql.com/graphql-python/1-getting-started/>.
