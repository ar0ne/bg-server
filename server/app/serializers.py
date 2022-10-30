# Model serializers

from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.models import Room

RoomSerializer = pydantic_model_creator(Room)
RoomListSerializer = pydantic_queryset_creator(Room)