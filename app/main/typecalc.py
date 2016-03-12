class TypeCalc:
    def __init__(self, form):
        self.form = form

    def get_type(self):
        form_values = {
            'noCallNoShow': 3,
            'leaveEarly': 2,
            'callInNoNote': 2,
            'drawerOff': 2,
            'notDoing': 1.5,
            'lateNoCall': 1,
            'eatBehind': 1,
            'extendedBreak': 1,
            'outOfUniform': 1,
            'cellPhone': 1,
            'headPhone': 1,
            'callInWNotice': .5,
            'missedMeeting': .5
        }
        better_type_names = {
            'noCallNoShow': 'no call no show',
            'leaveEarly': 'left early',
            'callInNoNote': 'called in with no note',
            'drawerOff': 'drawer was off',
            'notDoing': 'not doing as instructed',
            'lateNoCall': 'late with no call',
            'eatBehind': 'eating or drinking behind line',
            'extendedBreak': 'taking extended breaks',
            'outOfUniform': 'out of uniform',
            'cellPhone': 'cell phone use',
            'headPhone': 'head phone use',
            'callInWNotice': 'called in with prior notice',
            'missedMeeting': 'missed meeting',
            'other': 'other'
        }
        numPts = 0
        type = ""
        for field in self.form:
            newNumPts = 0
            if field.name == 'other':
                try:
                    newNumPts = float(field.data)
                    if newNumPts > numPts:
                        numPts = float(newNumPts)
                        type = field.name
                except:
                    pass
            if field.data is True:
                try:
                    newNumPts = float(form_values[field.name])
                except:
                    pass
                if newNumPts > numPts:
                    numPts = newNumPts
                    type = field.name
        return better_type_names[type]