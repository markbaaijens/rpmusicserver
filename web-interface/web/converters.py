from enums import BookType

def ConvertBooleanToText(booleanValue):
    if booleanValue: 
        return 'Yes'
    else:
        return 'No'
    pass

def ConvertToTwoDecimals(decimalValue):
    return '%.2f' % decimalValue

def ConvertEnumBookTypeToDescription(bookType):
    description = 'Unknown'
    if bookType == BookType.Unknown:
        description = 'Unknown'
    else:
        if bookType == BookType.Fiction:
            description = 'Fiction'
        else:
            if bookType == BookType.NonFiction:
                description = 'Non-fiction'
            else:
                if bookType == BookType.Educational:
                    description = 'Educational'
    return description + ' (' + str(bookType) + ')'