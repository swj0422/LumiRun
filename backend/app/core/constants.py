class RoleConstants:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    GROUP_ASSISTANT = "group_assistant"
    MEMBER = "member"

    ADMIN_ROLES = [SUPER_ADMIN, ADMIN]
    MANAGER_ROLES = [SUPER_ADMIN, ADMIN, MANAGER, GROUP_ASSISTANT]
    ALL_ROLES = [SUPER_ADMIN, ADMIN, MANAGER, GROUP_ASSISTANT, MEMBER]

    @staticmethod
    def get_teacher_alias():
        return RoleConstants.MANAGER

    @staticmethod
    def get_class_assistant_alias():
        return RoleConstants.GROUP_ASSISTANT


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
