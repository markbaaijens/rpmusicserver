from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, BooleanField, SelectField, RadioField, ValidationError

class EditTranscoderForm(FlaskForm):
    sourceFolder = StringField('SourceFolder')
    oggFolder = StringField('OggFolder')
    oggQuality = IntegerField('OggQuality')
    mp3Folder = StringField('Mp3Folder')
    mp3Bitrate = IntegerField('Mp3Bitrate')
    submit = SubmitField('Save')

    # Not using standard wtf-validators like Required b/c they do not 
    # show custom messages; this is overruled by HTML5
    # Name of field validatirs must be in this exact format: validate_<variable>
    def validate_oggQuality(self, field):
        if not field.data in [1, 2, 3, 4, 5]:  
            raise ValidationError('Value must be between 1 and 5')
        pass

    def validate_mp3Bitrate(self, field):
        if not field.data in [128, 256, 384]:  
            raise ValidationError('Value must be 128, 256 or 384')
        pass
