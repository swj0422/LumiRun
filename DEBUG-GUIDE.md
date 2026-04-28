# 调试指南

## 问题整理

### 1. "Module 'util' has been externalized for browser compatibility" 警告

**问题描述**：
前端出现 "Module 'util' has been externalized for browser compatibility" 警告，无法访问 "util.debuglog" 和 "util.inspect"。

**原因**：
前端项目中某个依赖库间接引用了 Node.js 的 "util" 模块，与浏览器环境不兼容。

**解决方案**：
- 检查前端代码，确认没有直接引用 "util" 模块
- 该警告不影响功能，可暂时忽略

### 2. 成长管理页面成长记录未显示信息

**问题描述**：
成长管理页面的成长记录没有显示信息，API 返回空数组。

**原因**：
- 前端代理配置错误，目标端口与后端实际端口不匹配
- 前端请求 URL 路径错误，未添加 /api 前缀
- 前端请求参数错误，传递的是 class_name 而非 class_id

**解决方案**：
- 修改 `vite.config.ts` 中的代理配置，将目标端口从 8001 改回 8000
- 修改 `GrowthList.vue` 中的 `fetchLogs` 方法，将请求 URL 从 `/v1/growth/logs` 改为 `/api/v1/growth/logs`
- 修改 `GrowthList.vue` 中的 `fetchLogs` 方法，将 `params.append('class_name', selectedClass.value)` 改为 `params.append('class_id', selectedClass.value)`

### 3. 班级管理、学员管理、首页都没数据

**问题描述**：
班级管理、学员管理、首页等页面都没有数据显示。

**原因**：
- 前端代理配置错误，`/v1` 路径的代理没有正确重写路径
- 前端代码中的 API 路径不一致，有些使用了 `/api/v1/` 前缀，有些使用了 `/v1/` 前缀

**解决方案**：
- 修改 `vite.config.ts` 文件中的代理配置，将 `/v1` 路径的代理重写为 `/api${path}`
- 统一所有前端页面的 API 调用路径，使用 `/api/v1/` 前缀

### 4. 成长日志和标签管理没有数据

**问题描述**：
成长日志和标签管理页面没有数据显示。

**原因**：
- 成长日志：`get_growth_history` 方法中使用了缓存，可能是缓存导致了返回空数组
- 标签管理：`TagList.vue` 中的 `fetchTags` 方法，将 `tags.value = data || []` 改为 `tags.value = data?.items || []`

**解决方案**：
- 移除 `get_growth_history` 方法中的缓存相关代码，直接查询数据库
- 修改 `TagList.vue` 中的 `fetchTags` 方法，正确处理 API 响应格式

### 5. 学员管理添加学员弹窗，班级要展示级、班、单位

**问题描述**：
学员管理添加学员弹窗中，班级选择只显示班级名称，没有显示级、班、单位等信息。

**解决方案**：
- 修改 `StudentListMain.vue` 文件中的班级选择模板，将原来只显示 `class_name` 的代码：
  ```html
  {{ cls.class_name }}
  ```
- 修改为显示完整的班级信息：
  ```html
  {{ cls.school_name || '' }} {{ cls.session || '' }}级 {{ cls.class_name }}班
  ```

### 6. 添加学员时，class_student表数据库bind_status没填

**问题描述**：
添加学员时，`class_student` 表的 `bind_status` 字段没填，并且出现 `'str' object has no attribute 'value'` 错误。

**原因**：
- `BindStatus` 是一个继承自 `str` 的枚举类型，当它被存储到数据库后，再从数据库中读取时，可能会被转换为字符串而不是枚举类型，因此没有 `value` 属性

**解决方案**：
- 修改 `student_service.py` 文件中的 `add_student` 方法，添加类型检查：
  ```python
  "bind_status": new_student.bind_status if isinstance(new_student.bind_status, str) else new_student.bind_status.value,
  ```

### 7. 学员管理里面学员列表，学员数据没有跟随上面搜索和筛选变动

**问题描述**：
学员管理页面的学员列表数据没有跟随上面的搜索和筛选变动。

**原因**：
- `fetchStudents` 方法只添加了 `keyword`、`school_name` 和 `status` 参数，没有添加 `selectedClass` 和 `selectedSession` 参数

**解决方案**：
- 修改 `StudentListMain.vue` 文件中的 `fetchStudents` 方法，添加对 `selectedClass` 和 `selectedSession` 参数的处理

### 8. 级的筛选有问题

**问题描述**：
级的筛选功能不工作。

**原因**：
- 前端传递了 `session` 参数，但是后端的 `get_teacher_students` 方法没有接收 `session` 参数，也没有在班级查询中使用这个参数

**解决方案**：
- 修改 `StudentService.get_teacher_students` 方法，添加 `session` 参数
- 在缓存键中添加 `session` 参数
- 在班级查询中添加 `session` 过滤条件
- 修改 API 端点 `get_teacher_students`，添加 `session` 查询参数

### 9. 班级的筛选有问题

**问题描述**：
班级的筛选功能不工作。

**原因**：
- 前端的 `selectedClass` 是一个字符串类型的 ref，当用户选择班级时，它会被设置为班级的 id（可能是数字类型），但当用户取消选择时，它会被设置为空字符串
- 在 `fetchStudents` 方法中，当 `selectedClass.value` 不为空时，会将其作为 `class_id` 参数传递给后端，但后端期望 `class_id` 是一个整数类型

**解决方案**：
- 修改 `fetchStudents` 方法，添加类型检查和转换：
  ```javascript
  if (selectedClass.value && !isNaN(Number(selectedClass.value))) {
    params.class_id = Number(selectedClass.value);
  }
  ```

### 10. 19班有一堆数据，但是筛选19班显示没数据

**问题描述**：
19班有45个学员，但是筛选19班时显示没数据。

**原因**：
- 前端的班级筛选绑定的是 `cls.class_name`，而不是 `cls.id`
- 当用户选择"19班"时，`selectedClass.value` 被设置为字符串"19"，但19班的实际ID是4

**解决方案**：
- 修改班级选择的模板，将 `v-for="cls in uniqueClasses"` 改为 `v-for="cls in classes"`
- 将 `:key="cls.class_name"` 改为 `:key="cls.id"`
- 将 `:value="cls.class_name"` 改为 `:value="cls.id"`

### 11. 登录问题 - request.ts:219 请求的资源不存在

**问题描述**：
登录页面出现 "请求的资源不存在" 错误，无法获取验证码。

**原因**：
- 前端 API 调用路径缺少 `/api` 前缀，导致请求无法被正确代理到后端服务器

**解决方案**：
- 修改 `Login.vue` 文件中的 `refreshCaptcha` 方法，将请求 URL 从 `/v1/auth/captcha` 改为 `/api/v1/auth/captcha`
- 修改 `auth.ts` 文件中的所有 API 路径，为它们添加 `/api` 前缀

### 12. class_student表，bind_status字段增加none

**问题描述**：
`class_student` 表的 `bind_status` 字段缺少 `none` 选项。

**原因**：
- 数据库表结构中 `bind_status` 字段的枚举值中缺少 'none' 选项

**解决方案**：
- 修改数据库表结构，为 `bind_status` 字段添加 'none' 选项
- 设置默认值为 'none'

### 13. 班级管理，各班级对应的学员数不对

**问题描述**：
班级管理页面显示的学员数为0，与实际情况不符。

**原因**：
- `ClassService.get_class_student_count` 方法只统计了 `BindStatus.APPROVED` 状态的学员，没有包含导师导入的学员（`BindStatus.NONE`）
- 此外，在 SQLAlchemy 中使用 `in_` 方法时，需要传递枚举的字符串值，而不是枚举对象

**解决方案**：
- 修改 `ClassService.get_class_student_count` 方法，将统计条件改为同时统计 `BindStatus.NONE` 和 `BindStatus.APPROVED` 的学员
- 使用 `BindStatus.NONE.value` 和 `BindStatus.APPROVED.value` 来获取枚举的字符串值

### 14. 程序里面记录时间不对，不是操作时候的时间

**问题描述**：
程序中记录的时间与实际操作时间不一致。

**原因**：
- 所有的时间字段都是使用 `datetime.utcnow()` 来设置的，这会导致时间显示为 UTC 时间，而不是本地时间

**解决方案**：
- 修改所有模型文件中的时间字段默认值，从 `datetime.utcnow` 改为 `datetime.now`
- 修改所有服务文件中的时间设置，从 `datetime.utcnow()` 改为 `datetime.now()`

### 15. 导师成长排行没有数据显示

**问题描述**：
导师成长排行页面没有显示任何学员数据。

**原因**：
- `get_leaderboard` 方法中 `if total_score != 0:` 条件的缩进错误，导致只有最后一个学员的成长值被检查
- 缓存键没有版本号，修改代码后缓存没有更新

**解决方案**：
- 修复 `growth_service.py` 中的缩进错误，将 `if total_score != 0:` 条件放入 `for student in students:` 循环内部
- 在所有缓存键中添加版本号（如 `v2`），确保代码修改后缓存会更新

### 16. 班级助理无法查看排行榜数据

**问题描述**：
班级助理登录后无法查看成长排行数据。

**原因**：
- `security.py` 中的 `require_teacher` 依赖没有包含 `class_assistant` 角色
- `get_leaderboard` 方法只获取导师自己的班级，没有包括班级助理被授权的班级

**解决方案**：
- 修改 `security.py`，将 `class_assistant` 添加到 `require_teacher` 角色中：
  ```python
  require_teacher = require_role("super_admin", "admin", "teacher", "class_assistant")
  ```
- 修改 `growth_service.py` 中的 `get_leaderboard` 方法，使用 `ClassAssistantService.get_user_assistant_classes` 获取班级助理被授权的班级，并与导师自己的班级合并

### 17. 排行榜显示范围逻辑

**问题描述**：
排行榜显示的学员范围与学员管理不一致。

**原因**：
- 排行榜默认只显示 `BindStatus.APPROVED` 状态的学员
- 用户要求同时显示 `BindStatus.NONE`（导师导入的学员）和 `BindStatus.APPROVED`（已绑定的学员）

**解决方案**：
- 修改 `growth_service.py` 中的 `get_leaderboard` 方法，将默认过滤条件改为：
  ```python
  query = query.where(
      ClassStudent.bind_status.in_([BindStatus.APPROVED, BindStatus.NONE]),
      ClassStudent.is_active == True
  )
  ```

### 18. 排行榜总成长值过滤逻辑

**问题描述**：
用户要求显示总成长值大于0和小于0的学员，只有等于0的不显示。

**原因**：
- 原条件 `total_score > 0` 不会显示负成长值的学员

**解决方案**：
- 修改 `growth_service.py` 中的 `get_leaderboard` 方法，将条件从 `if total_score > 0:` 改为 `if total_score != 0:`

### 19. 助理绑定班级路径错误

**问题描述**：
助理点击"绑定班级"时，调用了 `/api/v1/student/bind` 接口（缺少 s），且使用了错误的角色身份。

**原因**：
- 前端调用路径错误：`/api/v1/student/bind` → 应为 `/api/v1/students/bind`
- 助理页面不应该直接绑定班级，应该跳转到学员页面

**解决方案**：
- 修改 `Home.vue`、`AssistantHome.vue`、`AssistantLayout.vue` 中的路径：`/api/v1/student/bind` → `/api/v1/students/bind`
- 修改 `AssistantHome.vue` 和 `AssistantLayout.vue` 中的 `openBindClassModal` 函数，跳转到 `/student` 页面进行绑定

### 20. 学员工作台显示名字不正确

**问题描述**：
学员工作台左上角显示的是账号名字（如"沈助理"），而不是学员在班级中的名字（如"甘音希"）。

**原因**：
- 后端 `get_my_classes` 接口返回的是 `student_profile.real_name`（账号名字），而不是学员在班级中的名字（`name_in_class`）
- 前端 API 路径错误：使用了 `/api/v1/student/my-classes` 而不是 `/api/v1/students/my-classes`

**解决方案**：
- 修改 `student.py` 文件中的 `get_my_classes` 方法，将 `student_name` 字段从 `student_profile.real_name` 改为 `binding.name_in_class or student_profile.real_name`
- 修改所有前端文件中的 API 路径，将 `/api/v1/student/my-classes` 改为 `/api/v1/students/my-classes`
  - StudentLayout.vue
  - RoleSelection.vue
  - AssistantLayout.vue
  - AssistantHome.vue
  - Home.vue (mobile/student)

### 21. 角色选择页面只显示一个身份选项

**问题描述**：
角色选择页面只显示一个身份选项，无法同时显示学员和助理身份。

**原因**：
- 前端 `checkRoles` 函数中，API 路径错误导致无法正确获取绑定班级信息
- 逻辑判断不完善，未正确处理学员角色和绑定班级状态

**解决方案**：
- 修改 `RoleSelection.vue` 中的 `checkRoles` 函数，使用正确的 API 路径 `/api/v1/students/my-classes`
- 优化角色判断逻辑，同时检查用户角色和绑定班级状态

### 22. 后端缺少 select 函数导入

**问题描述**：
导师批准学员绑定申请时，出现 `name 'select' is not defined` 错误。

**原因**：
- `student.py` 文件的 `approve_bind` 函数中使用了 `select` 函数，但没有导入它

**解决方案**：
- 在 `approve_bind` 函数内部添加 `from sqlalchemy import select` 导入语句

## 总结

通过以上修复，所有页面的功能都应该能够正常工作了：
- 成长管理页面的成长记录能够正常显示
- 班级管理、学员管理、首页等页面都能够正常显示数据
- 成长日志和标签管理页面能够正常显示数据
- 学员管理添加学员弹窗中，班级选择能够显示完整的班级信息
- 添加学员时，`class_student` 表的 `bind_status` 字段能够正确填写
- 学员管理页面的搜索和筛选功能能够正常工作
- 级的筛选和班级的筛选功能能够正常工作
- 登录页面能够正常获取验证码
- `class_student` 表的 `bind_status` 字段包含 `none` 选项
- 班级管理页面能够正确显示学员数
- 程序记录的时间与实际操作时间一致
- 导师成长排行能够正常显示学员数据
- 班级助理能够查看被授权班级的排行榜数据
- 排行榜正确显示 `BindStatus.NONE` 和 `BindStatus.APPROVED` 状态的学员
- 排行榜正确显示总成长值大于0和小于0的学员，只有等于0的不显示
- 学员工作台左上角显示正确的学员名字（从绑定班级信息中获取）
- 角色选择页面能够同时显示学员和助理身份选项
- 导师能够正常批准学员绑定申请
- 添加成长值时能够正确传递 `class_id` 字段
- 学员能够正常查看自己的成长值变动记录
- 导师兑换管理页面能够正常显示订单数据
- 已完成页面只显示已完成/已取消的订单
- 操作时间能够正确显示，不再显示 "Invalid Date"
- 已完成页面数字在页面加载时就显示，无需点击选项卡
- 已完成页面数据从 `gift_order_log` 表正确加载
- 学员页面排名显示所在班的排名，样式同导师页面，自己总成长值为0时显示自己
- 助理身份和学员身份的成长记录正确过滤：助理查看自己操作的记录，学员查看自己被加减的记录
- 意见征集功能统一：学员和助理都可以查看他人发帖，管理自己的发帖
- 导师首页布局调整完成：订单处理和绑定待审核移至第二行

### 23. 添加成长值时出现 422 Unprocessable Content 错误

**问题描述**：
添加成长值时出现 422 Unprocessable Content 错误，提示请求数据不符合验证规则。

**原因**：
前端发送的请求数据缺少 `class_id` 字段，而根据 `GrowthLogCreate` 模型，`class_id` 是必填字段。

**解决方案**：
- 修改 `GrowthList.vue` 文件中的 `handleAddGrowth` 函数，在请求数据中添加 `class_id` 字段：
  ```javascript
  const response = await request.post('/api/v1/growth/record', {
    student_name: selectedStudent.real_name,
    class_id: parseInt(growthForm.value.class_id), // 添加 class_id 字段
    change_score: score,
    reason: reason,
    input_type: 1,
  });
  ```

### 24. 学员看不到成长值变动记录

**问题描述**：
学员登录后查看成长值页面，只能看到可用成长值和累计成长值，但看不到具体的成长值变动记录。

**原因**：
1. 第一次修复：在 `GrowthService.get_growth_logs` 方法中，当用户不是导师时（即学员或班级助理），`only_own_records` 被设置为 `True`，导致查询只返回 `operator_id` 等于当前用户ID的记录。但学员的成长值记录通常是由导师或助理添加的，所以 `operator_id` 不是学员自己的ID，导致学员看不到自己的成长值记录。

2. 第二次修复：当用户是学员时，代码会尝试获取班级列表，但学员没有自己的班级，所以 `class_ids` 会是空的，导致查询返回空结果。

3. 第三次修复：当导师添加新的成长值记录后，没有清除成长值日志的缓存，导致学员的缓存仍然是旧的，看不到新的记录。

4. 第四次修复：`PermissionChecker.require_growth_permission` 方法只允许导师和班级助理访问成长值相关接口，学员被拒绝访问。

5. 第五次修复：在 `GrowthService.get_growth_logs` 方法中，查询 `ClassStudent` 时只选择了 `id` 字段，导致 `student_class` 是一个整数而不是对象，无法访问 `student_class.id` 属性。

6. 第六次修复：在 `get_growth_logs` 方法中，当学员有自己的 `student_class` 记录时，代码进入了 `if only_own_records and student_class:` 分支，但在后续代码中使用了 `class_ids` 变量，而这个变量只在 `else` 分支中被定义，导致报错：`cannot access local variable 'class_ids' where it is not associated with a value`。

**解决方案**：
- 第一次修复：修改 `growth_service.py` 文件中的 `get_growth_logs` 方法，区分学员和班级助理的查询逻辑：
  ```python
  # 对于班级助理，只显示自己的记录
  # 对于学员，只显示与自己相关的记录（基于class_student_id）
  if only_own_records:
      # 检查用户是否是学员
      from app.models.student_profile import StudentProfile
      from app.models.class_student import ClassStudent
      
      # 查找当前用户对应的ClassStudent记录
      student_class_result = await db.execute(
          select(ClassStudent.id).join(
              StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
          ).where(
              StudentProfile.user_id == teacher_id
          )
      )
      student_class = student_class_result.scalar_one_or_none()
      
      if student_class:
          # 如果是学员，只显示与自己相关的记录
          query = query.where(Growth.class_student_id == student_class.id)
      else:
          # 如果是班级助理，只显示自己添加的记录
          query = query.where(Growth.operator_id == teacher_id)
  ```

- 第二次修复：重构 `get_growth_logs` 方法，对于学员直接根据 `class_student_id` 过滤，不依赖班级列表：
  ```python
  # 对于学员，直接根据class_student_id过滤，不依赖班级列表
  if only_own_records and student_class:
      # 如果是学员，只显示与自己相关的记录
      query = query.where(Growth.class_student_id == student_class.id)
  else:
      # 对于导师和班级助理，需要根据班级列表过滤
      # ... 原有班级过滤逻辑 ...
  ```

- 第三次修复：在 `record_growth_log` 方法中添加清除成长值日志缓存的逻辑：
  ```python
  # 清除成长值日志缓存
  await cache.clear_pattern(f"growth_logs:*")
  ```

- 第四次修复：修改 `PermissionChecker.require_growth_permission` 方法，允许学员访问成长值相关接口：
  ```python
  # 检查用户是否是学员
  from app.models.student_profile import StudentProfile
  from app.models.class_student import ClassStudent
  from sqlalchemy import select
  
  student_class_result = await db.execute(
      select(ClassStudent.id).join(
          StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
      ).where(
          StudentProfile.user_id == user.id
      )
  )
  is_student = student_class_result.scalar_one_or_none() is not None
  
  if not (is_teacher or is_assistant or is_student):
      raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="无权限操作成长值"
      )
  ```

- 第五次修复：修改 `GrowthService.get_growth_logs` 方法，查询完整的 `ClassStudent` 对象：
  ```python
  # 查找当前用户对应的ClassStudent记录
  student_class_result = await db.execute(
      select(ClassStudent).join(
          StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
      ).where(
          StudentProfile.user_id == teacher_id
      )
  )
  student_class = student_class_result.scalar_one_or_none()
  ```

- 第六次修复：删除 `get_growth_logs` 方法中第598行的 `logger.info(f"[DEBUG] Class IDs: {class_ids}")`，避免使用未定义的变量：
  ```python
  # 原来的代码（会导致错误）
  logger.info(f"[DEBUG] Class IDs: {class_ids}")
  
  # 修改后的代码（删除了这行）
  # 删除了这行调试日志，避免使用未定义的变量
  ```

## 注意事项

1. **API 路径一致性**：所有前端页面的 API 调用路径都应该使用 `/api/v1/` 前缀
2. **参数类型匹配**：前端传递的参数类型应该与后端期望的参数类型匹配
3. **响应格式处理**：前端应该正确处理后端 API 返回的响应格式
4. **缓存管理**：对于频繁变化的数据，应该谨慎使用缓存，或确保缓存能够及时更新
5. **错误处理**：应该添加适当的错误处理，确保系统能够优雅地处理错误情况
6. **时间处理**：使用 `datetime.now()` 而不是 `datetime.utcnow()` 来记录本地时间
7. **枚举值处理**：在 SQLAlchemy 中使用枚举时，注意传递正确的枚举值格式
8. **请求数据完整性**：确保前端发送的请求数据包含所有后端模型要求的必填字段

### 25. 导师兑换管理没有数据显示

**问题描述**：
导师兑换管理页面没有数据显示，API 返回空数组或错误。

**原因**：
- `get_orders` 函数中 `total` 变量可能为 `None`，导致 JSON 序列化错误
- 前端 API 调用参数或路径错误
- `gift_order` 表结构与模型定义不匹配，缺少 `teacher_id` 字段
- 异步代码中访问懒加载关系导致 `sqlalchemy.exc.MissingGreenlet` 错误

**解决方案**：
- 修复 `get_orders` 函数，将 `total = (await db.execute(count_query)).scalar()` 修改为 `total = (await db.execute(count_query)).scalar() or 0`
- 确认前端调用路径为 `/api/v1/orders/`，参数包含 `class_id` 和 `status`
- 修复 `gift_order` 表结构，添加缺失的 `teacher_id` 字段
- 在查询 `ClassStudent` 时使用 `selectinload` 预加载 `student_profile` 和 `user` 关系

### 26. 已完成页面的数据显示问题

**问题描述**：
已完成页面显示了所有订单，包括待处理的订单。

**原因**：
- `get_orders` 函数没有过滤订单状态，导致返回所有订单

**解决方案**：
- 修改 `get_orders` 函数，添加状态过滤逻辑，确保只返回待处理的订单（状态为 0 或 1）
- 保持 `get_completed_orders` 函数的逻辑不变，继续返回已完成和已取消的订单

### 27. 操作时间显示为 Invalid Date 的问题

**问题描述**：
已完成页面的操作时间显示为 "Invalid Date"。

**原因**：
- 前端已完成页面模板使用 `order.operated_at` 字段来渲染操作时间，但后端 `get_completed_orders` 函数返回的是 `updated_at` 字段，字段名不一致导致前端无法正确获取时间数据

**解决方案**：
- 修改后端 `get_completed_orders` 函数，将返回字段中的 `updated_at` 改名为 `operated_at`，确保与前端模板使用的字段名一致

### 28. 已完成页面数字显示问题

**问题描述**：
已完成页面的数字显示有问题，需要点击已完成选项卡后数字才会显示。

**原因**：
- `completedCount` 只在 `fetchCompletedOrders` 函数中计算，而这个函数只在用户点击 "已完成" 选项卡时才会被调用

**解决方案**：
- 修改前端代码，在组件挂载和激活时同时调用 `fetchCompletedOrders` 函数，确保 `completedCount` 在页面加载时就被计算

### 29. 已完成页面数据从 gift_order_log 加载

**问题描述**：
已完成页面的数据应该从 `gift_order_log` 表中加载，而不是从 `gift_order` 表中加载。

**原因**：
- `get_completed_orders` 函数从 `gift_order` 表中查询数据，而不是从 `gift_order_log` 表中查询

**解决方案**：
- 修改 `get_completed_orders` 函数，将其改回从 `gift_order_log` 表中查询数据
- 在查询 `ClassStudent` 时使用 `selectinload` 预加载 `student_profile` 和 `user` 关系，解决异步加载关系时的 `MissingGreenlet` 错误

### 30. 学员页面排名显示问题

**问题描述**：
学员页面的排名显示有问题，需要显示所在班的排名，样式同导师页面，如果自己总成长值为0，也要显示自己，不显示总成长值为0的其他人。

**原因**：
- 后端 `get_leaderboard` 函数没有特殊处理总成长值为0的当前用户
- 前端 API 调用路径错误
- 前端缺少空值检查，导致在 `selectedClassId` 为 `null` 或 `undefined` 时尝试访问不存在的 API 路径

**解决方案**：
- 修改后端 `get_leaderboard` 函数，确保当前用户即使总成长值为0也能显示在排名中，同时不显示总成长值为0的其他学员
- 修正前端 API 调用路径，将排名接口的调用路径从 `/api/v1/leaderboard/class` 改为 `/api/v1/growth/leaderboard/class/` + selectedClassId.value
- 在 `fetchRankList` 函数中添加空值检查，确保只在 `selectedClassId.value` 存在时才调用 API
- 修改前端排名页面的样式，使其与导师页面一致，包括添加特殊的排名图标和背景色
