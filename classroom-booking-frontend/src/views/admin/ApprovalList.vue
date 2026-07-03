<template>
  <div>
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">预订审批</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待审核" name="pending">
          <el-table :data="pendingList" v-loading="loading" stripe border>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="user.username" label="申请人" width="120" align="center" />
            <el-table-column prop="classroom.room_no" label="教室" width="100" align="center" />
            <el-table-column label="日期时段" width="180" align="center">
              <template #default="{ row }">{{ row.reserve_date }} {{ row.start_time }}~{{ row.end_time }}</template>
            </el-table-column>
            <el-table-column prop="purpose" label="用途" show-overflow-tooltip min-width="120" />
            <el-table-column prop="create_time" label="提交时间" width="160" align="center">
              <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="success" @click="openApproveDialog(row, 1)">通过</el-button>
                <el-button link type="danger" @click="openRejectDialog(row)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="pendingPage"
            v-model:page-size="perPage"
            :total="pendingTotal"
            layout="prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end"
            @current-change="loadPending"
          />
        </el-tab-pane>

        <el-tab-pane label="已通过" name="approved">
          <el-table :data="approvedList" v-loading="loading" stripe border>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="user.username" label="申请人" width="120" align="center" />
            <el-table-column prop="classroom.room_no" label="教室" width="100" align="center" />
            <el-table-column label="日期时段" width="180" align="center">
              <template #default="{ row }">{{ row.reserve_date }} {{ row.start_time }}~{{ row.end_time }}</template>
            </el-table-column>
            <el-table-column prop="purpose" label="用途" show-overflow-tooltip min-width="120" />
            <el-table-column prop="approval.approval_time" label="审批时间" width="160" align="center">
              <template #default="{ row }">{{ formatTime(row.approval?.approval_time) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openView(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="已驳回" name="rejected">
          <el-table :data="rejectedList" v-loading="loading" stripe border>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="user.username" label="申请人" width="120" align="center" />
            <el-table-column prop="classroom.room_no" label="教室" width="100" align="center" />
            <el-table-column label="日期时段" width="180" align="center">
              <template #default="{ row }">{{ row.reserve_date }} {{ row.start_time }}~{{ row.end_time }}</template>
            </el-table-column>
            <el-table-column prop="purpose" label="用途" show-overflow-tooltip min-width="120" />
            <el-table-column prop="approval.opinion" label="驳回原因" show-overflow-tooltip min-width="150" />
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openView(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 审批弹窗（通过） -->
    <el-dialog v-model="approveDialogVisible" title="审批通过" width="500px" align-center destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="申请人">{{ currentRow?.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="教室">{{ currentRow?.classroom?.room_no }}</el-descriptions-item>
        <el-descriptions-item label="时段">{{ currentRow?.reserve_date }} {{ currentRow?.start_time }} ~ {{ currentRow?.end_time }}</el-descriptions-item>
        <el-descriptions-item label="用途">{{ currentRow?.purpose }}</el-descriptions-item>
      </el-descriptions>
      <el-form style="margin-top: 16px">
        <el-form-item label="审批意见">
          <el-input v-model="approveForm.opinion" type="textarea" rows="3" placeholder="请输入审批意见（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="success" @click="submitApprove" :loading="submitting">确认通过</el-button>
      </template>
    </el-dialog>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="rejectDialogVisible" title="审批驳回" width="500px" align-center destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="申请人">{{ currentRow?.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="教室">{{ currentRow?.classroom?.room_no }}</el-descriptions-item>
        <el-descriptions-item label="时段">{{ currentRow?.reserve_date }} {{ currentRow?.start_time }} ~ {{ currentRow?.end_time }}</el-descriptions-item>
        <el-descriptions-item label="用途">{{ currentRow?.purpose }}</el-descriptions-item>
      </el-descriptions>
      <el-form :model="rejectForm" :rules="rejectRules" ref="rejectRef" style="margin-top: 16px">
        <el-form-item label="驳回原因" prop="opinion">
          <el-input v-model="rejectForm.opinion" type="textarea" rows="3" placeholder="请填写驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="submitReject" :loading="submitting">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 查看弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="预订详情" width="500px" align-center destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="预订ID">{{ currentRow?.reservation_id }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRow?.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="教室">{{ currentRow?.classroom?.room_no }}</el-descriptions-item>
        <el-descriptions-item label="日期">{{ currentRow?.reserve_date }}</el-descriptions-item>
        <el-descriptions-item label="时段">{{ currentRow?.start_time }} ~ {{ currentRow?.end_time }}</el-descriptions-item>
        <el-descriptions-item label="用途">{{ currentRow?.purpose }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small" :type="statusType(currentRow?.status)">{{ statusText(currentRow?.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审批意见" v-if="currentRow?.approval?.opinion">{{ currentRow?.approval?.opinion }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listPendingApprovals, approveReservation, listAllReservations } from '@/api/admin'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const activeTab = ref('pending')
const pendingList = ref([])
const approvedList = ref([])
const rejectedList = ref([])
const pendingPage = ref(1)
const perPage = ref(10)
const pendingTotal = ref(0)

const approveDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const currentRow = ref(null)
const submitting = ref(false)
const approveForm = ref({ opinion: '' })
const rejectRef = ref()
const rejectForm = ref({ opinion: '' })
const rejectRules = {
  opinion: [{ required: true, message: '请填写驳回原因', trigger: 'blur' }]
}

const statusMap = { 0: '已取消', 1: '待审核', 2: '已确认', 3: '已驳回', 4: '已完成' }
const statusTypeMap = { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger', 4: 'primary' }
const statusText = (s) => statusMap[s] || '未知'
const statusType = (s) => statusTypeMap[s] || ''

const loadPending = async () => {
  loading.value = true
  try {
    const res = await listPendingApprovals({ page: pendingPage.value, per_page: perPage.value })
    pendingList.value = res.data.items
    pendingTotal.value = res.data.total
  } finally {
    loading.value = false
  }
}

const loadApproved = async () => {
  loading.value = true
  try {
    const res = await listAllReservations({ page: 1, per_page: 100, status: 2 })
    approvedList.value = res.data.items
  } finally {
    loading.value = false
  }
}

const loadRejected = async () => {
  loading.value = true
  try {
    const res = await listAllReservations({ page: 1, per_page: 100, status: 3 })
    rejectedList.value = res.data.items
  } finally {
    loading.value = false
  }
}

const handleTabChange = (tab) => {
  if (tab === 'pending') loadPending()
  else if (tab === 'approved') loadApproved()
  else if (tab === 'rejected') loadRejected()
}

const openApproveDialog = (row) => {
  currentRow.value = row
  approveForm.value = { opinion: '' }
  approveDialogVisible.value = true
}

const openRejectDialog = (row) => {
  currentRow.value = row
  rejectForm.value = { opinion: '' }
  rejectDialogVisible.value = true
}

const openView = (row) => {
  currentRow.value = row
  viewDialogVisible.value = true
}

const submitApprove = async () => {
  submitting.value = true
  try {
    await approveReservation(currentRow.value.reservation_id, {
      result: 1,
      opinion: approveForm.value.opinion
    })
    ElMessage.success('审批通过')
    approveDialogVisible.value = false
    loadPending()
  } finally {
    submitting.value = false
  }
}

const submitReject = async () => {
  await rejectRef.value.validate()
  submitting.value = true
  try {
    await approveReservation(currentRow.value.reservation_id, {
      result: 2,
      opinion: rejectForm.value.opinion
    })
    ElMessage.success('已驳回')
    rejectDialogVisible.value = false
    loadPending()
  } finally {
    submitting.value = false
  }
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(() => {
  loadPending()
})
</script>

<style scoped>

</style>
