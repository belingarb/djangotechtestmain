import json

import pytest
from django.core.exceptions import ObjectDoesNotExist

from techtest.authors.models import Author

pytestmark = pytest.mark.django_db


def test_authors(client):
    # Test create / retrieve
    data = {
        "first_name": "test_author_fn",
        "last_name": "test_author_ln"
    }
    res = client.post('/authors/', data=data, content_type="application/json")
    json_data = json.loads(res.content)
    author_id = json_data.get('id')
    assert res.status_code == 201
    assert json_data.get('first_name') == data['first_name']
    assert json_data.get('last_name') == data['last_name']
    assert Author.objects.get(id=json_data.get('id'))
    # Test retrieve
    res = client.get(f'/authors/{author_id}/')
    assert res.status_code == 200
    assert json_data.get('first_name') == data['first_name']
    assert json_data.get('last_name') == data['last_name']
    assert Author.objects.get(id=author_id)

    # Test list
    res = client.get('/authors/')
    json_data = json.loads(res.content)
    assert len(json_data) == 1
    assert json_data[0].get('first_name') == data['first_name']
    assert json_data[0].get('last_name') == data['last_name']

    # Test update
    updated_data = {
        "first_name": "test_author_fn_update",
        "last_name": "test_author_ln_update"
    }
    res = client.put(f'/authors/{author_id}/', data=updated_data, content_type='application/json')
    json_data = json.loads(res.content)
    assert res.status_code == 200
    assert json_data.get('first_name') == updated_data['first_name']
    assert json_data.get('last_name') == updated_data['last_name']

    # Test delete
    res = client.delete(f'/authors/{author_id}/')
    assert res.status_code == 200
    # Test if it was removed correctly
    with pytest.raises(ObjectDoesNotExist):
        Author.objects.get(id=author_id)

    # Test retrieve object that does not exist
    res = client.get('/authors/2/')
    assert res.status_code == 404






