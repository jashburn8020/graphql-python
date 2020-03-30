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

- Add the Vote model in [`links/models.py`](hackernews/links/models.py)
- Reflect the changes in the database

```
python manage.py makemigrations
python manage.py migrate
```

- Add a new mutation, `CreateVote`, for voting in [`links/schema.py`](hackernews/links/schema.py)
- Vote for a link:

```
mutation {
  createVote(linkId: 4) {
    user {
      id
      username
      email
    }
    link {
      id
      url
    }
  }
}
```

## Relating Links and Votes

- To get a list of all the votes and a list of votes from each link
- Add the `VoteType`, `votes` field, and a `resolve_votes` method to [`links/schema.py`](hackernews/links/schema.py) to get all votes
- Query for all the votes

```
query {
  votes {
    id
    user {
      id
      username
    }
    link {
      id
      url
    }
  }
}
```

- Query for all the links

```
query {
  links {
    id
    url
    votes {
      id
      user {
        id
        username
      }
    }
  }
}
```

# Error Handling

## Schema Errors

- All the fields from queries and mutations have a strong type, so requesting and inputting wrong data will generate an error
- Example:

```
query {
  links {
    id
    cheese
  }
}
```

- Response (status 400):

```
{
  "errors": [
    {
      "message": "Cannot query field \"cheese\" on type \"LinkType\".",
      "locations": [
        {
          "line": 4,
          "column": 5
        }
      ]
    }
  ]
}
```

## Graphene Errors

- On the application level, you can use the `GraphQLError` class or Python exceptions
- See [`links/schema.py`](hackernews/links/schema.py)
  - both give similar response

# Filtering

## Filtering Links

- Pass an argument to the `links` field, used by the resolver to filter the results
  - concept is the same as mutations
- In [`links/schema.py`](hackernews/links/schema.py):

```
class Query(graphene.ObjectType):
    # Search parameter inside our links field
    links = graphene.List(LinkType, search=graphene.String())
    ...

    def resolve_links(self, info, search=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        if search:
            links_filter = Q(url__icontains=search) | Q(description__icontains=search)
            return Link.objects.filter(links_filter)

        return Link.objects.all()

    ...
```

- Search query

```
query {
  links(search: "jonatas") {
    id
    url
    description
  }
}
```

# Pagination

- The simple way defined in the GraphQL pagination documentation is to slice the results using two parameters:
  - `first`: returns the first _n_ items
  - `skip`: skips the first _n_ items
- See <https://graphql.org/learn/pagination/>
- Add `first` and `skip` parameter support to `Query` in [`links/schema.py`](hackernews/links/schema.py)
- Pagination query

```
query {
  links(first: 2, skip: 1) {
    id
    description
    url
  }
}
```

# Relay

- Relay is a Javascript framework built by Facebook with the purpose of improving the GraphQL architecture by making some core assumptions:
  - a mechanism for refetching an object
    - gives every object a global unique identifier
  - a description of how to page through connections
    - creates a cursor-based pagination structure
  - structure around mutations to make them predictable
    - introduces the input parameter to mutations
- See:
  - <https://facebook.github.io/relay/docs/en/graphql-server-specification.html>
  - <http://docs.graphene-python.org/projects/django/en/latest/tutorial-relay/>
- Graphene and Graphene Django already comes with the Relay implementation

## Using Relay on Links

- Create a new file [`links/schema_relay.py`](hackernews/links/schema_relay.py)
  - _Relay_ prefix to avoid confusion - not really needed
- Add the new query to the root schema file, [`hackernews/schema.py`](hackernews/hackernews/schema.py)
- Relay query for a link:

```
query {
  relayLink(id: "TGlua05vZGU6Mg==") {
    id
    url
    description
  }
}
```

- Relay query for links:

```
query {
  relayLinks {
    edges {
      node {
        id
        url
        description
        votes {
          edges {
            node {
              id
              user {
                id
                username
              }
            }
          }
        }
      }
    }
  }
}
```

- Edges: represents a collection, which has pagination properties
- Nodes: the final object or and edge for a new list of objects
- Relay query with pagination - `before`, `after`, `first`, `last`
  - each edge has a `pageInfo` object, including cursor for navigating between pages

```
query {
  relayLinks(first: 2) {
    edges {
      node {
        id
        url
        description
      }
    }
    pageInfo {
      hasPreviousPage
      hasNextPage
      startCursor
      endCursor
    }
  }
}
```

- Response:

```
{
  "data": {
    "relayLinks": {
      "edges": [
        {
          "node": {
            "id": "TGlua05vZGU6MQ==",
            "url": "https://www.howtographql.com/",
            "description": "The Fullstack Tutorial for GraphQL"
          }
        },
        {
          "node": {
            "id": "TGlua05vZGU6Mg==",
            "url": "https://twitter.com/jonatasbaldin/",
            "description": "The Jonatas Baldin Twitter"
          }
        }
      ],
      "pageInfo": {
        "hasPreviousPage": false,
        "hasNextPage": true,
        "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        "endCursor": "YXJyYXljb25uZWN0aW9uOjE="
      }
    }
  }
}
```

- Relay query with pagination using cursor:

```
query {
  relayLinks(first: 1, before: "YXJyYXljb25uZWN0aW9uOjE=") {
    edges {
      node {
        id
        url
        description
      }
    }
    pageInfo {
      hasPreviousPage
      hasNextPage
      startCursor
      endCursor
    }
  }
}
```

- Response:

```
{
  "data": {
    "relayLinks": {
      "edges": [
        {
          "node": {
            "id": "TGlua05vZGU6MQ==",
            "url": "https://www.howtographql.com/",
            "description": "The Fullstack Tutorial for GraphQL"
          }
        }
      ],
      "pageInfo": {
        "hasPreviousPage": false,
        "hasNextPage": false,
        "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        "endCursor": "YXJyYXljb25uZWN0aW9uOjA="
      }
    }
  }
}
```

## Relay and Mutations

- Add mutation code to [`links/schema_relay.py`](hackernews/links/schema_relay.py)
- Add the new mutation to the root schema file, [`hackernews/schema.py`](hackernews/hackernews/schema.py)
- Relay mutation to create a link:

```
mutation {
  relayCreateLink(input: {
    url: "http://deployeveryday.com",
    description: "Author's Blog"
  }) {
    link {
      id
      url
      description
    }
  }
}
```

- The `input` argument accepts the defined `url` and `description` arguments as a dictionary

# Sources

- "graphql-python Getting Started." <https://www.howtographql.com/graphql-python/1-getting-started/>.
- "graphql-python Queries." <https://www.howtographql.com/graphql-python/2-queries/>.
- "graphql-python Mutations." <https://www.howtographql.com/graphql-python/3-mutations/>
- "graphql-python Authentication." <https://www.howtographql.com/graphql-python/4-authentication/>
- "graphql-python Links and Voting." <https://www.howtographql.com/graphql-python/5-links-and-voting/>
- "graphql-python Error Handling." <https://www.howtographql.com/graphql-python/6-error-handling/>.
- "graphql-python Filtering." <https://www.howtographql.com/graphql-python/7-filtering/>.
- "graphql-python Pagination." <https://www.howtographql.com/graphql-python/8-pagination/>.
- "graphql-python Relay." <https://www.howtographql.com/graphql-python/9-relay/>.
