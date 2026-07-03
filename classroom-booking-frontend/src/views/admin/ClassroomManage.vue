<template>
  <div>
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">教室管理</span>
          <div>
            <el-input v-model="searchKeyword" placeholder="按教室编号搜索" clearable style="width: 200px; margin-right: 10px" @keyup.enter="loadData" />
            <el-button type="primary" @click="openCreateDialog">新增教室</el-button>
          </div>
        </div>
      </template>

      <el-table :data="classrooms" v-loading="loading" stripe border>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="room_no" label="教室编号" width="120" align="center" />
        <el-table-column prop="floor" label="楼层" width="80" align="center" />
        <el-table-column prop="capacity" label="容量" width="100" align="center" />
        <el-table-column label="投影仪" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.has_projector ? 'success' : 'info'">{{ row.has_projector ? '有' : '无' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="白板" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.has_whiteboard ? 'success' : 'info'">{{ row.has_whiteboard ? '有' : '无' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="facility_remark" label="设施备注" show-overflow-tooltip min-width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '正常' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教室' : '新增教室'" width="500px" align-center destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="教室编号" prop="room_no">
          <el-input v-model="form.room_no" placeholder="请输入教室编号" />
        </el-form-item>
        <el-form-item label="楼层" prop="floor">
          <el-input-number v-model="form.floor" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="投影仪">
          <el-switch v-model="form.has_projector" :active-value="1" :inactive-value="0" active-text="有" inactive-text="无" />
        </el-form-item>
        <el-form-item label="白板">
          <el-switch v-model="form.has_whiteboard" :active-value="1" :inactive-value="0" active-text="有" inactive-text="无" />
        </el-form-item>
        <el-form-item label="设施备注">
          <el-input v-model="form.facility_remark" type="textarea" rows="2" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listClassrooms, createClassroom, updateClassroom, deleteClassroom } from '@/api/classroom'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const classrooms = ref([])
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()
const form = ref({
  room_no: '', floor: 1, capacity: 30,
  has_projector: 0, has_whiteboard: 0,
  facility_remark: '', status: 1
})
const formRules = {
  room_no: [{ required: true, message: '请输入教室编号', trigger: 'blur' }],
  floor: [{ required: true, message: '请输入楼层', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (searchKeyword.value) params.room_no = searchKeyword.value
    const res = await listClassrooms(params)
    classrooms.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  form.value = { room_no: '', floor: 1, capacity: 30, has_projector: 0, has_whiteboard: 0, facility_remark: '', status: 1 }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.value = {
    classroom_id: row.classroom_id,
    room_no: row.room_no,
    floor: row.floor,
    capacity: row.capacity,
    has_projector: row.has_projector,
    has_whiteboard: row.has_whiteboard,
    facility_remark: row.facility_remark,
    status: row.status
  }
  dialogVisible.value = true
}

const submit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (isEdit.value) {
      const { classroom_id, ...updateData } = form.value
      await updateClassroom(classroom_id, updateData)
    } else {
      await createClassroom(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确认删除教室 ${row.room_no}？`, '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
  await deleteClassroom(row.classroom_id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>

</style>
