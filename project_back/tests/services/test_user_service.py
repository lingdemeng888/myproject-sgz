import unittest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import BusinessException
from app.models import user_role  # noqa: F401  # ensures association table is registered
from app.models.base import Base
from app.models.department import Department
from app.models.major import Major
from app.models.role import Role
from app.schemas.user import StudentRegisterRequest
from app.services.user_service import UserService


class RegisterStudentServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self._create_student_role()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _create_student_role(self):
        role = Role(role_key="STUDENT", name="学生")
        self.db.add(role)
        self.db.commit()
        self.student_role_id = role.id

    def _create_department(self, *, status: int = 1) -> Department:
        dept = Department(
            dept_code=f"DEPT-{uuid.uuid4().hex[:6]}",
            name="测试院系",
            status=status
        )
        self.db.add(dept)
        self.db.commit()
        return dept

    def _create_major(self, department: Department, *, status: int = 1) -> Major:
        major = Major(
            department_id=department.id,
            major_code=f"MAJ-{uuid.uuid4().hex[:6]}",
            name="测试专业",
            status=status
        )
        self.db.add(major)
        self.db.commit()
        return major

    def _build_request(self, *, primary_major_id: int, username_suffix: str) -> StudentRegisterRequest:
        return StudentRegisterRequest(
            username=f"student_{username_suffix}",
            real_name="测试学生",
            student_no=f"SN{username_suffix}",
            phone=f"1380000{username_suffix:0>4}",
            password="Secret123",
            primary_major_id=primary_major_id,
            email=f"student_{username_suffix}@example.com"
        )

    def test_register_student_sets_department_id(self):
        dept = self._create_department(status=1)
        major = self._create_major(department=dept, status=1)

        request = self._build_request(primary_major_id=major.id, username_suffix="0001")
        user = UserService.register_student(self.db, request)

        self.assertEqual(user.primary_major_id, major.id)
        self.assertEqual(user.department_id, dept.id)

    def test_register_student_rejects_disabled_major(self):
        dept = self._create_department(status=1)
        major = self._create_major(department=dept, status=0)

        request = self._build_request(primary_major_id=major.id, username_suffix="0002")

        with self.assertRaises(BusinessException) as ctx:
            UserService.register_student(self.db, request)

        self.assertIn("主修专业已被禁用", str(ctx.exception.code))

    def test_register_student_rejects_disabled_department(self):
        dept = self._create_department(status=0)
        major = self._create_major(department=dept, status=1)

        request = self._build_request(primary_major_id=major.id, username_suffix="0003")

        with self.assertRaises(BusinessException) as ctx:
            UserService.register_student(self.db, request)

        self.assertIn("院系", str(ctx.exception.code))


if __name__ == "__main__":
    unittest.main()
