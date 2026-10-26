<template>
  <div class="page">
    <el-card class="card">
      <h2 class="title">注册账号</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名"><el-input v-model="form.username" size="large" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name" size="large" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" size="large" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password size="large" /></el-form-item>
        <el-button type="primary" size="large" class="w100" :loading="loading" @click="onRegister">注 册</el-button>
        <div class="links"><el-link type="primary" @click="$router.push('/login')">已有账号，去登录</el-link></div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../api'

const router = useRouter()
const form = reactive({ username: '', name: '', phone: '', password: '' })
const loading = ref(false)

async function onRegister() {
  if (!form.username || !form.password) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    await authApi.register({ ...form })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    // 已提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #43a047 0%, #1b5e20 100%); }
.card { width: 400px; padding: 8px 12px; }
.title { text-align: center; margin: 8px 0 20px; color: #2e7d32; }
.w100 { width: 100%; }
.links { display: flex; justify-content: center; margin-top: 14px; }
</style>
