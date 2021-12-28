from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, BooleanField, SelectField, RadioField
from wtforms.validators import Length, InputRequired, NumberRange

from enums import BookType

# TODO Use selectorfield, datefield, etc.
# TODO Move validators to a different file: https://exploreflask.com/en/latest/forms.html
# TODO Check for unique name: https://exploreflask.com/en/latest/forms.html

class EditBookForm(FlaskForm):
    id = IntegerField('Id', render_kw={'readonly': True})
    name = StringField('Name')
    price = DecimalField('Price', places=2)
    isbn = IntegerField('ISBN')
    isObsolete = BooleanField('Obsolete')

    # TODO Use RadioField or SelectField; fill with BookType-enum
    #      bookType = RadioField('Type', choices=[(0, 'Unknown'), (1, 'Fiction'), (2, 'Non-fiction'), (3, 'Educational')])
    #      - set default and read return-value 
    #      - request.json does not return anything in controller!
    bookType = IntegerField('Type')
    submit = SubmitField('Save')

    # Not using standard wtf-validators like Required b/c they do not show custom message; this is overruled by HTML5
    def validate_name(self, field):
        if field.data == '':  
            raise ValueError('Field is required')
        if len(field.data) > 30:
            raise ValueError('Maximum size is 30 characters')
        pass

    def validate_isbn(self, field):
        if field.data < 1 or field.data > 10000 - 1:
            raise ValueError('Value must be between 1 and 9999')
        pass

class DeleteBookForm(FlaskForm):
    submit = SubmitField('Delete')