<template>
  <div>
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">我的预订</span>
        </div>
      </template>

      <!-- 筛选区 -->
      <el-form :model="filterForm" inline style="margin-bottom: 16px">
        <el-form-item label="预订状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option label="已取消" :value="0" />
            <el-option label="待审核" :value="1" />
            <el-option label="已确认" :value="2" />
            <el-option label="已驳回" :value="3" />
            <el-option label="已完成" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="filterForm.date_range" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadData">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格区 -->
      <el-table :data="reservations" v-loading="loading" stripe border>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="classroom.room_no" label="教室" width="100" align="center" />
        <el-table-column prop="reserve_date" label="预订日期" width="120" align="center" />
        <el-table-column label="时段" width="140" align="center">
          <template #default="{ row }">{{ row.start_time }} ~ {{ row.end_time }}</template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" show-overflow-tooltip min-width="150" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" align="center">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openView(row)">查看</el-button>
            <el-button v-if="row.status === 2" link type="primary" @click="openEdit(row)">修改</el-button>
            <el-button v-if="[1,2].includes(row.status)" link type="danger" @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区 -->
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

    <!-- 修改弹窗 -->
    <el-dialog v-model="editDialogVisible" title="修改预订" width="500px" align-center destroy-on-close>
      <el-form :model="editForm" :rules="editRules" ref="editRef" label-width="100px">
        <el-form-item label="教室">
          <el-select v-model="editForm.classroom_id" style="width: 100%">
            <el-option v-for="c in classroomOptions" :key="c.classroom_id" :label="c.room_no" :value="c.classroom_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预订日期" prop="reserve_date">
          <el-date-picker v-model="editForm.reserve_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="editForm.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="editForm.end_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用途" prop="purpose">
          <el-input v-model="editForm.purpose" type="textarea" rows="3" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="editLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listMyReservations, updateReservation, cancelReservation } from '@/api/reservation'
import { listClassrooms } from '@/api/classroom'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const loading = ref(false)
const reservations = ref([])
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const filterForm = ref({ status: '', date_range: [] })
const classroomOptions = ref([])

const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)
const editLoading = ref(false)
const currentRow = ref(null)
const editRef = ref()
const editForm = ref({})
const editRules = {
  reserve_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请填写用途', trigger: 'blur' }]
}

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
    const res = await listMyReservations(params)
    reservations.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  filterForm.value = { status: '', date_range: [] }
  page.value = 1
  loadData()
}

const loadClassrooms = async () => {
  const res = await listClassrooms({ per_page: 100 })
  classroomOptions.value = res.data.items
}

const openView = (row) => {
  currentRow.value = row
  viewDialogVisible.value = true
}

const openEdit = (row) => {
  currentRow.value = row
  editForm.value = { ...row }
  editDialogVisible.value = true
}

const submitEdit = async () => {
  await editRef.value.validate()
  if (editForm.value.end_time <= editForm.value.start_time) {
    ElMessage.warning('结束时间必须晚于开始时间')
    return
  }
  editLoading.value = true
  try {
    await updateReservation(editForm.value.reservation_id, editForm.value)
    ElMessage.success('修改成功')
    editDialogVisible.value = false
    loadData()
  } finally {
    editLoading.value = false
  }
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm('确认取消该预订？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
  await cancelReservation(row.reservation_id)
  ElMessage.success('取消成功')
  loadData()
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
  loadClassrooms()
})
</script>

<style scoped>

</style>
