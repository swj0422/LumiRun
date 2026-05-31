"""
测试登录脚本
验证新的默认账号（manager）是否能正常登录
"""
import asyncio
import sys
import httpx


BASE_URL = "http://localhost:8084"


async def test_manager_login():
    """测试 manager 账号登录"""
    print("\n" + "=" * 50)
    print("测试 manager 账号登录")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "username": "manager",
                    "password": "Password123"
                }
            )

            print(f"\n请求URL: {BASE_URL}/api/v1/auth/login")
            print(f"请求体: {{'username': 'manager', 'password': 'Password123'}}")
            print(f"响应状态: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("\n✅ manager 账号登录成功！")
                    print(f"获取到的 Token: {data['access_token'][:50]}...")
                    return True
                else:
                    print("\n❌ manager 账号登录失败：未获取到 access_token")
                    return False
            else:
                print(f"\n❌ manager 账号登录失败：HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            return False


async def test_member_login():
    """测试 member 账号登录"""
    print("\n" + "=" * 50)
    print("测试 member 账号登录")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "username": "member",
                    "password": "Password123"
                }
            )

            print(f"\n请求URL: {BASE_URL}/api/v1/auth/login")
            print(f"请求体: {{'username': 'member', 'password': 'Password123'}}")
            print(f"响应状态: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("\n✅ member 账号登录成功！")
                    print(f"获取到的 Token: {data['access_token'][:50]}...")
                    return True
                else:
                    print("\n❌ member 账号登录失败：未获取到 access_token")
                    return False
            else:
                print(f"\n❌ member 账号登录失败：HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            return False


async def test_admin_login():
    """测试 admin 账号登录"""
    print("\n" + "=" * 50)
    print("测试 admin 账号登录")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "username": "admin",
                    "password": "Password123"
                }
            )

            print(f"\n请求URL: {BASE_URL}/api/v1/auth/login")
            print(f"请求体: {{'username': 'admin', 'password': 'Password123'}}")
            print(f"响应状态: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("\n✅ admin 账号登录成功！")
                    print(f"获取到的 Token: {data['access_token'][:50]}...")
                    return True
                else:
                    print("\n❌ admin 账号登录失败：未获取到 access_token")
                    return False
            else:
                print(f"\n❌ admin 账号登录失败：HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            return False


async def main():
    print("\n" + "#" * 50)
    print("# LumiRun 登录测试脚本")
    print("#" * 50)
    print("\n测试新的默认账号:")
    print("  - admin@example.com / admin / Password123 (超级管理员)")
    print("  - manager@example.com / manager / Password123 (管理者)")
    print("  - member@example.com / member / Password123 (成员)")

    results = {}

    results["admin"] = await test_admin_login()
    results["manager"] = await test_manager_login()
    results["member"] = await test_member_login()

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    all_passed = True
    for account, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {account}: {status}")
        if not success:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("\n🎉 所有账号登录测试通过！")
        return 0
    else:
        print("\n⚠️ 部分账号登录测试失败，请检查后端服务和数据库初始化")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
