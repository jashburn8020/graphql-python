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
  - the query just inherits the query defined in [`links/schema.py`](hackernews/links/schema.py)
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

- Add mutation code to [`links/schema.py`](hackernews/links/schema.py):
- Add `Mutation` to [`hackernews/schema.py`](hackernews/hackernews/schema.py)
- Create a link in GraphiQL:

```
mutation {
  createLink(
    url: "https://github.com",
    description: "Lots of Code!"
  ) {
    id
    url
    description
  }
}
```

# Authentication

## Creating a User

- Create a new folder under `hackernews` called `users` and a new file called [`schema.py`](hackernews/users/schema.py)
- Put the new mutation in the root schema file, [`hackernews/schema.py`](hackernews/hackernews/schema.py)
- Create the user in GraphiQL:

```
mutation {
  createUser(username: "asdf", email: "asdf@qwerty.com", password: "123") {
    user {
      id
      username
      email
    }
  }
}
```

## Querying the Users

- Create a query for listing all users in [`users/schema.py`](hackernews/users/schema.py)
- Enable the users query in the root schema file, [`hackernews/schema.py`](hackernews/hackernews/schema.py)
- Query users in GraphiQL:

```
query {
  users {
    id
    username
    email
  }
}
```

## User Authentication

- Stateless authentication using django-graphql-jwt library to implement JWT Tokens in Graphene
  - when a User signs up or logs in, a token will be returned
    - a piece of data that identifies the User
  - this token must be sent by the User in the HTTP Authorization header with every request when authentication is needed

## Configuring django-graphql-jwt

- In the [`hackernews/settings.py`](hackernews/hackernews/settings.py) file, under the `GRAPHENE` variable, add the following `MIDDLEWARE` line:

```
GRAPHENE = {
    "SCHEMA": "hackernews.schema.schema",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware",],
}
```

- Add the `AUTHENTICATION_BACKENDS` setting:

```
AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

- Update [`hackernews/schema.py`](hackernews/hackernews/schema.py):

```
import graphql_jwt
...

class Mutation(users.schema.Mutation, links.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
```

- `tokenAuth` is used to authenticate the User with its username and password to obtain the JSON Web token:

```
mutation {
  tokenAuth(username: "asdf", password: "123") {
    token
  }
}
```

- Example `tokenAuth` response:

```
{
  "data": {
    "tokenAuth": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFzZGYiLCJleHAiOjE1ODUxODE1MDIsIm9yaWdJYXQiOjE1ODUxODEyMDJ9.J5MlC3W27MPH2ZEWK5jXW-A1wVMQ8_9g04qhBBPuCx0"
    }
  }
}
```

- `verifyToken` to confirm that the token is valid, passing it as an argument:

```
mutation {
  verifyToken(token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFzZGYiLCJleHAiOjE1ODUxODE1MDIsIm9yaWdJYXQiOjE1ODUxODEyMDJ9.J5MlC3W27MPH2ZEWK5jXW-A1wVMQ8_9g04qhBBPuCx0") {
    payload
  }
}
```

- Example `verifyToken` response:

```
{
  "data": {
    "verifyToken": {
      "payload": {
        "username": "asdf",
        "exp": 1585181502,
        "origIat": 1585181202
      }
    }
  }
}
```

- `refreshToken` to obtain a new token within the renewed expiration time for non-expired tokens, if they are enabled to expire:

```
mutation {
  refreshToken(token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFzZGYiLCJleHAiOjE1ODUxODE1MDIsIm9yaWdJYXQiOjE1ODUxODEyMDJ9.J5MlC3W27MPH2ZEWK5jXW-A1wVMQ8_9g04qhBBPuCx0") {
    token
    payload
  }
}
```

- Example `refreshToken` response:

```
{
  "data": {
    "refreshToken": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFzZGYiLCJleHAiOjE1ODUxODE5NjgsIm9yaWdJYXQiOjE1ODUxODEyMDJ9.nhyhnTijPJkwG479JHMoswlffUVNODAHtski4TheRy0",
      "payload": {
        "username": "asdf",
        "exp": 1585181968,
        "origIat": 1585181202
      }
    }
  }
}
```

- See: <https://github.com/flavors/django-graphql-jwt>

## Testing the Authentication

- To test if our authentication is working, add the `me` Query in the [`users/schema.py`](hackernews/users/schema.py) file within the `Query` class
- Make the `me` query with the following header:
  - `Authorization`: `JWT <token from tokenAuth response>`

```
query {
    me {
        id
        username
    }
}
```

# Links and Voting

## Attaching Users to Links

- Integrate the Links and Users models
  - add the `posted_by` field to the `Link` class in [`links/models.py`](hackernews/links/models.py)
- Run the Django commands to reflect the changes in the database:

```
python manage.py makemigrations
python manage.py migrate
```

- In [`links/schema.py`](hackernews/links/schema.py), in the `CreateLink` mutation, return the User in the `posted_by` field
- To test it, send a mutation to the server along with the JWT token

```
mutation {
    createLink(url: "http://test.com", description: "testy") {
        id
        url
        description
        postedBy {
            id
            username
            email
        }
    }
}
```

- Example response:

```
{
    "data": {
        "createLink": {
            "id": 4,
            "url": "http://test.com",
            "description": "testy",
            "postedBy": {
                "id": "1",
                "username": "asdf",
                "email": "asdf@qwerty.com"
            }
        }
    }
}
```

## Adding Votes

# Sources

- "GraphQL-Python Tutorial." <https://www.howtographql.com/graphql-python/1-getting-started/>.
