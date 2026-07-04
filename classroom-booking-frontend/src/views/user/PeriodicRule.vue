<script setup>
import { ref, onMounted } from 'vue'
import { getPeriodicRules, createPeriodicRule, updatePeriodicRuleStatus, deletePeriodicRule } from '../../api/reservation'
import { getClassroomList } from '../../api/classroom'
import { ElMessage, ElMessageBox } from 'element-plus'

const rules = ref([])
const classrooms = ref([])
const loading = ref(false)

const dialogVisible = ref(false)
const form = ref({
  classroom_id: null,
  weekday: 1,
  start_time: '',
  end_time: '',
  purpose: '',
  start_date: '',
  end_date: ''
})

const weekdayMap = {
  1: '周一',
  2: '周二',
  3: '周三',
  4: '周四',
  5: '周五',
  6: '周六',
  7: '周日'
}

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await getPeriodicRules()
    rules.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchClassrooms = async () => {
  try {
    const res = await getClassroomList({ status: 1, per_page: 100 })
    classrooms.value = res.data.items
  } catch (error) {
    console.error(error)
  }
}

const openDialog = () => {
  form.value = {
    classroom_id: null,
    weekday: 1,
    start_time: '',
    end_time: '',
    purpose: '',
    start_date: '',
    end_date: ''
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    await createPeriodicRule(form.value)
    ElMessage.success('周期规则创建成功')
    dialogVisible.value = false
    fetchRules()
  } catch (error) {
    console.error(error)
  }
}

const toggleStatus = async (row) => {
  const newStatus = row.status === 1 ? 0 : 1
  try {
    await updatePeriodicRuleStatus(row.rule_id, newStatus)
    ElMessage.success('状态更新成功')
    fetchRules()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该周期规则吗？', '提示', { type: 'warning' })
    await deletePeriodicRule(row.rule_id)
    ElMessage.success('删除成功')
    fetchRules()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

onMounted(() => {
  fetchRules()
  fetchClassrooms()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>周期预订</span>
          <el-button type="primary" @click="openDialog">创建规则</el-button>
        </div>
      </template>

      <el-table :data="rules" v-loading="loading" border>
        <el-table-column prop="classroom.room_no" label="教室" width="100" />
        <el-table-column label="周期" width="80">
          <template #default="{ row }">
            每{{ weekdayMap[row.weekday] }}
          </template>
        </el-table-column>
        <el-table-column label="时段" width="150">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" />
        <el-table-column label="有效期" width="180">
          <template #default="{ row }">
            {{ row.start_date }} 至 {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="toggleStatus(row)">
              {{ row.status === 1 ? '停用' : '启用' }}
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create Dialog -->
    <el-dialog v-model="dialogVisible" title="创建周期规则" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="教室">
          <el-select v-model="form.classroom_id" placeholder="选择教室" style="width: 100%">
            <el-option
              v-for="item in classrooms"
              :key="item.classroom_id"
              :label="item.room_no"
              :value="item.classroom_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="星期">
          <el-select v-model="form.weekday" placeholder="选择星期" style="width: 100%">
            <el-option v-for="(label, key) in weekdayMap" :key="key" :label="label" :value="parseInt(key)" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker v-model="form.start_time" placeholder="开始时间" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker v-model="form.end_time" placeholder="结束时间" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用途">
          <el-input v-model="form.purpose" placeholder="填写用途" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" placeholder="开始日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date" placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
