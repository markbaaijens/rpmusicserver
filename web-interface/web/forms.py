from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, BooleanField, SelectField, RadioField, ValidationError

class EditTranscoderForm(FlaskForm):
    sourceFolder = StringField('Source Folder')
    oggFolder = StringField('Ogg Folder')
    oggQuality = RadioField('Ogg Quality', 
        choices=[(0, '1 = default'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], 
        coerce=int)
    mp3Folder = StringField('Mp3 Folder')
    mp3Bitrate = RadioField('Mp3 Bitrate', 
        choices=[(0, '128 = default'), (256, '256'), (384, 384)],
        coerce=int)
    resetToDefaults = BooleanField('Reset to defaults')
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')    

    # Not using standard wtf-validators like Required b/c they do not 
    # show custom messages; this is overruled by HTML5
    # Name of field validators must be in this exact format: validate_<variable>
    def validate_oggQuality(self, field):
        if field.data == None:
            field.data = 0
        if not int(field.data) in [0, 1, 2, 3, 4, 5]:  
            raise ValidationError('Value must be between 0 and 5')
        pass

    def validate_mp3Bitrate(self, field):
        if field.data == None:
            field.data = 0        
        if not int(field.data) in [0, 128, 256, 384]:  
            raise ValidationError('Value must be 0, 128, 256 or 384')
        pass

    def validate_sourceFolder(self, field):
        if not self.resetToDefaults.data: 
            if field.data == '':
                raise ValidationError('To activate trancoder, SourceFolder should have a value')

            if not((self.oggFolder.data != '') or (self.mp3Folder.data != '')):
                raise ValidationError('To activate trancoder, either OggFolder or Mp3Folder should have a value')
        pass

