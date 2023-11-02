from techtest.authors.models import Author
from marshmallow import fields, Schema, validate, post_load


class AuthorSchema(Schema):
    class Meta(object):
        model = Author

    id = fields.Integer()
    first_name = fields.String(validate=validate.Length(max=30))
    last_name = fields.String(validate=validate.Length(max=30))

    @post_load
    def update_or_create(self, data, *args, **kwargs):
        author, _ = Author.objects.update_or_create(
            id=data.pop("id", None), defaults=data
        )
        return author
