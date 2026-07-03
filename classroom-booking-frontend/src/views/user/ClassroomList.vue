<template>
  <div>
    <!-- 筛选区 -->
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">空闲教室查询</span>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
        </div>
      </template>
      <el-form :model="queryForm" inline>
        <el-form-item label="预订日期">
          <el-date-picker v-model="queryForm.reserve_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 150px" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker v-model="queryForm.start_time" placeholder="开始时间" format="HH:mm" value-format="HH:mm" style="width: 120px" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker v-model="queryForm.end_time" placeholder="结束时间" format="HH:mm" value-format="HH:mm" style="width: 120px" />
        </el-form-item>
        <el-form-item label="最小容量">
          <el-input-number v-model="queryForm.min_capacity" :min="1" placeholder="容量" style="width: 120px" />
        </el-form-item>
        <el-form-item label="楼层">
          <el-select v-model="queryForm.floor" placeholder="不限" clearable style="width: 100px">
            <el-option v-for="f in [1,2,3,4,5]" :key="f" :label="`${f}楼`" :value="f" />
          </el-select>
        </el-form-item>
        <el-form-item label="设施">
          <el-checkbox v-model="queryForm.has_projector">投影仪</el-checkbox>
          <el-checkbox v-model="queryForm.has_whiteboard">白板</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果区 -->
    <el-card shadow="never" class="page-card" style="margin-top: 16px" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="page-title">查询结果</span>
          <span class="result-count">共 {{ classrooms.length }} 间空闲教室</span>
        </div>
      </template>
      <el-empty v-if="!loading && classrooms.length === 0" description="暂无空闲教室，请调整筛选条件" />
      <el-row :gutter="20" v-else>
        <el-col :xs="24" :sm="12" :md="8" v-for="item in classrooms" :key="item.classroom_id" style="margin-bottom: 20px">
          <el-card shadow="hover" class="room-card">
            <template #header>
              <div class="room-header">
                <span class="room-no">{{ item.room_no }}</span>
                <el-tag size="small" type="success">空闲</el-tag>
              </div>
            </template>
            <div class="room-info">
              <p><el-icon><OfficeBuilding /></el-icon> 楼层：{{ item.floor }}楼</p>
              <p><el-icon><User /></el-icon> 容量：{{ item.capacity }}人</p>
              <p>
                <el-icon><Monitor /></el-icon> 投影仪：
                <el-tag size="small" :type="item.has_projector ? 'success' : 'info'">{{ item.has_projector ? '有' : '无' }}</el-tag>
              </p>
              <p>
                <el-icon><EditPen /></el-icon> 白板：
                <el-tag size="small" :type="item.has_whiteboard ? 'success' : 'info'">{{ item.has_whiteboard ? '有' : '无' }}</el-tag>
              </p>
              <p v-if="item.facility_remark" class="remark">备注：{{ item.facility_remark }}</p>
            </div>
            <el-button type="primary" @click="openBookDialog(item)" style="width: 100%; margin-top: 12px">立即预订</el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 预订弹窗 -->
    <el-dialog v-model="bookDialogVisible" title="预订教室" width="500px" align-center destroy-on-close>
      <el-form :model="bookForm" :rules="bookRules" ref="bookRef" label-width="100px">
        <el-form-item label="教室">
          <span class="form-static">{{ selectedRoom?.room_no }}</span>
        </el-form-item>
        <el-form-item label="预订日期" prop="reserve_date">
          <el-date-picker v-model="bookForm.reserve_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="bookForm.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="bookForm.end_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预订用途" prop="purpose">
          <el-input v-model="bookForm.purpose" type="textarea" rows="3" maxlength="200" show-word-limit placeholder="请填写预订用途" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBooking" :loading="bookingLoading">提交预订</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { findFreeClassrooms } from '@/api/classroom'
import { createReservation } from '@/api/reservation'
import { ElMessage } from 'element-plus'
import { Search, OfficeBuilding, User, Monitor, EditPen } from '@element-plus/icons-vue'

const loading = ref(false)
const classrooms = ref([])
const queryForm = ref({
  reserve_date: '',
  start_time: '',
  end_time: '',
  min_capacity: undefined,
  floor: undefined,
  has_projector: false,
  has_whiteboard: false
})

const bookDialogVisible = ref(false)
const bookingLoading = ref(false)
const selectedRoom = ref(null)
const bookRef = ref()
const bookForm = ref({
  classroom_id: null,
  reserve_date: '',
  start_time: '',
  end_time: '',
  purpose: ''
})
const bookRules = {
  reserve_date: [{ required: true, message: '请选择预订日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请填写预订用途', trigger: 'blur' }]
}

const handleQuery = async () => {
  loading.value = true
  try {
    const params = {}
    if (queryForm.value.reserve_date) params.reserve_date = queryForm.value.reserve_date
    if (queryForm.value.start_time) params.start_time = queryForm.value.start_time
    if (queryForm.value.end_time) params.end_time = queryForm.value.end_time
    if (queryForm.value.min_capacity) params.min_capacity = queryForm.value.min_capacity
    if (queryForm.value.floor) params.floor = queryForm.value.floor
    if (queryForm.value.has_projector) params.has_projector = 1
    if (queryForm.value.has_whiteboard) params.has_whiteboard = 1
    const res = await findFreeClassrooms(params)
    classrooms.value = res.data
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  queryForm.value = {
    reserve_date: '',
    start_time: '',
    end_time: '',
    min_capacity: undefined,
    floor: undefined,
    has_projector: false,
    has_whiteboard: false
  }
  classrooms.value = []
}

const openBookDialog = (room) => {
  selectedRoom.value = room
  bookForm.value = {
    classroom_id: room.classroom_id,
    reserve_date: queryForm.value.reserve_date || '',
    start_time: queryForm.value.start_time || '',
    end_time: queryForm.value.end_time || '',
    purpose: ''
  }
  bookDialogVisible.value = true
}

const submitBooking = async () => {
  await bookRef.value.validate()
  if (bookForm.value.end_time <= bookForm.value.start_time) {
    ElMessage.warning('结束时间必须晚于开始时间')
    return
  }
  bookingLoading.value = true
  try {
    await createReservation(bookForm.value)
    ElMessage.success('预订成功')
    bookDialogVisible.value = false
    handleQuery()
  } finally {
    bookingLoading.value = false
  }
}

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  queryForm.value.reserve_date = today
  queryForm.value.start_time = '08:00'
  queryForm.value.end_time = '18:00'
  handleQuery()
})
</script>

<style scoped>

.result-count {
  font-size: 14px;
  color: #64748b;
}
.room-card {
  border-radius: 4px;
}
.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.room-no {
  font-size: 18px;
  font-weight: bold;
  color: #1e293b;
}
.room-info p {
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
  font-size: 14px;
}
.remark {
  color: #64748b;
  font-size: 12px;
}
.form-static {
  font-size: 14px;
  color: #475569;
}
</style>
