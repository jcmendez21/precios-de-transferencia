"""Tests del management command seed_roles."""

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command


@pytest.mark.django_db
def test_seed_roles_creates_four_groups():
    call_command("seed_roles")
    names = set(Group.objects.values_list("name", flat=True))
    assert names == {"admin_firma", "senior", "junior", "revisor"}


@pytest.mark.django_db
def test_seed_roles_is_idempotent():
    call_command("seed_roles")
    call_command("seed_roles")  # segundo run no debe fallar ni duplicar
    assert Group.objects.count() == 4
