<script setup>
import { ref, onMounted } from 'vue'
import { getClassroomList, createClassroom, updateClassroom, deleteClassroom } from '../../api/classroom'
import { ElMessage, ElMessageBox } from 'element-plus'

const classrooms = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  room_no: '',
  floor: 1,
  capacity: 30,
  has_projector: 0,
  has_whiteboard: 0,
  facility_remark: ''
})
const editingId = ref(null)

const fetchClassrooms = async () => {
  loading.value = true
  try {
    const res = await getClassroomList({ page: page.value })
    classrooms.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  dialogTitle.value = '新增教室'
  editingId.value = null
  form.value = {
    room_no: '',
    floor: 1,
    capacity: 30,
    has_projector: 0,
    has_whiteboard: 0,
    facility_remark: ''
  }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  dialogTitle.value = '编辑教室'
  editingId.value = row.classroom_id
  form.value = { ...row }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    if (editingId.value) {
      await updateClassroom(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createClassroom(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchClassrooms()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除教室 ${row.room_no} 吗？`, '提示', { type: 'warning' })
    await deleteClassroom(row.classroom_id)
    ElMessage.success('删除成功')
    fetchClassrooms()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const handlePageChange = (val) => {
  page.value = val
  fetchClassrooms()
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
          <span>教室管理</span>
          <el-button type="primary" @click="openCreateDialog">新增教室</el-button>
        </div>
      </template>

      <el-table :data="classrooms" v-loading="loading" border>
        <el-table-column prop="room_no" label="教室编号" width="100" />
        <el-table-column prop="floor" label="楼层" width="80" />
        <el-table-column prop="capacity" label="容量" width="80" />
        <el-table-column label="设施" :formatter="formatFacility" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="教室编号">
          <el-input v-model="form.room_no" placeholder="如：101" />
        </el-form-item>
        <el-form-item label="楼层">
          <el-input-number v-model="form.floor" :min="1" />
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="form.capacity" :min="1" />
        </el-form-item>
        <el-form-item label="投影仪">
          <el-radio-group v-model="form.has_projector">
            <el-radio :label="1">有</el-radio>
            <el-radio :label="0">无</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="白板">
          <el-radio-group v-model="form.has_whiteboard">
            <el-radio :label="1">有</el-radio>
            <el-radio :label="0">无</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.facility_remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>
