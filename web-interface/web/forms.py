# TODO Use RadioField(s)
# Problems: 
# - initial value is not propagated to radio-control
# - when using a second radio-field on mp3Bitrate, field.data in validate_oggQuality
#   returns 'none', thus the validation returns false

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, BooleanField, SelectField, RadioField, ValidationError

class EditTranscoderForm(FlaskForm):
    sourceFolder = StringField('SourceFolder')
    oggFolder = StringField('OggFolder')
    oggQuality = IntegerField('OggQuality')
#    oggQuality = RadioField(
#        'OggQuality', 
#        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    mp3Folder = StringField('Mp3Folder')
    mp3Bitrate = IntegerField('Mp3Bitrate')
#    mp3Bitrate = RadioField(
#        'Mp3Bitrate',
#        choices=[(128, 128), (256, 256), (384, 384)])
    submit = SubmitField('Save')

    # Not using standard wtf-validators like Required b/c they do not 
    # show custom messages; this is overruled by HTML5
    # Name of field validators must be in this exact format: validate_<variable>
    def validate_oggQuality(self, field):
        if not int(field.data) in [0, 1, 2, 3, 4, 5]:  
            raise ValidationError('Value must be between 1 and 5')
        pass

    def validate_mp3Bitrate(self, field):
        if not int(field.data) in [0, 128, 256, 384]:  
            raise ValidationError('Value must be 128, 256 or 384')
        pass
