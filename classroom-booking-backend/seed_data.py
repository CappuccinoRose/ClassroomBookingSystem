import os
os.environ['DATABASE_URL'] = 'sqlite:///classroom_booking.db'
os.environ['JWT_SECRET_KEY'] = 'jwt-secret-key-for-classroom-booking'
os.environ['SECRET_KEY'] = 'classroom-booking-secret-key-2024'

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.classroom import Classroom
from app.models.reservation import Reservation
from app.models.approval import Approval
from app.models.periodic_rule import PeriodicRule
from datetime import datetime, date, time, timedelta
import bcrypt
import random

app = create_app()
app.app_context().push()

print("Clearing existing data...")
db.session.query(Approval).delete()
db.session.query(Reservation).delete()
db.session.query(PeriodicRule).delete()
db.session.query(Classroom).delete()
db.session.query(User).delete()
db.session.commit()

print("Creating users...")
users = []
for i in range(1, 11):
    pw = bcrypt.hashpw(f'password{i}'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=f'user{i}', password_hash=pw, email=f'user{i}@example.com', role=0, status=1)
    db.session.add(user)
    users.append(user)

admin_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
admin = User(username='admin', password_hash=admin_pw, email='admin@example.com', role=1, status=1)
db.session.add(admin)
db.session.commit()
print(f"Created {len(users)} users and 1 admin")

print("Creating classrooms...")
classroom_data = [
    ('101', 1, 30, 1, 1, '靠近电梯'),
    ('102', 1, 50, 1, 0, '多媒体教室'),
    ('103', 1, 40, 0, 1, '讨论室'),
    ('201', 2, 60, 1, 1, '大型阶梯教室'),
    ('202', 2, 35, 1, 0, '普通教室'),
    ('203', 2, 45, 0, 1, '白板会议室'),
    ('301', 3, 80, 1, 1, '报告厅'),
    ('302', 3, 25, 0, 0, '小型研讨室'),
    ('303', 3, 55, 1, 1, '综合教室'),
    ('401', 4, 100, 1, 1, '学术报告厅'),
    ('402', 4, 20, 0, 0, '辅导室'),
    ('501', 5, 70, 1, 1, '实验教室'),
]
classrooms = []
for room_no, floor, capacity, proj, wb, remark in classroom_data:
    c = Classroom(room_no=room_no, floor=floor, capacity=capacity,
                  has_projector=proj, has_whiteboard=wb, facility_remark=remark, status=1)
    db.session.add(c)
    classrooms.append(c)
db.session.commit()
print(f"Created {len(classrooms)} classrooms")

print("Creating reservations...")
reservations = []
base_date = date.today()
purposes = ['数学研讨', '英语角', '物理实验', '化学课', '编程培训', '班会',
            '学术报告', '社团活动', '考研复习', '面试准备', '项目答辩', '论文指导']

for i in range(200):
    user = random.choice(users)
    classroom = random.choice(classrooms)
    day_offset = random.randint(-10, 60)
    reserve_date = base_date + timedelta(days=day_offset)
    start_hour = random.choice([8, 9, 10, 14, 15, 16, 18, 19])
    start = time(start_hour, random.choice([0, 30]))
    end = time(start_hour + random.choice([1, 2, 3]), random.choice([0, 30]))
    status = random.choices([0, 1, 2, 3, 4], weights=[15, 10, 50, 10, 15])[0]
    r = Reservation(
        user_id=user.user_id,
        classroom_id=classroom.classroom_id,
        reserve_date=reserve_date,
        start_time=start,
        end_time=end,
        purpose=random.choice(purposes),
        status=status
    )
    db.session.add(r)
    reservations.append(r)
db.session.commit()
print(f"Created {len(reservations)} reservations")

print("Creating approvals...")
approvals = []
for r in reservations:
    if r.status in [2, 3]:
        result = 1 if r.status == 2 else 2
        a = Approval(
            reservation_id=r.reservation_id,
            admin_id=admin.user_id,
            result=result,
            opinion='审批通过' if result == 1 else '时段冲突，驳回',
            approval_time=datetime.now()
        )
        db.session.add(a)
        approvals.append(a)
db.session.commit()
print(f"Created {len(approvals)} approvals")

print("Creating periodic rules...")
rules = []
periodic_purposes = ['高等数学', '大学英语', '线性代数', '数据结构', '操作系统',
                     '计算机网络', '数据库原理', '软件工程', '人工智能', '机器学习',
                     '每周例会', '学术研讨', '实验课程', '毕业设计', '导师辅导']
# 为admin创建5条周期规则
admin_periodic = [
    (1, 1, '08:00', '10:00', '高等数学'),
    (3, 2, '14:00', '16:00', '大学英语'),
    (5, 3, '10:00', '12:00', '数据结构'),
    (2, 4, '18:00', '20:00', '导师辅导'),
    (4, 5, '09:00', '11:00', '操作系统'),
]
for classroom_id, weekday, st, et, purpose in admin_periodic:
    rule = PeriodicRule(
        user_id=admin.user_id,
        classroom_id=classroom_id,
        weekday=weekday,
        start_time=time(*map(int, st.split(':'))),
        end_time=time(*map(int, et.split(':'))),
        purpose=purpose,
        start_date=base_date - timedelta(days=random.randint(0, 10)),
        end_date=base_date + timedelta(days=random.choice([60, 90, 120])),
        status=1
    )
    db.session.add(rule)
    rules.append(rule)

# 为其他用户创建25条周期规则
for i in range(25):
    user = random.choice(users)
    classroom = random.choice(classrooms)
    weekday = random.randint(1, 7)
    start = time(random.choice([8, 9, 10, 14, 15, 16, 18, 19]), random.choice([0, 30]))
    end = time(min(start.hour + random.choice([1, 2, 3]), 22), random.choice([0, 30]))
    rule = PeriodicRule(
        user_id=user.user_id,
        classroom_id=classroom.classroom_id,
        weekday=weekday,
        start_time=start,
        end_time=end,
        purpose=random.choice(periodic_purposes),
        start_date=base_date - timedelta(days=random.randint(0, 30)),
        end_date=base_date + timedelta(days=random.choice([30, 60, 90, 120, 180])),
        status=random.choice([1, 1, 1, 1, 0])
    )
    db.session.add(rule)
    rules.append(rule)
db.session.commit()
print(f"Created {len(rules)} periodic rules")

print("\n=== Data seeding completed ===")
print(f"Users: {User.query.count()}")
print(f"Classrooms: {Classroom.query.count()}")
print(f"Reservations: {Reservation.query.count()}")
print(f"Approvals: {Approval.query.count()}")
print(f"Periodic Rules: {PeriodicRule.query.count()}")
