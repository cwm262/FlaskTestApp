class PointCalc:
    def __init__(self, form):
        self.form = form

    def calc_amount(self):
        amount = 0
        pt_values = {
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
        for field in self.form:
            if field.name == 'warning':
                if field.data is True:
                    return 0
            if field.name == 'other':
                try:
                    amount += float(field.data)
                except:
                    pass
            if field.data is True:
                try:
                    amount += pt_values[field.name]
                except:
                    pass
        return amount
