import graphene
import django_filters
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Link, Vote


class LinkFilter(django_filters.FilterSet):
    """Relay allows you to use django-filter for filtering data."""

    class Meta:
        model = Link
        # FilterSet with url and description fields
        fields = ["url", "description"]


class LinkNode(DjangoObjectType):
    """Data is exposed in _Nodes_."""

    class Meta:
        model = Link
        # Each node implements an interface with a unique ID
        interfaces = (graphene.relay.Node,)


class VoteNode(DjangoObjectType):
    class Meta:
        model = Vote
        interfaces = (graphene.relay.Node,)


class RelayQuery(graphene.ObjectType):
    # The query uses LinkNode with the relay_link field
    relay_link = graphene.relay.Node.Field(LinkNode)
    # relay_links field as a Connection, which implements the pagination structure
    relay_links = DjangoFilterConnectionField(LinkNode, filterset_class=LinkFilter)


# Mutation


class RelayCreateLink(graphene.relay.ClientIDMutation):
    link = graphene.Field(LinkNode)

    class Input:
        url = graphene.String()
        description = graphene.String()

    def mutate_and_get_payload(root, info, **input):
        user = info.context.user or None

        link = Link(
            url=input.get("url"), description=input.get("description"), posted_by=user,
        )
        link.save()

        return RelayCreateLink(link=link)


class RelayMutation(graphene.AbstractType):
    relay_create_link = RelayCreateLink.Field()
