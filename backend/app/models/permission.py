from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Permission(Base):
    """权限表"""
    __tablename__ = "sys_permission"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    permission_name = Column(String(50), nullable=False, comment="权限名称")
    permission_code = Column(String(50), unique=True, nullable=False, comment="权限编码")
    parent_id = Column(Integer, ForeignKey("sys_permission.id"), nullable=True, comment="父权限ID")
    type = Column(Integer, nullable=False, comment="权限类型：1-菜单，2-按钮")
    path = Column(String(255), nullable=True, comment="路由路径")
    component = Column(String(255), nullable=True, comment="组件路径")
    icon = Column(String(50), nullable=True, comment="图标")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态：0-禁用，1-启用")
    
    # 关系
    parent = relationship("Permission", remote_side=[id], backref="children")
    roles = relationship("Role", secondary="sys_role_permission", back_populates="permissions")


class RolePermission(Base):
    """角色权限关联表"""
    __tablename__ = "sys_role_permission"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("sys_role.id"), nullable=False, comment="角色ID")
    permission_id = Column(Integer, ForeignKey("sys_permission.id"), nullable=False, comment="权限ID")
