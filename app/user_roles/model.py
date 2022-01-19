class Roles:
    ALL_AUTHENTICATED = "all_authenticated"

    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

    SUPERVISOR = "supervisor"
    DOCTOR = "doctor"
    NURSE = "nurse"
    MEDICAL_ASSISTANT = "medical_assistant"
    OTHER = "other"
    CONTENT_PUBLISHER = "content_publisher"
    BUSINESS_LEADER = "business_leader"
    PATIENT = "patient"

    ALL = [
        ADMIN,
        SUPER_ADMIN,

        SUPERVISOR,
        DOCTOR,
        NURSE,
        MEDICAL_ASSISTANT,
        OTHER,
        CONTENT_PUBLISHER,
        BUSINESS_LEADER,

        PATIENT,
    ]

    ALL_ADMINS = [
        ADMIN,
        SUPER_ADMIN,
    ]

    ALL_EXCEPT_PATIENT = [
        ADMIN,
        SUPER_ADMIN,

        SUPERVISOR,
        DOCTOR,
        NURSE,
        MEDICAL_ASSISTANT,
        OTHER,
        CONTENT_PUBLISHER,
        BUSINESS_LEADER,
    ]

    ADMINS_AND_PATIENT = [
        ADMIN,
        SUPER_ADMIN,
        PATIENT,
    ]

    CARE_PLAN_AUTHORS = [
        ADMIN,
        SUPER_ADMIN,

        SUPERVISOR,
        DOCTOR,
    ]
