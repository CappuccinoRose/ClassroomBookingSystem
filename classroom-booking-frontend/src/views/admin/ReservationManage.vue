<template>
  <div>
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">全量预订管理</span>
        </div>
      </template>

      <!-- 筛选区 -->
      <el-form :model="filterForm" inline style="margin-bottom: 8px">
        <el-row :gutter="16" style="width: 100%">
          <el-col :span="5">
            <el-form-item label="用户账号" style="width: 100%; margin-right: 0">
              <el-input v-model="filterForm.username" placeholder="用户账号" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="教室编号" style="width: 100%; margin-right: 0">
              <el-input v-model="filterForm.room_no" placeholder="教室编号" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预订日期" style="width: 100%; margin-right: 0">
              <el-date-picker v-model="filterForm.date_range" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="预订状态" style="width: 100%; margin-right: 0">
              <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 100%">
                <el-option label="已取消" :value="0" />
                <el-option label="待审核" :value="1" />
                <el-option label="已确认" :value="2" />
                <el-option label="已驳回" :value="3" />
                <el-option label="已完成" :value="4" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row style="width: 100%">
          <el-col :span="24" style="display: flex; justify-content: flex-end; align-items: center">
            <el-button type="primary" @click="handleQuery">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-col>
        </el-row>
      </el-form>

      <!-- 表格区 -->
      <el-table :data="reservations" v-loading="loading" stripe border @sort-change="handleSort">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="reservation_id" label="预订ID" width="90" align="center" sortable="custom" />
        <el-table-column prop="user.username" label="用户账号" width="120" align="center" />
        <el-table-column prop="classroom.room_no" label="教室编号" width="100" align="center" />
        <el-table-column prop="reserve_date" label="预订日期" width="120" align="center" sortable="custom" />
        <el-table-column label="时段" width="140" align="center">
          <template #default="{ row }">{{ row.start_time }} ~ {{ row.end_time }}</template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" show-overflow-tooltip min-width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" align="center" sortable="custom">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openView(row)">查看详情</el-button>
            <el-button v-if="[1,2].includes(row.status)" link type="danger" @click="handleCancel(row)">强制取消</el-button>
            <el-button v-if="row.status === 0" link type="success" @click="handleRestore(row)">恢复取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="perPage"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="loadData"
        @size-change="loadData"
      />
    </el-card>

    <!-- 查看弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="预订详情" width="500px" align-center destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="预订ID">{{ currentRow?.reservation_id }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ currentRow?.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="教室">{{ currentRow?.classroom?.room_no }}</el-descriptions-item>
        <el-descriptions-item label="预订日期">{{ currentRow?.reserve_date }}</el-descriptions-item>
        <el-descriptions-item label="时段">{{ currentRow?.start_time }} ~ {{ currentRow?.end_time }}</el-descriptions-item>
        <el-descriptions-item label="用途">{{ currentRow?.purpose }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small" :type="statusType(currentRow?.status)">{{ statusText(currentRow?.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentRow?.create_time) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 取消原因弹窗 -->
    <el-dialog v-model="cancelDialogVisible" title="强制取消预订" width="500px" align-center destroy-on-close>
      <el-form :model="cancelForm" ref="cancelRef" label-width="100px">
        <el-form-item label="预订信息">
          <span>{{ currentRow?.classroom?.room_no }} {{ currentRow?.reserve_date }} {{ currentRow?.start_time }}~{{ currentRow?.end_time }}</span>
        </el-form-item>
        <el-form-item label="取消原因" prop="reason">
          <el-input v-model="cancelForm.reason" type="textarea" rows="3" placeholder="请填写取消原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="submitCancel" :loading="submitting">确认取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listAllReservations, adminCancelReservation, restoreReservation } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const reservations = ref([])
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const filterForm = ref({ username: '', room_no: '', date_range: [], status: '' })
const sortField = ref('')
const sortOrder = ref('')

const viewDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const currentRow = ref(null)
const submitting = ref(false)
const cancelForm = ref({ reason: '' })

const statusMap = { 0: '已取消', 1: '待审核', 2: '已确认', 3: '已驳回', 4: '已完成' }
const statusTypeMap = { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger', 4: 'primary' }
const statusText = (s) => statusMap[s] || '未知'
const statusType = (s) => statusTypeMap[s] || ''

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filterForm.value.status !== '') params.status = filterForm.value.status
    if (filterForm.value.date_range?.length === 2) {
      params.start_date = filterForm.value.date_range[0]
      params.end_date = filterForm.value.date_range[1]
    }
    if (filterForm.value.username) params.username = filterForm.value.username
    if (filterForm.value.room_no) params.room_no = filterForm.value.room_no
    if (sortField.value) {
      params.sort = sortField.value
      params.order = sortOrder.value
    }
    const res = await listAllReservations(params)
    reservations.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  page.value = 1
  loadData()
}

const handleReset = () => {
  filterForm.value = { username: '', room_no: '', date_range: [], status: '' }
  page.value = 1
  sortField.value = 'create_time'
  sortOrder.value = 'desc'
  loadData()
}

const handleSort = ({ prop, order }) => {
  sortField.value = prop || ''
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  loadData()
}

const openView = (row) => {
  currentRow.value = row
  viewDialogVisible.value = true
}

const handleCancel = (row) => {
  currentRow.value = row
  cancelForm.value = { reason: '' }
  cancelDialogVisible.value = true
}

const submitCancel = async () => {
  submitting.value = true
  try {
    await adminCancelReservation(currentRow.value.reservation_id)
    ElMessage.success('强制取消成功')
    cancelDialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

const handleRestore = async (row) => {
  await ElMessageBox.confirm('确认恢复该预订？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
  await restoreReservation(row.reservation_id)
  ElMessage.success('恢复成功')
  loadData()
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(() => {
  sortField.value = 'create_time'
  sortOrder.value = 'desc'
  loadData()
})
</script>

<style scoped>

</style>
