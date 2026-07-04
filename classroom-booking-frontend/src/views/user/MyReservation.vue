<script setup>
import { ref, onMounted } from 'vue'
import { getMyReservations, cancelReservation, updateReservation } from '../../api/reservation'
import { ElMessage, ElMessageBox } from 'element-plus'

const reservations = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const statusFilter = ref(undefined)

const editDialogVisible = ref(false)
const editForm = ref({
  reservation_id: null,
  reserve_date: '',
  start_time: '',
  end_time: '',
  purpose: ''
})

const statusMap = {
  0: { label: '已取消', type: 'info' },
  1: { label: '待审核', type: 'warning' },
  2: { label: '已确认', type: 'success' },
  3: { label: '已驳回', type: 'danger' },
  4: { label: '已完成', type: '' }
}

const fetchReservations = async () => {
  loading.value = true
  try {
    const res = await getMyReservations({
      page: page.value,
      status: statusFilter.value
    })
    reservations.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该预订吗？', '提示', {
      type: 'warning'
    })
    await cancelReservation(row.reservation_id)
    ElMessage.success('取消成功')
    fetchReservations()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const openEditDialog = (row) => {
  editForm.value = {
    reservation_id: row.reservation_id,
    reserve_date: row.reserve_date,
    start_time: row.start_time,
    end_time: row.end_time,
    purpose: row.purpose
  }
  editDialogVisible.value = true
}

const submitEdit = async () => {
  try {
    await updateReservation(editForm.value.reservation_id, {
      reserve_date: editForm.value.reserve_date,
      start_time: editForm.value.start_time,
      end_time: editForm.value.end_time,
      purpose: editForm.value.purpose
    })
    ElMessage.success('修改成功')
    editDialogVisible.value = false
    fetchReservations()
  } catch (error) {
    console.error(error)
  }
}

const handlePageChange = (val) => {
  page.value = val
  fetchReservations()
}

const formatDateTime = (date, time) => {
  return `${date} ${time}`
}

onMounted(() => {
  fetchReservations()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的预订</span>
          <el-select v-model="statusFilter" placeholder="筛选状态" clearable @change="fetchReservations">
            <el-option label="已取消" :value="0" />
            <el-option label="待审核" :value="1" />
            <el-option label="已确认" :value="2" />
            <el-option label="已驳回" :value="3" />
            <el-option label="已完成" :value="4" />
          </el-select>
        </div>
      </template>

      <el-table :data="reservations" v-loading="loading" border>
        <el-table-column prop="classroom.room_no" label="教室" width="100" />
        <el-table-column label="日期时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.reserve_date, row.start_time) }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 2"
              type="primary"
              size="small"
              @click="openEditDialog(row)"
            >
              修改
            </el-button>
            <el-button
              v-if="[1, 2].includes(row.status)"
              type="danger"
              size="small"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          :page-size="10"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Edit Dialog -->
    <el-dialog v-model="editDialogVisible" title="修改预订" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="预订日期">
          <el-date-picker
            v-model="editForm.reserve_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="editForm.start_time"
            placeholder="开始时间"
            value-format="HH:mm"
            format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker
            v-model="editForm.end_time"
            placeholder="结束时间"
            value-format="HH:mm"
            format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预订用途">
          <el-input v-model="editForm.purpose" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>
