from django.contrib import admin

from ..models import (Announcement, CustomUser, Department, EmailModel,
                      Faculty, Instrument, LabAssistant, Slot, Student,
                      StudentRequest)
from ..models.instrument.requests import *
from .announcement import AnnouncementAdmin
from .email import EmailAdmin
from .instrument import InstrumentAdmin
from .request import RequestAdmin
from .slot import SlotAdmin
from .user import (CustomUserAdmin, DepartmentAdmin, FacultyAdmin,
                   LabAssistantAdmin, StudentAdmin)

admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(EmailModel, EmailAdmin)
admin.site.register(LabAssistant, LabAssistantAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(StudentRequest, RequestAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(UserDetail)
admin.site.register(FTIR)
admin.site.register(FESEM)
admin.site.register(LCMS)
admin.site.register(TCSPC)
admin.site.register(Rheometer)
admin.site.register(AAS)
admin.site.register(TGA)
admin.site.register(BET)
admin.site.register(CDSpectrophotometer)
admin.site.register(LSCM)
admin.site.register(DSC)
admin.site.register(GC)
admin.site.register(EDXRF)
admin.site.register(HPLC)
admin.site.register(HPLC_FD)
admin.site.register(NMR)
admin.site.register(PXRD)
admin.site.register(SAXS_WAXS)
admin.site.register(SCXRD)
admin.site.register(XPS)
admin.site.register(UVSpectrophotometer)
admin.site.register(UTM)
admin.site.register(VSM)
admin.site.register(EPR_ESR)
admin.site.register(GPC)
admin.site.register(CHNS)
admin.site.register(RT_PCR)
admin.site.register(Quantachrome)
admin.site.register(DLS)
admin.site.register(BDFACS)
admin.site.register(ContactAngle)
admin.site.register(DigitalPolarimeter)
admin.site.register(Fluorolog3)
admin.site.register(Fluoromax)
admin.site.register(SpectraFluorimeter)
admin.site.register(Ultracentrifuge)
admin.site.register(Announcement, AnnouncementAdmin)
