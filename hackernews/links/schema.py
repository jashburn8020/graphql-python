import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q
from users.schema import UserType
from .models import Link, Vote


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    # Search parameter inside our links field
    links = graphene.List(LinkType, search=graphene.String())
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        if search:
            links_filter = Q(url__icontains=search) | Q(description__icontains=search)
            return Link.objects.filter(links_filter)

        return Link.objects.all()

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


# Mutation


class CreateLink(graphene.Mutation):
    """Defines a mutation class. Right after, you define the output of the mutation,
    the data the server can send back to the client. The output is defined field by
    field for learning purposes; can be defined as just one."""

    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        """Defines the data you can send to the server, in this case, the links' url
        and description."""

        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        """The mutation method. It creates a link in the database using the data sent
        by the user, through the url and description parameters. The server returns the
        CreateLink class with the data just created."""
        user = info.context.user or None

        link = Link(url=url, description=description, posted_by=user,)
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )


class CreateVote(graphene.Mutation):
    """CreateVote mutation"""

    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged to vote!")

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception("Invalid Link!")

        Vote.objects.create(
            user=user, link=link,
        )

        return CreateVote(user=user, link=link)


class Mutation(graphene.ObjectType):
    """Creates a mutation class with a field to be resolved, which points to our
    mutation defined before."""

    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
