<script setup>
import { ref, onMounted } from 'vue'
import { getClassroomList, getFreeClassrooms } from '../../api/classroom'
import { createReservation } from '../../api/reservation'
import { ElMessage, ElMessageBox } from 'element-plus'

const classrooms = ref([])
const loading = ref(false)
const searchForm = ref({
  reserve_date: '',
  start_time: '',
  end_time: '',
  min_capacity: undefined,
  has_projector: undefined,
  has_whiteboard: undefined
})

const reservationDialogVisible = ref(false)
const reservationForm = ref({
  classroom_id: null,
  reserve_date: '',
  start_time: '',
  end_time: '',
  purpose: ''
})

const fetchClassrooms = async () => {
  loading.value = true
  try {
    const res = await getClassroomList({ status: 1 })
    classrooms.value = res.data.items
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const searchFreeClassrooms = async () => {
  if (!searchForm.value.reserve_date || !searchForm.value.start_time || !searchForm.value.end_time) {
    ElMessage.warning('请填写完整的查询条件')
    return
  }

  loading.value = true
  try {
    const res = await getFreeClassrooms(searchForm.value)
    classrooms.value = res.data
    ElMessage.success(`找到 ${res.data.length} 间空闲教室`)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openReservationDialog = (classroom) => {
  reservationForm.value = {
    classroom_id: classroom.classroom_id,
    reserve_date: searchForm.value.reserve_date || '',
    start_time: searchForm.value.start_time || '',
    end_time: searchForm.value.end_time || '',
    purpose: ''
  }
  reservationDialogVisible.value = true
}

const submitReservation = async () => {
  if (!reservationForm.value.purpose) {
    ElMessage.warning('请填写预订用途')
    return
  }

  try {
    await createReservation(reservationForm.value)
    ElMessage.success('预订成功')
    reservationDialogVisible.value = false
  } catch (error) {
    console.error(error)
  }
}

const formatFacility = (row) => {
  const facilities = []
  if (row.has_projector) facilities.push('投影仪')
  if (row.has_whiteboard) facilities.push('白板')
  if (row.facility_remark) facilities.push(row.facility_remark)
  return facilities.join('、') || '无'
}

onMounted(() => {
  fetchClassrooms()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教室查询</span>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="预订日期">
          <el-date-picker
            v-model="searchForm.reserve_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="searchForm.start_time"
            placeholder="开始时间"
            value-format="HH:mm"
            format="HH:mm"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker
            v-model="searchForm.end_time"
            placeholder="结束时间"
            value-format="HH:mm"
            format="HH:mm"
          />
        </el-form-item>
        <el-form-item label="最小容量">
          <el-input-number v-model="searchForm.min_capacity" :min="1" placeholder="容量" />
        </el-form-item>
        <el-form-item label="投影仪">
          <el-select v-model="searchForm.has_projector" placeholder="不限" clearable>
            <el-option label="有" :value="1" />
            <el-option label="无" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchFreeClassrooms">查询空闲教室</el-button>
          <el-button @click="fetchClassrooms">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="classrooms" v-loading="loading" border>
        <el-table-column prop="room_no" label="教室编号" width="100" />
        <el-table-column prop="floor" label="楼层" width="80" />
        <el-table-column prop="capacity" label="容量" width="80" />
        <el-table-column label="设施" :formatter="formatFacility" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openReservationDialog(row)">
              预订
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Reservation Dialog -->
    <el-dialog v-model="reservationDialogVisible" title="预订教室" width="500px">
      <el-form :model="reservationForm" label-width="100px">
        <el-form-item label="预订日期">
          <el-date-picker
            v-model="reservationForm.reserve_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="reservationForm.start_time"
            placeholder="开始时间"
            value-format="HH:mm"
            format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker
            v-model="reservationForm.end_time"
            placeholder="结束时间"
            value-format="HH:mm"
            format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预订用途">
          <el-input
            v-model="reservationForm.purpose"
            type="textarea"
            placeholder="请填写预订用途"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reservationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReservation">确认预订</el-button>
      </template>
    </el-dialog>
  </div>
</template>
