"""
逐光成长系统 - 完整数据初始化脚本
包含角色、用户、权限等所有初始数据
"""
import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker
from app.core.security import get_password_hash


async def init_roles(session):
    """初始化角色数据"""
    roles = [
        {"id": 1, "role_name": "super_admin", "remark": "系统最高权限，可管理所有功能"},
        {"id": 2, "role_name": "admin", "remark": "管理用户和日志，不可操作业务数据"},
        {"id": 3, "role_name": "teacher", "remark": "管理班级、学员、成长值、奖励"},
        {"id": 4, "role_name": "student", "remark": "查看成长值、兑换奖励"}
    ]
    
    for role in roles:
        await session.execute(
            text("""
                INSERT INTO sys_role (id, role_name, remark)
                VALUES (:id, :role_name, :remark)
                ON DUPLICATE KEY UPDATE role_name = VALUES(role_name), remark = VALUES(remark)
            """),
            role
        )
    print("✓ 角色数据初始化完成")


async def init_users(session):
    """初始化用户数据"""
    password_hash = get_password_hash("Password123")
    
    users = [
        {
            "id": 1,
            "email": "admin@example.com",
            "username": "admin",
            "password": password_hash,
            "real_name": "超级管理员",
            "phone": "13800138000",
            "role_id": 1,
            "status": 1,
            "login_count": 0
        },
        {
            "id": 2,
            "email": "teacher@example.com",
            "username": "teacher",
            "password": password_hash,
            "real_name": "张导师",
            "phone": "13800138001",
            "role_id": 3,
            "status": 1,
            "login_count": 0
        },
        {
            "id": 3,
            "email": "student@example.com",
            "username": "student",
            "password": password_hash,
            "real_name": "李同学",
            "phone": "13800138002",
            "role_id": 4,
            "status": 1,
            "login_count": 0
        }
    ]
    
    for user in users:
        await session.execute(
            text("""
                INSERT INTO sys_user (id, email, username, password, real_name, phone, role_id, status, login_count)
                VALUES (:id, :email, :username, :password, :real_name, :phone, :role_id, :status, :login_count)
                ON DUPLICATE KEY UPDATE 
                    email = VALUES(email),
                    username = VALUES(username),
                    real_name = VALUES(real_name),
                    phone = VALUES(phone),
                    role_id = VALUES(role_id)
            """),
            user
        )
    print("✓ 用户数据初始化完成")


async def init_permissions(session):
    """初始化权限数据"""
    # 清空现有权限数据
    await session.execute(text("DELETE FROM sys_role_permission"))
    await session.execute(text("DELETE FROM sys_permission"))
    await session.execute(text("ALTER TABLE sys_permission AUTO_INCREMENT = 1"))
    
    # 菜单权限
    menu_permissions = [
        # 控制台
        {"id": 1, "permission_name": "控制台", "permission_code": "menu:dashboard", "parent_id": None, "type": 1, "path": "/admin", "component": "Dashboard", "icon": "HomeOutlined", "sort": 1, "status": 1},
        # 用户管理
        {"id": 2, "permission_name": "用户管理", "permission_code": "menu:user", "parent_id": None, "type": 1, "path": "/admin/users", "component": "UserList", "icon": "UserOutlined", "sort": 2, "status": 1},
        # 角色管理
        {"id": 3, "permission_name": "角色管理", "permission_code": "menu:role", "parent_id": None, "type": 1, "path": "/admin/roles", "component": "RoleList", "icon": "TeamOutlined", "sort": 3, "status": 1},
        # 权限管理
        {"id": 4, "permission_name": "权限管理", "permission_code": "menu:permission", "parent_id": None, "type": 1, "path": "/admin/permissions", "component": "PermissionList", "icon": "LockOutlined", "sort": 4, "status": 1},
        # 班级管理
        {"id": 5, "permission_name": "班级管理", "permission_code": "menu:class", "parent_id": None, "type": 1, "path": "/admin/classes", "component": "ClassList", "icon": "BankOutlined", "sort": 5, "status": 1},
        # 学员管理
        {"id": 6, "permission_name": "学员管理", "permission_code": "menu:student", "parent_id": None, "type": 1, "path": "/admin/students", "component": "StudentList", "icon": "SolutionOutlined", "sort": 6, "status": 1},
        # 礼品管理
        {"id": 7, "permission_name": "礼品管理", "permission_code": "menu:gift", "parent_id": None, "type": 1, "path": "/admin/gifts", "component": "GiftList", "icon": "GiftOutlined", "sort": 7, "status": 1},
        # 订单管理
        {"id": 8, "permission_name": "订单管理", "permission_code": "menu:order", "parent_id": None, "type": 1, "path": "/admin/orders", "component": "OrderList", "icon": "ShoppingOutlined", "sort": 8, "status": 1},
        # 心愿便利贴管理
        {"id": 9, "permission_name": "心愿便利贴管理", "permission_code": "menu:wish", "parent_id": None, "type": 1, "path": "/admin/wishes", "component": "WishList", "icon": "HeartOutlined", "sort": 9, "status": 1},
        # 意见征集管理
        {"id": 10, "permission_name": "意见征集管理", "permission_code": "menu:suggestion", "parent_id": None, "type": 1, "path": "/admin/suggestions", "component": "SuggestionList", "icon": "CommentOutlined", "sort": 10, "status": 1},
        # 系统日志
        {"id": 11, "permission_name": "系统日志", "permission_code": "menu:log", "parent_id": None, "type": 1, "path": "/admin/logs", "component": "LogList", "icon": "FileTextOutlined", "sort": 11, "status": 1},
        # 系统设置
        {"id": 12, "permission_name": "系统设置", "permission_code": "menu:settings", "parent_id": None, "type": 1, "path": "/admin/settings", "component": "Settings", "icon": "SettingOutlined", "sort": 12, "status": 1}
    ]
    
    for perm in menu_permissions:
        await session.execute(
            text("""
                INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status)
                VALUES (:id, :permission_name, :permission_code, :parent_id, :type, :path, :component, :icon, :sort, :status)
            """),
            perm
        )
    
    # 按钮权限
    button_permissions = [
        # 控制台按钮
        {"id": 101, "permission_name": "查看统计", "permission_code": "btn:dashboard:view", "parent_id": 1, "type": 2},
        # 用户管理按钮
        {"id": 201, "permission_name": "查看用户", "permission_code": "btn:user:view", "parent_id": 2, "type": 2},
        {"id": 202, "permission_name": "编辑用户", "permission_code": "btn:user:edit", "parent_id": 2, "type": 2},
        {"id": 203, "permission_name": "禁用用户", "permission_code": "btn:user:disable", "parent_id": 2, "type": 2},
        {"id": 204, "permission_name": "启用用户", "permission_code": "btn:user:enable", "parent_id": 2, "type": 2},
        {"id": 205, "permission_name": "重置密码", "permission_code": "btn:user:reset-password", "parent_id": 2, "type": 2},
        {"id": 206, "permission_name": "编辑角色", "permission_code": "btn:user:edit-role", "parent_id": 2, "type": 2},
        {"id": 207, "permission_name": "导出用户", "permission_code": "btn:user:export", "parent_id": 2, "type": 2},
        # 角色管理按钮
        {"id": 301, "permission_name": "查看角色", "permission_code": "btn:role:view", "parent_id": 3, "type": 2},
        {"id": 302, "permission_name": "创建角色", "permission_code": "btn:role:create", "parent_id": 3, "type": 2},
        {"id": 303, "permission_name": "编辑角色", "permission_code": "btn:role:edit", "parent_id": 3, "type": 2},
        {"id": 304, "permission_name": "删除角色", "permission_code": "btn:role:delete", "parent_id": 3, "type": 2},
        {"id": 305, "permission_name": "分配权限", "permission_code": "btn:role:assign-permission", "parent_id": 3, "type": 2},
        # 权限管理按钮
        {"id": 401, "permission_name": "查看权限", "permission_code": "btn:permission:view", "parent_id": 4, "type": 2},
        {"id": 402, "permission_name": "创建权限", "permission_code": "btn:permission:create", "parent_id": 4, "type": 2},
        {"id": 403, "permission_name": "编辑权限", "permission_code": "btn:permission:edit", "parent_id": 4, "type": 2},
        {"id": 404, "permission_name": "删除权限", "permission_code": "btn:permission:delete", "parent_id": 4, "type": 2},
        # 班级管理按钮
        {"id": 501, "permission_name": "查看班级", "permission_code": "btn:class:view", "parent_id": 5, "type": 2},
        {"id": 502, "permission_name": "查看学员", "permission_code": "btn:class:view-students", "parent_id": 5, "type": 2},
        {"id": 503, "permission_name": "查看成长记录", "permission_code": "btn:class:view-growth", "parent_id": 5, "type": 2},
        {"id": 504, "permission_name": "关闭班级", "permission_code": "btn:class:close", "parent_id": 5, "type": 2},
        {"id": 505, "permission_name": "开放班级", "permission_code": "btn:class:open", "parent_id": 5, "type": 2},
        {"id": 506, "permission_name": "删除班级", "permission_code": "btn:class:delete", "parent_id": 5, "type": 2},
        {"id": 507, "permission_name": "导出班级", "permission_code": "btn:class:export", "parent_id": 5, "type": 2},
        # 学员管理按钮
        {"id": 601, "permission_name": "查看学员", "permission_code": "btn:student:view", "parent_id": 6, "type": 2},
        {"id": 602, "permission_name": "查看详情", "permission_code": "btn:student:view-detail", "parent_id": 6, "type": 2},
        {"id": 603, "permission_name": "查看成长记录", "permission_code": "btn:student:view-growth", "parent_id": 6, "type": 2},
        {"id": 604, "permission_name": "强制解绑", "permission_code": "btn:student:unbind", "parent_id": 6, "type": 2},
        {"id": 605, "permission_name": "强制删除", "permission_code": "btn:student:delete", "parent_id": 6, "type": 2},
        {"id": 606, "permission_name": "查看学员日志", "permission_code": "btn:student:view-log", "parent_id": 6, "type": 2},
        {"id": 607, "permission_name": "导出学员", "permission_code": "btn:student:export", "parent_id": 6, "type": 2},
        # 礼品管理按钮
        {"id": 701, "permission_name": "查看礼品", "permission_code": "btn:gift:view", "parent_id": 7, "type": 2},
        {"id": 702, "permission_name": "上架礼品", "permission_code": "btn:gift:online", "parent_id": 7, "type": 2},
        {"id": 703, "permission_name": "下架礼品", "permission_code": "btn:gift:offline", "parent_id": 7, "type": 2},
        {"id": 704, "permission_name": "修改库存", "permission_code": "btn:gift:edit-stock", "parent_id": 7, "type": 2},
        {"id": 705, "permission_name": "删除礼品", "permission_code": "btn:gift:delete", "parent_id": 7, "type": 2},
        {"id": 706, "permission_name": "导出礼品", "permission_code": "btn:gift:export", "parent_id": 7, "type": 2},
        # 订单管理按钮
        {"id": 801, "permission_name": "查看订单", "permission_code": "btn:order:view", "parent_id": 8, "type": 2},
        {"id": 802, "permission_name": "查看详情", "permission_code": "btn:order:view-detail", "parent_id": 8, "type": 2},
        {"id": 803, "permission_name": "强制核销", "permission_code": "btn:order:verify", "parent_id": 8, "type": 2},
        {"id": 804, "permission_name": "强制取消", "permission_code": "btn:order:cancel", "parent_id": 8, "type": 2},
        {"id": 805, "permission_name": "导出订单", "permission_code": "btn:order:export", "parent_id": 8, "type": 2},
        # 心愿便利贴管理按钮
        {"id": 901, "permission_name": "查看心愿", "permission_code": "btn:wish:view", "parent_id": 9, "type": 2},
        {"id": 902, "permission_name": "查看发布人", "permission_code": "btn:wish:view-publisher", "parent_id": 9, "type": 2},
        {"id": 903, "permission_name": "删除心愿", "permission_code": "btn:wish:delete", "parent_id": 9, "type": 2},
        {"id": 904, "permission_name": "导出心愿", "permission_code": "btn:wish:export", "parent_id": 9, "type": 2},
        # 意见征集管理按钮
        {"id": 1001, "permission_name": "查看帖子", "permission_code": "btn:suggestion:view", "parent_id": 10, "type": 2},
        {"id": 1002, "permission_name": "删除帖子", "permission_code": "btn:suggestion:delete-post", "parent_id": 10, "type": 2},
        {"id": 1003, "permission_name": "删除评论", "permission_code": "btn:suggestion:delete-comment", "parent_id": 10, "type": 2},
        {"id": 1004, "permission_name": "导出意见", "permission_code": "btn:suggestion:export", "parent_id": 10, "type": 2},
        # 系统日志按钮
        {"id": 1101, "permission_name": "查看日志", "permission_code": "btn:log:view", "parent_id": 11, "type": 2},
        {"id": 1102, "permission_name": "查看详情", "permission_code": "btn:log:view-detail", "parent_id": 11, "type": 2},
        {"id": 1103, "permission_name": "导出日志", "permission_code": "btn:log:export", "parent_id": 11, "type": 2},
        # 系统设置按钮
        {"id": 1201, "permission_name": "查看设置", "permission_code": "btn:settings:view", "parent_id": 12, "type": 2},
        {"id": 1202, "permission_name": "编辑设置", "permission_code": "btn:settings:edit", "parent_id": 12, "type": 2},
        {"id": 1203, "permission_name": "清理缓存", "permission_code": "btn:settings:clear-cache", "parent_id": 12, "type": 2}
    ]
    
    for perm in button_permissions:
        await session.execute(
            text("""
                INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type)
                VALUES (:id, :permission_name, :permission_code, :parent_id, :type)
            """),
            perm
        )
    
    print("✓ 权限数据初始化完成")


async def init_role_permissions(session):
    """初始化角色权限关联数据"""
    # super_admin (role_id=1) 拥有所有权限
    await session.execute(
        text("INSERT INTO sys_role_permission (role_id, permission_id) SELECT 1, id FROM sys_permission")
    )
    
    # admin (role_id=2) 权限分配
    # 可访问：控制台、用户、班级、学员、礼品、订单、心愿、意见、系统日志
    admin_permissions = [
        1, 101,  # 控制台
        2, 201, 202, 203, 204, 207,  # 用户管理
        5, 501, 502, 503, 504, 505, 507,  # 班级管理
        6, 601, 602, 603, 604, 605, 606, 607,  # 学员管理
        7, 701, 702, 703, 704, 705, 706,  # 礼品管理
        8, 801, 802, 803, 804, 805,  # 订单管理
        9, 901, 902, 903, 904,  # 心愿便利贴管理
        10, 1001, 1002, 1003, 1004,  # 意见征集管理
        11, 1101, 1102, 1103  # 系统日志
    ]
    
    for perm_id in admin_permissions:
        await session.execute(
            text("INSERT INTO sys_role_permission (role_id, permission_id) VALUES (2, :perm_id)"),
            {"perm_id": perm_id}
        )
    
    # teacher (role_id=3) 和 student (role_id=4) 不能进入后台，不分配任何后台权限
    
    print("✓ 角色权限关联数据初始化完成")


async def init_all_data():
    """初始化所有数据"""
    async with async_session_maker() as session:
        try:
            await session.begin()
            
            await init_roles(session)
            await init_users(session)
            await init_permissions(session)
            await init_role_permissions(session)
            
            await session.commit()
            print("\n✓ 所有数据初始化成功！")
            print("\n默认账号信息：")
            print("┌─────────────────────────────┬──────────┬──────────────┬─────────────┐")
            print("│ 邮箱                        │ 用户名   │ 密码         │ 角色        │")
            print("├─────────────────────────────┼──────────┼──────────────┼─────────────┤")
            print("│ admin@example.com           │ admin    │ Password123  │ 超级管理员  │")
            print("│ teacher@example.com         │ teacher  │ Password123  │ 导师        │")
            print("│ student@example.com         │ student  │ Password123  │ 学员        │")
            print("└─────────────────────────────┴──────────┴──────────────┴─────────────┘")
            print("\n⚠️  安全提示：首次登录后请立即修改默认密码！")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 数据初始化失败：{e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("  逐光成长系统 - 数据初始化脚本")
    print("=" * 60)
    print()
    asyncio.run(init_all_data())
