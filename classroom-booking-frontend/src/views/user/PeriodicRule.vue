<template>
  <div>
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">周期预订管理</span>
          <el-button type="primary" @click="openCreateDialog">新建周期规则</el-button>
        </div>
      </template>

      <el-table :data="rules" v-loading="loading" stripe border>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="rule_id" label="规则ID" width="80" align="center" />
        <el-table-column prop="classroom.room_no" label="目标教室" width="100" align="center" />
        <el-table-column label="周期星期" width="100" align="center">
          <template #default="{ row }">每周{{ weekdayText(row.weekday) }}</template>
        </el-table-column>
        <el-table-column label="固定时段" width="140" align="center">
          <template #default="{ row }">{{ row.start_time }} ~ {{ row.end_time }}</template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" show-overflow-tooltip min-width="120" />
        <el-table-column label="有效期" width="200" align="center">
          <template #default="{ row }">{{ row.start_date }} ~ {{ row.end_date }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="toggleStatus(row)">
              {{ row.status === 1 ? '停用' : '启用' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建周期规则" width="500px" align-center destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="选择教室" prop="classroom_id">
          <el-select v-model="form.classroom_id" placeholder="请选择教室" style="width: 100%">
            <el-option v-for="c in classroomOptions" :key="c.classroom_id" :label="c.room_no" :value="c.classroom_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="星期几" prop="weekday">
          <el-select v-model="form.weekday" placeholder="请选择" style="width: 100%">
            <el-option v-for="i in 7" :key="i" :label="`每周${weekdayText(i)}`" :value="i" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用途" prop="purpose">
          <el-input v-model="form.purpose" type="textarea" rows="2" maxlength="200" show-word-limit placeholder="请填写用途" />
        </el-form-item>
        <el-form-item label="生效日期" prop="start_date">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listPeriodicRules, createPeriodicRule, updateRuleStatus, deleteRule } from '@/api/reservation'
import { listClassrooms } from '@/api/classroom'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const rules = ref([])
const classroomOptions = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()
const form = ref({
  classroom_id: null,
  weekday: 1,
  start_time: '',
  end_time: '',
  purpose: '',
  start_date: '',
  end_date: ''
})
const formRules = {
  classroom_id: [{ required: true, message: '请选择教室', trigger: 'change' }],
  weekday: [{ required: true, message: '请选择星期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  purpose: [{ required: true, message: '请填写用途', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择生效日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

const weekdayText = (w) => ['', '一', '二', '三', '四', '五', '六', '日'][w]

const loadData = async () => {
  loading.value = true
  try {
    const res = await listPeriodicRules()
    rules.value = res.data
  } finally {
    loading.value = false
  }
}

const loadClassrooms = async () => {
  const res = await listClassrooms({ per_page: 100 })
  classroomOptions.value = res.data.items
}

const openCreateDialog = () => {
  form.value = { classroom_id: null, weekday: 1, start_time: '', end_time: '', purpose: '', start_date: '', end_date: '' }
  dialogVisible.value = true
}

const submitCreate = async () => {
  await formRef.value.validate()
  if (form.value.end_time <= form.value.start_time) {
    ElMessage.warning('结束时间必须晚于开始时间')
    return
  }
  if (form.value.end_date <= form.value.start_date) {
    ElMessage.warning('结束日期必须晚于开始日期')
    return
  }
  submitting.value = true
  try {
    await createPeriodicRule(form.value)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (row) => {
  const newStatus = row.status === 1 ? 0 : 1
  await updateRuleStatus(row.rule_id, newStatus)
  ElMessage.success('状态更新成功')
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确认删除该规则？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
  await deleteRule(row.rule_id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  loadClassrooms()
})
</script>

<style scoped>

</style>
