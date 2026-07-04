<script setup>
import { ref, onMounted } from 'vue'
import { getPendingApprovals, approveReservation } from '../../api/admin'
import { ElMessage } from 'element-plus'

const approvals = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const approveDialogVisible = ref(false)
const approveForm = ref({
  reservation_id: null,
  result: 1,
  opinion: ''
})

const fetchApprovals = async () => {
  loading.value = true
  try {
    const res = await getPendingApprovals({ page: page.value })
    approvals.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openApproveDialog = (row) => {
  approveForm.value = {
    reservation_id: row.reservation_id,
    result: 1,
    opinion: ''
  }
  approveDialogVisible.value = true
}

const submitApprove = async () => {
  try {
    await approveReservation(approveForm.value.reservation_id, {
      result: approveForm.value.result,
      opinion: approveForm.value.opinion
    })
    ElMessage.success('审批完成')
    approveDialogVisible.value = false
    fetchApprovals()
  } catch (error) {
    console.error(error)
  }
}

const handlePageChange = (val) => {
  page.value = val
  fetchApprovals()
}

const formatDateTime = (date, time) => {
  return `${date} ${time}`
}

onMounted(() => {
  fetchApprovals()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审批管理</span>
        </div>
      </template>

      <el-table :data="approvals" v-loading="loading" border>
        <el-table-column prop="reservation_id" label="ID" width="80" />
        <el-table-column prop="user.username" label="申请人" width="100" />
        <el-table-column prop="classroom.room_no" label="教室" width="100" />
        <el-table-column label="日期时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.reserve_date, row.start_time) }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openApproveDialog(row)">审批</el-button>
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

    <!-- Approve Dialog -->
    <el-dialog v-model="approveDialogVisible" title="审批预订" width="500px">
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="审批结果">
          <el-radio-group v-model="approveForm.result">
            <el-radio :label="1">通过</el-radio>
            <el-radio :label="2">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input
            v-model="approveForm.opinion"
            type="textarea"
            placeholder="请填写审批意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApprove">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>
