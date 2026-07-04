<script setup>
import { ref, onMounted } from 'vue'
import { getAllReservations, adminCancelReservation, restoreReservation } from '../../api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const reservations = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const searchForm = ref({
  status: undefined,
  username: '',
  room_no: ''
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
    const res = await getAllReservations({
      page: page.value,
      ...searchForm.value
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
    await ElMessageBox.confirm('确定要强制取消该预订吗？', '提示', { type: 'warning' })
    await adminCancelReservation(row.reservation_id)
    ElMessage.success('取消成功')
    fetchReservations()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const handleRestore = async (row) => {
  try {
    await restoreReservation(row.reservation_id)
    ElMessage.success('恢复成功')
    fetchReservations()
  } catch (error) {
    console.error(error)
  }
}

const handleSearch = () => {
  page.value = 1
  fetchReservations()
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
          <span>预订管理</span>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户账号">
          <el-input v-model="searchForm.username" placeholder="用户账号" clearable />
        </el-form-item>
        <el-form-item label="教室编号">
          <el-input v-model="searchForm.room_no" placeholder="教室编号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="已取消" :value="0" />
            <el-option label="待审核" :value="1" />
            <el-option label="已确认" :value="2" />
            <el-option label="已驳回" :value="3" />
            <el-option label="已完成" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="reservations" v-loading="loading" border>
        <el-table-column prop="reservation_id" label="ID" width="80" />
        <el-table-column prop="user.username" label="用户" width="100" />
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
              v-if="[1, 2].includes(row.status)"
              type="danger"
              size="small"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button
              v-if="row.status === 0"
              type="success"
              size="small"
              @click="handleRestore(row)"
            >
              恢复
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
  </div>
</template>
