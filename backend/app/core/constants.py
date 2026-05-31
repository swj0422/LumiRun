class RoleConstants:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"
    CLASS_ASSISTANT = "class_assistant"
    STUDENT = "student"

    ADMIN_ROLES = [SUPER_ADMIN, ADMIN]
    TEACHER_ROLES = [SUPER_ADMIN, ADMIN, TEACHER, CLASS_ASSISTANT]
    ALL_ROLES = [SUPER_ADMIN, ADMIN, TEACHER, CLASS_ASSISTANT, STUDENT]


class LogConstants:
    TYPE_CREATE = "create"
    TYPE_UPDATE = "update"
    TYPE_DELETE = "delete"
    TYPE_VIEW = "view"
    
    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_ERROR = "error"


class StatusConstants:
    STATUS_DISABLED = 0
    STATUS_ENABLED = 1
    
    ORDER_STATUS_PENDING = 0
    ORDER_STATUS_APPROVED = 1
    ORDER_STATUS_VERIFIED = 2
    ORDER_STATUS_REJECTED = 3
