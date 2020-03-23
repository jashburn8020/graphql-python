# Core Concepts

## The Schema Definition Language (SDL)

- GraphQL has its own type system that's used to define the schema of an API
- Syntax for writing schemas is called Schema Definition Language (SDL)
- Example of a simple type called `Person`:

```
type Person {
  name: String!
  age: Int!
}
```

- Fields
  - `name`: type `String`
  - `age`: type `Int`
  - `!`: field is required
- Relationship between types

```
type Post {
  title: String!
  author: Person!
}

type Person {
  id: ID!
  name: String!
  age: Int!
  posts: [Post!]!
}
```

- One-to-many-relationship between `Person` and `Post`
  - `posts` field is an array of posts

## Fetching Data with Queries

- GraphQL APIs typically only expose a single endpoint
- Structure of data that's returned is not fixed
  - lets the client decide what data is actually needed

### Basic Queries

- Example query:

```
{
  allPersons {
    name
  }
}
```

- `allPersons` field is called the _root field_ of the query
- Everything that follows the root field is called the _payload_ of the query
- Example response:

```
{
  "allPersons": [
    { "name": "Johnny" },
    { "name": "Sarah" },
    { "name": "Alice" }
  ]
}
```

- If the client also needed the persons' `age`, include the new field in the query's payload
- Example to load all the `posts` that a `Person` has written:

```
{
  allPersons {
    name
    age
    posts {
      title
    }
  }
}
```

### Queries with Arguments

- Each field can have zero or more arguments if that's specified in the schema
- For example, the `allPersons` field could have a `last` parameter to only return up to a specific number of persons

```
{
  allPersons(last: 2) {
    name
  }
}
```

## Writing Data with Mutations

- Changes are made using _mutations_ to
  - create new data
  - update existing data
  - delete existing data
- Mutations follow the same syntactical structure as queries, but they always need to start with the `mutation` keyword
- Example to create a new `Person`:

```
mutation {
  createPerson(name: "Bob", age: 36) {
    id
  }
}
```

- Mutation also has a root field - `createPerson`
- Can specify a payload for a mutation to ask for different properties of the new `Person` object - `id`
  - being able to also query information when sending mutations allows you to retrieve new information from the server in a single roundtrip

## Realtime Updates with Subscriptions

- _Subscriptions_
  - when a client subscribes to an event, it will initiate and hold a steady connection to the server
  - whenever that particular event then actually happens, the server pushes the corresponding data to the client

```
subscription {
  newPerson {
    name
    age
  }
}
```

- Whenever a new mutation is performed that creates a new `Person`, the server sends the information about this person over to the client:

```
{
  "newPerson": {
    "name": "Jane",
    "age": 23
  }
}
```

## Defining a Schema

- The schema
  - specifies the capabilities of the API
  - defines how clients can request the data
  - often seen as a contract between the server and client
  - is a collection of GraphQL types
- Special _root_ types:

```
type Query { ... }
type Mutation { ... }
type Subscription { ... }
```

- `Query`, `Mutation`, and `Subscription` types are the entry points for the requests sent by the client
- To enable the `allPersons`-query and the `last` argument:

```
type Query {
  allPersons(last: Int): [Person!]!
}
```

- For the `createPerson`-mutation:

```
type Mutation {
  createPerson(name: String!, age: Int!): Person!
}
```

- For the `newPerson`-subscription:

```
type Subscription {
  newPerson: Person!
}
```

- See:
  - https://blog.graph.cool/graphql-server-basics-the-schema-ac5e2950214e
  - https://blog.graph.cool/graphql-server-basics-the-network-layer-51d97d21861
  - https://blog.graph.cool/graphql-server-basics-demystifying-the-info-argument-in-graphql-resolvers-6f26249f613a

# Big Picture (Architecture)

## Use Cases

- 3 different kinds of architectures that include a GraphQL server:
  1. GraphQL server with a connected database
  1. GraphQL server that is a thin layer in front of a number of third party or legacy systems and integrates them through a single GraphQL API
  1. A hybrid approach of a connected database and third party or legacy systems that can all be accessed through the same GraphQL API

## Resolver Functions

- The payload of a GraphQL query (or mutation) consists of a set of fields
- In the GraphQL server implementation, each of these fields corresponds to exactly one function - a _resolver_

# Advanced Tutorial - Clients

- "Infrastructure" features that you probably want to have in your app:
  - send queries and mutations directly without constructing HTTP requests
  - view-layer integration
  - caching
  - validation and optimization of queries based on the schema
- GraphQL provides the ability to abstract away a lot of the manual work you'd usually have to do
- 2 major GraphQL clients:
  - Apollo Client: <https://github.com/apollographql/apollo-client>
  - Relay: <https://facebook.github.io/relay/>

## Send Queries and Mutations Directly

- A GraphQL client allows you to fetch and update data in a _declarative_ manner
  - declare your data requirements
  - let the system take care of sending the request and handling the response

## View Layer Integrations & UI updates

- The declarative nature of GraphQL ties in particularly well with functional reactive programming techniques
  - a view simply declares its data dependencies and the UI is wired up with an FRP layer
- Taking React as an example, GraphQL clients use the concept of higher-order components to
  - fetch the needed data under the hood
  - make it available in the props of your components

## Caching Query Results: Concepts and Strategies

- With GraphQL, simply caching data that's fetched remotely into a local store, and returning them whenever the same query is sent is very inefficient for most applications
- _Normalize_ the data beforehand
  - the (potentially nested) query result gets flattened
  - the store will only contain individual records that can be referenced with a globally unique ID
  - see <https://dev-blog.apollodata.com/the-concepts-of-graphql-bc68bd819be3>

## Build-time Schema Validation & Optimizations

- The schema contains all information about what a client can potentially do with a GraphQL API
  - opportunity to validate and optimize queries at build-time

## Colocating Views and Data Dependencies

- GraphQL allows you to have UI code and data requirements side-by-side
  - mental overhead of thinking about how the right data ends up in the right parts of the UI is eliminated

# Server

- GraphQL enables the server developer to focus on describing the data available rather than implementing and optimizing specific endpoints

## GraphQL Execution

- GraphQL specifies an execution algorithm for how queries are transformed into results
  - query is traversed field by field, executing "resolvers" for each field
- Example schema:

```
type Query {
  author(id: ID!): Author
}

type Author {
  posts: [Post]
}

type Post {
  title: String
  content: String
}
```

- Example query:

```
query {
  author(id: "abc") {
    posts {
      title
      content
    }
  }
}
```

- Execution:

```
Query.author(root, { id: 'abc' }, context) -> author
Author.posts(author, null, context) -> posts
for each post in posts
  Post.title(post, null, context) -> title
  Post.content(post, null, context) -> content
```

- See <https://dev-blog.apollodata.com/graphql-explained-5844742f195e>

## Batched Resolving

- Imagine we wanted to get the authors of several posts on a blog:

```
query {
  posts {
    title
    author {
      name
      avatar
    }
  }
}
```

- Likely that many of the posts will have the same authors
  - we might accidentally make multiple requests for the same author object
- Wrap fetching function in a utility
  - wait for all of the resolvers to run
  - make sure to only fetch each item once
- Example:

```
authorLoader = new AuthorLoader()

// Queue up a bunch of fetches
authorLoader.load(1);
authorLoader.load(2);
authorLoader.load(1);
authorLoader.load(2);

// Then, the loader only does the minimal amount of work
fetch('/authors/1');
fetch('/authors/2');
```

- If our API supports batched requests, we can do only one fetch to the backend:

```
fetch('/authors?ids=1,2')
```

- In JavaScript, the above strategies can be implemented using a utility called DataLoader: <https://github.com/facebook/dataloader>

# More GraphQL Concepts

## Enhancing Reusability with Fragments

- A fragment is a collection of fields on a specific type.
- Consider the following type:

```
type User {
  name: String!
  age: Int!
  email: String!
  street: String!
  zipcode: String!
  city: String!
}
```

- We can represent the user's physical address as a fragment:

```
fragment addressDetails on User {
  name
  street
  zipcode
  city
}
```

- Query to access the address information of a user:

```
{
  allUsers {
    ... addressDetails
  }
}
```

## Parameterizing Fields with Arguments

- In GraphQL type definitions, each field can take zero or more arguments
  - each argument needs to have a name and a type
  - can have default values for arguments
- Example: an argument to the `allUsers` field
  - to filter users and include only those above a certain age
  - with a default value so that by default all users will be returned

```
type Query {
  allUsers(olderThan: Int = -1): [User!]!
}
```

- Query:

```
{
  allUsers(olderThan: 30) {
    name
    age
  }
}
```

## Named Query Results with Aliases

- Since GraphQL response data is shaped after the structure of the fields being requested, you might run into naming issues when you're sending multiple queries asking for the same fields

```
{
  User(id: "1") {
    name
  }
  User(id: "2") {
    name
  }
}
```

- The above will produce an error with a GraphQL server, since it's the same field but different arguments
- The only way to send a query like that would be to use aliases, i.e. specifying names for the query results:

```
{
  first: User(id: "1") {
    name
  }
  second: User(id: "2") {
    name
  }
}
```

- Response:

```
{
  "first": {
    "name": "Alice"
  },
  "second": {
    "name": "Sarah"
  }
}
```

## Advanced SDL

### Object & Scalar Types

- In GraphQL, there are two different kinds of types:
  1. _Scalar_ types: concrete units of data
     - 5 predefined scalars: String, Int, Float, Boolean, and ID
  1. _Object_ types: have fields that express the properties of that type and are composable
     - examples: the `User` or `Post` types

### Enums

- Enumerations types that has a fixed set of values
  - a special kind of scalar type
- Example: a `Weekday` type:

```
enum Weekday {
  MONDAY
  TUESDAY
  WEDNESDAY
  THURSDAY
  FRIDAY
  SATURDAY
  SUNDAY
}
```

### Interface

- Allows you to specify a set of fields that any concrete type, which implements this interface, needs to have

```
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
  age: Int!
}
```

### Union Types

- A type that should be either of a collection of other types

```
type Adult {
  name: String!
  work: String!
}

type Child {
  name: String!
  school: String!
}
```

- A `Person` type that is the union of `Adult` and `Child`:

```
union Person = Adult | Child
```

- When we retrieve information about a `Child` but only have a `Person` type to work with, how do we know whether we can actually access this field?
  - conditional fragments:

```
{
  allPersons {
    name # works for `Adult` and `Child`
    ... on Child {
      school
    }
    ... on Adult {
       work
    }
  }
}
```

# Tooling and Ecosystem

## Introspection

- GraphQL allows clients to ask a server for information about its schema
  - `introspection`
  - query the `__schema` meta-field, which is always available on the root type of a Query

```
query {
  __schema {
    types {
      name
    }
  }
}
```

- The above query lists all types on the schema
  - both object types we defined and scalar types
- Example - query a single type using the `__type` meta-field:

```
{
  __type(name: "Author") {
    name
    description
  }
}
```

- Result:

```
{
  "data": {
    "__type": {
      "name": "Author",
      "description": "The author of a post.",
    }
  }
}
```

- One of the most useful tools you will need as you build and use GraphQL APIs uses introspection heavily: GraphiQL
  - <https://github.com/graphql/graphiql/tree/master/packages/graphiql>
  - an in-browser tool for writing, validating, and testing GraphQL queries

## GraphQL Playground

- A powerful "GraphQL IDE" for interactively working with a GraphQL API
- <https://github.com/prisma-labs/graphql-playground>

# Security

- Queries may be abusive queries from evil clients, or may simply be very large queries used by legitimate clients
- Strategies to mitigate risks, in order from the simplest to the most complex

## Timeout

- Maximum time allowed for a query
- Pros
  - simple to implement
  - timeout as a final protection
- Cons
  - damage can already be done even when the timeout kicks in
  - sometimes hard to implement; cutting connections after a certain time may result in strange behaviours

## Maximum Query Depth

- GraphQL schemas are often cyclic graphs
- A client could craft a query like this:

```
query IAmEvil {
  author(id: "abc") {
    posts {
      author {
        posts {
          author {
            # that could go on as deep as the client wants!
          }
        }
      }
    }
  }
}
```

- By analyzing the query document's abstract syntax tree (AST), a GraphQL server can reject a request based on its depth
- Pros
  - since the AST of the document is analyzed statically, the query does not even execute, which adds no load on your GraphQL server
- Cons
  - depth alone is often not enough to cover all abusive queries
  - a query requesting an enormous amount of nodes on the root will be very expensive but unlikely to be blocked by a query depth analyzer

## Query Complexity

- In a lot of cases, certain fields in our schema are known to be more complex to compute than others
- Restrict queries with a maximum complexity
- A common default is to give each field a complexity of 1
- Example with a complexity of 3:

```
query {
  author(id: "abc") { # complexity: 1
    posts {           # complexity: 1
      title           # complexity: 1
    }
  }
}
```

- We can set a different complexity to a field
- We can even set a different complexity depending on arguments:

```
query {
  author(id: "abc") {    # complexity: 1
    posts(first: 5) {    # complexity: 5
      title              # complexity: 1
    }
  }
}
```

- Pros
  - covers more cases than a simple query depth
  - reject queries before executing them by statically analyzing the complexity
- Cons
  - hard to implement perfectly
  - if complexity is estimated by developers
    - how do we keep it up to date?
    - how do we find the costs in the first place?
  - mutations are hard to estimate, e.g., side effect that is hard to measure, like queuing a background job

## Throttling

- In most APIs, a simple throttle is used to stop clients from requesting resources too often
- For GraphQL, throttling on the number of requests does not really help
  - even a few queries might be too much if they are very large

### Throttling Based on Server Time

- Server time to complete a query as an estimate of how expensive the query is
- Example of a leaky bucket (algorithm) throttle
  - maximum server time (Bucket Size) allowed is set to 1000ms
  - clients gain 100ms of server time per second (Leak Rate)
  - mutation takes on average 200ms to complete
  - a client calling this operation more than 5 times within 1 second would be blocked until more available server time is added to the client
  - after two seconds, our client can call `createPost` a single time

### Throttling Based on Query Complexity

- With a maximum complexity cost (Bucket Size) of 9
  - our clients can run a query of cost 3 only 3 times
  - leak rate forbids them to query more
- Example usage: <https://developer.github.com/v4/guides/resource-limitations/>

# Common Questions

- How to do Server-side Caching?
  - with GraphQL it's not clear what a client will request next, so putting a caching layer right behind the API doesn't make a lot of sense
  - more info about caching: <http://graphql.org/learn/caching/>
- How to do Authentication and Authorization?
  - authentication: can be implemented with common patterns such as OAuth
  - authorization: it is recommended to delegate any data access logic to the business logic layer and not handle it directly in the GraphQL implementation
    - see <https://www.graph.cool/docs/reference/auth/overview-ohs4aek0pe>
- How to do Error Handling?
  - if the request fails or partially fails, a second root field called `errors` is added to the response
  - see <http://facebook.github.io/graphql/#sec-Errors>

```
{
  "data": { ... },
  "errors": [ ... ]
}
```

- Does GraphQL Support Offline Usage?
  - caching abilities of Relay and Apollo might already be enough for some use cases
  - there isn't a popular solution for actually persisting stored data yet
  - see:
    - <https://github.com/facebook/relay/issues/676>
    - <https://github.com/apollographql/apollo-client/issues/424>
    - <http://www.east5th.co/blog/2017/07/24/offline-graphql-queries-with-redux-offline-and-apollo/>

# Sources

- "Core Concepts." <https://www.howtographql.com/basics/2-core-concepts/>.
- "Big Picture (Architecture)." <https://www.howtographql.com/basics/3-big-picture/>.
- "Advanced Tutorial - Clients." <https://www.howtographql.com/advanced/0-clients/>.
- "Server." <https://www.howtographql.com/advanced/1-server/>.
- "More GraphQL Concepts." <https://www.howtographql.com/advanced/2-more-graphql-concepts/>.
- "Tooling and Ecosystem." <https://www.howtographql.com/advanced/3-tooling-and-ecosystem/>.
- "Security." <https://www.howtographql.com/advanced/4-security/>.
- "Common Questions." <https://www.howtographql.com/advanced/5-common-questions/>.
